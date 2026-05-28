import json
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import ProductForm, BoardingForm
from .models import Product, Sale, SaleItem, Boarding
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


 
 
 


LOW_STOCK_LIMIT = 5




 


@login_required
def boarding(request):

    form = BoardingForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('cashier:boarding')

    boardings = Boarding.objects.all().order_by('-created_at')

    inside_boardings = boardings.filter(
        status='inside'
    )

    checked_out_boardings = boardings.filter(
        status='checked_out'
    )[:20]

    total_boarding_income = (
        Boarding.objects.filter(
            status='checked_out'
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
    )

    total_inside = inside_boardings.count()

    total_checked_out = Boarding.objects.filter(
        status='checked_out'
    ).count()

    context = {
        'active_page': 'boarding',

        'form': form,

        'inside_boardings': inside_boardings,

        'checked_out_boardings': checked_out_boardings,

        'total_boarding_income': total_boarding_income,

        'total_inside': total_inside,

        'total_checked_out': total_checked_out,
    }

    return render(request,'cashier/boarding.html',context)


@require_POST
@login_required
def boarding_checkout(request, pk):
    boarding_item = get_object_or_404(Boarding, pk=pk, status='inside')
    boarding_item.checkout()
    return redirect('cashier:boarding')


@require_POST
@login_required
def delete_boarding(request, pk):
    boarding_item = get_object_or_404(Boarding, pk=pk)
    boarding_item.delete()
    return redirect('cashier:boarding')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('cashier:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('cashier:dashboard')

        return render(request, 'cashier/login.html', {
            'error': 'اسم المستخدم أو كلمة المرور غير صحيحة'
        })

    return render(request, 'cashier/login.html')

def logout_view(request):
    logout(request)
    return redirect('cashier:login')

@login_required
def dashboard(request):
    today = timezone.localdate()
    active_products = Product.objects.filter(is_active=True)
    today_sales = Sale.objects.filter(created_at__date=today)

    context = {
        'active_page': 'dashboard',
        'today_sales_total': today_sales.aggregate(v=Sum('total'))['v'] or Decimal('0'),
        'today_profit_total': today_sales.aggregate(v=Sum('profit'))['v'] or Decimal('0'),
        'products_count': active_products.count(),
        'low_stock_count': active_products.filter(quantity__lte=LOW_STOCK_LIMIT).count(),
        'recent_sales': Sale.objects.prefetch_related('items')[:5],
        'low_stock_products': active_products.filter(quantity__lte=LOW_STOCK_LIMIT)[:5],
    }
    return render(request, 'cashier/dashboard.html', context)

@login_required
def pos(request):
    return render(request, 'cashier/pos.html', {'active_page': 'pos'})

@login_required
def products(request):
    form = ProductForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('cashier:products')

    context = {
        'active_page': 'products',
        'form': form,
        'products': Product.objects.filter(is_active=True),
    }
    return render(request, 'cashier/products.html', context)

@login_required
@require_POST
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # إذا المنتج مستخدم في فواتير قديمة، لا نحذفه فعليًا حتى لا تنكسر التقارير والفواتير.
    # نخفيه فقط من المنتجات والكاشير ونصفر كميته.
    if SaleItem.objects.filter(product=product).exists():
        product.is_active = False
        product.quantity = 0
        product.save(update_fields=['is_active', 'quantity', 'updated_at'])
    else:
        # إذا لم يُستخدم في أي فاتورة، يمكن حذفه نهائيًا بدون التأثير على البيانات القديمة.
        product.delete()

    return redirect('cashier:products')

@login_required
def reports(request):
    today = timezone.localdate()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    sales = Sale.objects.all()
    if start_date:
        sales = sales.filter(created_at__date__gte=start_date)
    if end_date:
        sales = sales.filter(created_at__date__lte=end_date)

    month_sales = Sale.objects.filter(created_at__year=today.year, created_at__month=today.month)
    top_products = (
        SaleItem.objects
        .values('product_name')
        .annotate(
            sold_qty=Sum('quantity'),
            sales_total=Sum('line_total'),
            profit_total=Sum('line_profit')
        )
        .order_by('-sold_qty')[:10]
    )

    context = {
        'active_page': 'reports',
        'monthly_sales': month_sales.aggregate(v=Sum('total'))['v'] or Decimal('0'),
        'monthly_profit': month_sales.aggregate(v=Sum('profit'))['v'] or Decimal('0'),
        'monthly_items': SaleItem.objects.filter(sale__in=month_sales).aggregate(v=Sum('quantity'))['v'] or 0,
        'sales': sales[:50],
        'top_products': top_products,
        'start_date': start_date or '',
        'end_date': end_date or '',
    }
    return render(request, 'cashier/reports.html', context)

@login_required
def products_api(request):
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    products = Product.objects.filter(is_active=True, quantity__gt=0)

    if q:
        products = products.filter(Q(name__icontains=q) | Q(barcode__icontains=q))
    if category:
        products = products.filter(category=category)

    data = [{
        'id': p.id,
        'name': p.name,
        'category': p.get_category_display(),
        'price': float(p.sale_price),
        'stock': p.quantity,
    } for p in products[:100]]
    return JsonResponse({'products': data})

@login_required
@require_POST
def complete_sale_api(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
        items = payload.get('items', [])
        discount = Decimal(str(payload.get('discount', '0') or '0'))
    except (json.JSONDecodeError, InvalidOperation, TypeError, ValueError):
        return JsonResponse({'ok': False, 'message': 'بيانات غير صحيحة'}, status=400)

    if not items:
        return JsonResponse({'ok': False, 'message': 'السلة فارغة'}, status=400)

    if discount < 0:
        return JsonResponse({'ok': False, 'message': 'قيمة الخصم غير صحيحة'}, status=400)

    try:
        with transaction.atomic():
            sale = Sale.objects.create(discount=discount)
            subtotal = Decimal('0')
            profit = Decimal('0')

            for item in items:
                product_id = item.get('id')
                qty = int(item.get('qty', 1))

                if qty <= 0:
                    return JsonResponse({'ok': False, 'message': 'كمية غير صحيحة'}, status=400)

                product = Product.objects.select_for_update().get(id=product_id, is_active=True)

                if product.quantity < qty:
                    return JsonResponse({'ok': False, 'message': f'الكمية غير كافية للمنتج: {product.name}'}, status=400)

                line_total = product.sale_price * qty
                line_profit = (product.sale_price - product.purchase_price) * qty
                subtotal += line_total
                profit += line_profit

                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    product_name=product.name,
                    quantity=qty,
                    unit_price=product.sale_price,
                    unit_cost=product.purchase_price,
                    line_total=line_total,
                    line_profit=line_profit,
                )

                product.quantity -= qty
                product.save(update_fields=['quantity', 'updated_at'])

            if discount > subtotal:
                return JsonResponse({'ok': False, 'message': 'الخصم أكبر من قيمة الفاتورة'}, status=400)

            sale.subtotal = subtotal
            sale.total = subtotal - discount
            sale.profit = profit - discount
            sale.save(update_fields=['subtotal', 'total', 'profit'])

    except Product.DoesNotExist:
        return JsonResponse({'ok': False, 'message': 'يوجد منتج غير متاح أو محذوف من السلة'}, status=400)
    except (TypeError, ValueError):
        return JsonResponse({'ok': False, 'message': 'بيانات المنتج أو الكمية غير صحيحة'}, status=400)

    return JsonResponse({'ok': True, 'message': 'تم إتمام البيع بنجاح', 'sale_id': sale.id, 'total': float(sale.total)})

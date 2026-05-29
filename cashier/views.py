import json
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .forms import ProductForm, BoardingForm, ClinicForm
from .models import Product, Sale, SaleItem, Boarding, Clinic, ClinicStaff

from django.contrib.auth.models import User
from django.contrib import messages
 


LOW_STOCK_LIMIT = 5


def is_clinic_owner(user):
    if hasattr(user, 'staff_profile'):
        return user.staff_profile.is_owner

    if hasattr(user, 'clinic'):
        return True

    return False

@login_required
def staff_list(request):
    clinic = get_user_clinic(request.user)

    if not is_clinic_owner(request.user):
        return redirect('cashier:dashboard')

    staff_members = ClinicStaff.objects.filter(
        clinic=clinic
    ).select_related('user')

    return render(request, 'cashier/staff_list.html', {
        'active_page': 'staff',
        'staff_members': staff_members,
    })
    
@login_required
def staff_create(request):
    clinic = get_user_clinic(request.user)

    if not is_clinic_owner(request.user):
        return redirect('cashier:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        full_name = request.POST.get('full_name', '').strip()

        if not username or not password:
            messages.error(request, 'اسم المستخدم وكلمة المرور مطلوبين')
            return redirect('cashier:staff_create')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'اسم المستخدم موجود مسبقًا')
            return redirect('cashier:staff_create')

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=full_name
        )

        ClinicStaff.objects.create(
            clinic=clinic,
            user=user,
            is_owner=False
        )

        messages.success(request, 'تم إنشاء حساب الموظف بنجاح')
        return redirect('cashier:staff_list')

    return render(request, 'cashier/staff_create.html', {
        'active_page': 'staff',
    })
    

@login_required
def staff_change_password(request, pk):
    clinic = get_user_clinic(request.user)

    if not is_clinic_owner(request.user):
        return redirect('cashier:dashboard')

    staff = get_object_or_404(
        ClinicStaff,
        pk=pk,
        clinic=clinic
    )

    if request.method == 'POST':
        password = request.POST.get('password', '').strip()

        if not password:
            messages.error(request, 'كلمة المرور مطلوبة')
            return redirect('cashier:staff_change_password', pk=staff.id)

        staff.user.set_password(password)
        staff.user.save()

        messages.success(request, 'تم تغيير كلمة المرور بنجاح')
        return redirect('cashier:staff_list')

    return render(request, 'cashier/staff_change_password.html', {
        'active_page': 'staff',
        'staff': staff,
    })
    
    
    
    
    
    
    
    
    
    
    

@login_required
def clinic_settings(request):
    clinic = get_user_clinic(request.user)

    form = ClinicForm(request.POST or None, instance=clinic)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('cashier:clinic_settings')

    return render(request, 'cashier/clinic_settings.html', {
        'active_page': 'clinic_settings',
        'clinic': clinic,
        'form': form,
    })

def get_user_clinic(user):
    clinic, created = Clinic.objects.get_or_create(
        owner=user,
        defaults={'name': 'عيادتي البيطرية'}
    )
    return clinic


def login_view(request):

    if request.method == 'GET' and request.user.is_authenticated:
        logout(request)

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
            get_user_clinic(user)
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
    clinic = get_user_clinic(request.user)
    today = timezone.localdate()

    active_products = Product.objects.filter(
        clinic=clinic,
        is_active=True
    )

    today_sales = Sale.objects.filter(
        clinic=clinic,
        created_at__date=today
    )

    boarding_today_profit = (
        Boarding.objects.filter(
            clinic=clinic,
            status='checked_out',
            check_out__date=today
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    )

    inside_boarding_count = Boarding.objects.filter(
        clinic=clinic,
        status='inside'
    ).count()

    context = {
        'active_page': 'dashboard',
        'clinic': clinic,

        'today_sales_total': today_sales.aggregate(v=Sum('total'))['v'] or Decimal('0'),
        'today_profit_total': today_sales.aggregate(v=Sum('profit'))['v'] or Decimal('0'),

        'boarding_today_profit': boarding_today_profit,
        'inside_boarding_count': inside_boarding_count,

        'products_count': active_products.count(),
        'low_stock_count': active_products.filter(quantity__lte=LOW_STOCK_LIMIT).count(),

        'recent_sales': Sale.objects.filter(clinic=clinic).prefetch_related('items')[:5],
        'low_stock_products': active_products.filter(quantity__lte=LOW_STOCK_LIMIT)[:5],
    }

    return render(request, 'cashier/dashboard.html', context)


@login_required
def pos(request):
    clinic = get_user_clinic(request.user)

    return render(request, 'cashier/pos.html', {
        'active_page': 'pos',
        'clinic': clinic,
    })


@login_required
def products(request):
    clinic = get_user_clinic(request.user)

    form = ProductForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        product = form.save(commit=False)
        product.clinic = clinic
        product.save()
        return redirect('cashier:products')

    context = {
        'active_page': 'products',
        'clinic': clinic,
        'form': form,
        'products': Product.objects.filter(
            clinic=clinic,
            is_active=True
        ),
    }

    return render(request, 'cashier/products.html', context)


@login_required
@require_POST
def delete_product(request, pk):
    clinic = get_user_clinic(request.user)

    product = get_object_or_404(
        Product,
        pk=pk,
        clinic=clinic
    )

    if SaleItem.objects.filter(product=product).exists():
        product.is_active = False
        product.quantity = 0
        product.save(update_fields=['is_active', 'quantity', 'updated_at'])
    else:
        product.delete()

    return redirect('cashier:products')


@login_required
def reports(request):
    clinic = get_user_clinic(request.user)

    today = timezone.localdate()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    sales = Sale.objects.filter(clinic=clinic)

    if start_date:
        sales = sales.filter(created_at__date__gte=start_date)

    if end_date:
        sales = sales.filter(created_at__date__lte=end_date)

    month_sales = Sale.objects.filter(
        clinic=clinic,
        created_at__year=today.year,
        created_at__month=today.month
    )

    top_products = (
        SaleItem.objects
        .filter(sale__clinic=clinic)
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
        'clinic': clinic,

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
def boarding(request):
    clinic = get_user_clinic(request.user)

    form = BoardingForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        boarding_item = form.save(commit=False)
        boarding_item.clinic = clinic
        boarding_item.save()
        return redirect('cashier:boarding')

    boardings = Boarding.objects.filter(
        clinic=clinic
    ).order_by('-created_at')

    inside_boardings = boardings.filter(status='inside')
    checked_out_boardings = boardings.filter(status='checked_out')[:20]

    total_boarding_income = (
        Boarding.objects.filter(
            clinic=clinic,
            status='checked_out'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    )

    context = {
        'active_page': 'boarding',
        'clinic': clinic,

        'form': form,
        'inside_boardings': inside_boardings,
        'checked_out_boardings': checked_out_boardings,

        'total_boarding_income': total_boarding_income,
        'total_inside': inside_boardings.count(),
        'total_checked_out': boardings.filter(status='checked_out').count(),
    }

    return render(request, 'cashier/boarding.html', context)


@require_POST
@login_required
def boarding_checkout(request, pk):
    clinic = get_user_clinic(request.user)

    boarding_item = get_object_or_404(
        Boarding,
        pk=pk,
        clinic=clinic,
        status='inside'
    )

    boarding_item.checkout()
    return redirect('cashier:boarding')


@require_POST
@login_required
def delete_boarding(request, pk):
    clinic = get_user_clinic(request.user)

    boarding_item = get_object_or_404(
        Boarding,
        pk=pk,
        clinic=clinic
    )

    boarding_item.delete()
    return redirect('cashier:boarding')


@login_required
def products_api(request):
    clinic = get_user_clinic(request.user)

    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    products = Product.objects.filter(
        clinic=clinic,
        is_active=True,
        quantity__gt=0
    )

    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(barcode__icontains=q)
        )

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
    clinic = get_user_clinic(request.user)

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
            sale = Sale.objects.create(
                clinic=clinic,
                discount=discount
            )

            subtotal = Decimal('0')
            profit = Decimal('0')

            for item in items:
                product_id = item.get('id')
                qty = int(item.get('qty', 1))

                if qty <= 0:
                    return JsonResponse({'ok': False, 'message': 'كمية غير صحيحة'}, status=400)

                product = Product.objects.select_for_update().get(
                    id=product_id,
                    clinic=clinic,
                    is_active=True
                )

                if product.quantity < qty:
                    return JsonResponse({
                        'ok': False,
                        'message': f'الكمية غير كافية للمنتج: {product.name}'
                    }, status=400)

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

    return JsonResponse({
        'ok': True,
        'message': 'تم إتمام البيع بنجاح',
        'sale_id': sale.id,
        'total': float(sale.total)
    })
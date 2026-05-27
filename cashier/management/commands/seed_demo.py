from django.core.management.base import BaseCommand
from cashier.models import Product


class Command(BaseCommand):
    help = 'إضافة منتجات تجريبية للنظام'

    def handle(self, *args, **options):
        products = [
            {'name': 'شامبو قطط', 'category': 'care', 'barcode': '10001', 'purchase_price': 2.00, 'sale_price': 3.50, 'quantity': 20},
            {'name': 'طعام كلاب 2KG', 'category': 'food', 'barcode': '10002', 'purchase_price': 5.50, 'sale_price': 8.00, 'quantity': 14},
            {'name': 'خدمة مطعوم', 'category': 'service', 'barcode': '10003', 'purchase_price': 0.00, 'sale_price': 12.00, 'quantity': 99},
            {'name': 'بخاخ براغيث', 'category': 'medicine', 'barcode': '10004', 'purchase_price': 3.50, 'sale_price': 5.25, 'quantity': 8},
        ]
        for item in products:
            Product.objects.update_or_create(barcode=item['barcode'], defaults=item)
        self.stdout.write(self.style.SUCCESS('تمت إضافة المنتجات التجريبية بنجاح'))

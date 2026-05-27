from decimal import Decimal
from django.db import models
from django.utils import timezone


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'طعام'),
        ('medicine', 'أدوية'),
        ('care', 'عناية'),
        ('service', 'خدمة'),
        ('other', 'أخرى'),
    ]
    is_active = models.BooleanField(default=True)
    
    name = models.CharField('اسم المنتج', max_length=200)
    category = models.CharField('التصنيف', max_length=30, choices=CATEGORY_CHOICES, default='other')
    barcode = models.CharField('الباركود', max_length=100, blank=True, null=True, unique=True)
    purchase_price = models.DecimalField('سعر الشراء', max_digits=10, decimal_places=2, default=0)
    sale_price = models.DecimalField('سعر البيع', max_digits=10, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField('الكمية', default=0)
    expiry_date = models.DateField('تاريخ الانتهاء', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'منتج'
        verbose_name_plural = 'المنتجات'

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        return self.quantity <= 5


class Sale(models.Model):
    created_at = models.DateTimeField('تاريخ البيع', default=timezone.now)
    subtotal = models.DecimalField('المجموع الفرعي', max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField('الخصم', max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField('الإجمالي', max_digits=10, decimal_places=2, default=0)
    profit = models.DecimalField('الربح', max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'فاتورة'
        verbose_name_plural = 'الفواتير'

    def __str__(self):
        return f'فاتورة #{self.id}'


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    line_profit = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'عنصر فاتورة'
        verbose_name_plural = 'عناصر الفواتير'

    def save(self, *args, **kwargs):
        self.line_total = Decimal(self.quantity) * self.unit_price
        self.line_profit = Decimal(self.quantity) * (self.unit_price - self.unit_cost)
        super().save(*args, **kwargs)

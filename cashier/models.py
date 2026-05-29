from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

from django.contrib.auth.models import User

 
 


 
class Clinic(models.Model):

    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='clinic'
    )

    name = models.CharField(
        max_length=200,
        default='عيادتي البيطرية'
    )

 
    phone = models.CharField(
        max_length=100,
        blank=True
    )

    address = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class ClinicStaff(models.Model):
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='staff_members'
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='staff_profile'
    )

    is_owner = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
 



class Product(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'طعام'),
        ('medicine', 'أدوية'),
        ('care', 'عناية'),
        ('service', 'خدمة'),
        ('other', 'أخرى'),
    ]
    is_active = models.BooleanField(default=True)
    clinic = models.ForeignKey('Clinic', on_delete=models.CASCADE,related_name='products', null=True,blank=True)
    
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
    
    clinic = models.ForeignKey('Clinic',on_delete=models.CASCADE, related_name='sales', null=True,blank=True)
    
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


class Boarding(models.Model):
    
    clinic = models.ForeignKey('Clinic',on_delete=models.CASCADE,related_name='boardings',null=True,blank=True)
    
    PET_TYPES = (
        ('cat', 'قط'),
        ('dog', 'كلب'),
    )

    TREATMENT_TYPES = (
        ('with_treatment', 'مع علاج'),
        ('without_treatment', 'بدون علاج'),
    )

    STATUS_TYPES = (
        ('inside', 'داخل العيادة'),
        ('checked_out', 'تم الخروج'),
    )

    owner_name = models.CharField(max_length=200, verbose_name='اسم صاحب الحيوان')
    phone = models.CharField(max_length=100, verbose_name='رقم الهاتف')

    pet_name = models.CharField(max_length=200, verbose_name='اسم الحيوان')
    pet_type = models.CharField(max_length=30, choices=PET_TYPES, verbose_name='نوع الحيوان')

    treatment_type = models.CharField(
        max_length=30,
        choices=TREATMENT_TYPES,
        default='without_treatment',
        verbose_name='العلاج'
    )

    check_in = models.DateTimeField(default=timezone.now, verbose_name='وقت الدخول')
    check_out = models.DateTimeField(blank=True, null=True, verbose_name='وقت الخروج')

    daily_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='سعر المبيت اليومي'
    )

    treatment_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='سعر العلاج'
    )

    total_days = models.PositiveIntegerField(default=1, verbose_name='عدد الأيام')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='المبلغ النهائي')

    status = models.CharField(max_length=30, choices=STATUS_TYPES, default='inside', verbose_name='الحالة')
    notes = models.TextField(blank=True, verbose_name='ملاحظات')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_days(self):
        end_time = self.check_out or timezone.now()
        diff = end_time - self.check_in

        days = diff.days
        seconds = diff.seconds

        if days <= 0:
            return 1

        if seconds > 0:
            days += 1

        return max(days, 1)

    def calculate_total(self):
        days = self.calculate_days()
        total = Decimal(days) * self.daily_price

        if self.treatment_type == 'with_treatment':
            total += self.treatment_price

        return days, total

    def checkout(self):
        self.check_out = timezone.now()
        self.status = 'checked_out'
        self.total_days, self.total_amount = self.calculate_total()
        self.save()

    def save(self, *args, **kwargs):
        self.total_days, self.total_amount = self.calculate_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.pet_name} - {self.owner_name}'
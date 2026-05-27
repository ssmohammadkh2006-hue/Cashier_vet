from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='اسم المنتج')),
                ('category', models.CharField(choices=[('food', 'طعام'), ('medicine', 'أدوية'), ('care', 'عناية'), ('service', 'خدمة'), ('other', 'أخرى')], default='other', max_length=30, verbose_name='التصنيف')),
                ('barcode', models.CharField(blank=True, max_length=100, null=True, unique=True, verbose_name='الباركود')),
                ('purchase_price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='سعر الشراء')),
                ('sale_price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='سعر البيع')),
                ('quantity', models.PositiveIntegerField(default=0, verbose_name='الكمية')),
                ('expiry_date', models.DateField(blank=True, null=True, verbose_name='تاريخ الانتهاء')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name': 'منتج', 'verbose_name_plural': 'المنتجات', 'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='تاريخ البيع')),
                ('subtotal', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='المجموع الفرعي')),
                ('discount', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='الخصم')),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='الإجمالي')),
                ('profit', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='الربح')),
            ],
            options={'verbose_name': 'فاتورة', 'verbose_name_plural': 'الفواتير', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='SaleItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=200)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('unit_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('line_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('line_profit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cashier.product')),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='cashier.sale')),
            ],
            options={'verbose_name': 'عنصر فاتورة', 'verbose_name_plural': 'عناصر الفواتير'},
        ),
    ]

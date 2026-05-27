from django.contrib import admin
from .models import Product, Sale, SaleItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'barcode', 'purchase_price', 'sale_price', 'quantity', 'expiry_date')
    search_fields = ('name', 'barcode')
    list_filter = ('category',)


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ('product_name', 'quantity', 'unit_price', 'unit_cost', 'line_total', 'line_profit')


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'total', 'profit', 'discount')
    date_hierarchy = 'created_at'
    inlines = [SaleItemInline]

from django.contrib import admin

from .models import Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    readonly_fields = ('line_total',)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'created_by', 'total_amount', 'created_at')
    list_filter = ('created_at', 'created_by')
    search_fields = ('customer_name', 'created_by__email')
    inlines = [SaleItemInline]
    readonly_fields = ('created_at', 'updated_at', 'total_amount')


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product', 'quantity', 'unit_price', 'line_total')
    list_filter = ('product', 'sale')
    search_fields = ('product__name', 'sale__customer_name')
    readonly_fields = ('created_at', 'line_total')

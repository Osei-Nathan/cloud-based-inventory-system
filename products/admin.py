from django.contrib import admin
from .models import Category, Supplier, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category Admin"""
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Category Info', {'fields': ('name', 'description')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Supplier Admin"""
    list_display = ('name', 'email', 'phone', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'phone', 'contact_info')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Supplier Info', {'fields': ('name', 'contact_info', 'email', 'phone', 'address')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Product Admin - Core inventory management"""
    list_display = ('sku', 'name', 'category', 'supplier', 'unit_price', 'stock_quantity', 'get_stock_status', 'created_at')
    list_filter = ('category', 'supplier', 'created_at')
    search_fields = ('name', 'sku', 'description')
    ordering = ('sku',)
    readonly_fields = ('created_at', 'updated_at', 'get_stock_status')
    
    fieldsets = (
        ('Product Info', {'fields': ('name', 'sku', 'description', 'category', 'supplier')}),
        ('Pricing & Stock', {
            'fields': ('unit_price', 'stock_quantity', 'low_stock_threshold', 'get_stock_status'),
            'description': 'Stock quantity can only be modified through sales transactions.'
        }),
        ('Audit', {'fields': ('created_by', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    def get_stock_status(self, obj):
        """Display color-coded stock status"""
        status = obj.get_stock_status()
        colors = {
            'OUT_OF_STOCK': 'red',
            'LOW_STOCK': 'orange',
            'IN_STOCK': 'green'
        }
        color = colors.get(status, 'gray')
        return f'<span style="color: {color}; font-weight: bold;">{status}</span>'
    
    get_stock_status.short_description = 'Stock Status'
    get_stock_status.allow_tags = True

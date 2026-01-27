from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import CustomUser

class Category(models.Model):
    """Product categories for organizing inventory"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name


class Supplier(models.Model):
    """Product suppliers/vendors"""
    name = models.CharField(max_length=255, unique=True)
    contact_info = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Product Model - Core inventory item.
    
    BUSINESS RULE: Stock quantity should only be modified through sales transactions.
    Direct stock editing is prohibited to maintain data integrity.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='products')
    sku = models.CharField(max_length=100, unique=True)
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    stock_quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    low_stock_threshold = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='products_created')
    
    class Meta:
        ordering = ['name']
        unique_together = ('sku',)
    
    def __str__(self):
        return f"{self.name} (SKU: {self.sku})"
    
    @property
    def is_low_stock(self):
        """Check if product is below low stock threshold"""
        return self.stock_quantity <= self.low_stock_threshold
    
    def get_stock_status(self):
        """Return human-readable stock status"""
        if self.stock_quantity == 0:
            return "OUT_OF_STOCK"
        elif self.is_low_stock:
            return "LOW_STOCK"
        return "IN_STOCK"
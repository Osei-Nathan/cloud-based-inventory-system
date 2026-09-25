from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from accounts.models import CustomUser
from products.models import Product


class Sale(models.Model):
    """Represents a completed sale transaction."""
    customer_name = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='sales_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Sale #{self.pk} - {self.customer_name}"

    def recalculate_total(self):
        self.total_amount = sum(item.line_total for item in self.items.all())
        self.save(update_fields=['total_amount'])


class SaleItem(models.Model):
    """Represents an individual item in a sale."""
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sale_items')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    @property
    def line_total(self):
        return self.quantity * self.unit_price

    def clean(self):
        super().clean()
        if self.quantity <= 0:
            raise ValidationError({'quantity': 'Quantity must be greater than zero.'})
        if self.product.stock_quantity < self.quantity:
            raise ValidationError(
                {'quantity': f'Not enough stock for {self.product.name}. Available: {self.product.stock_quantity}'}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.product.stock_quantity -= self.quantity
        self.product.save(update_fields=['stock_quantity'])
        self.sale.recalculate_total()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

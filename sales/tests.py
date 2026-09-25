from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from products.models import Category, Supplier, Product
from sales.models import Sale, SaleItem


class SalesDomainTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.staff = self.User.objects.create_user(
            email='staff@example.com',
            full_name='Staff User',
            password='Password123',
            role='STAFF',
        )
        self.admin = self.User.objects.create_user(
            email='admin@example.com',
            full_name='Admin User',
            password='Password123',
            role='ADMIN',
        )
        self.category = Category.objects.create(name='Electronics', description='Devices')
        self.supplier = Supplier.objects.create(name='Tech Supplier', email='supplier@example.com')
        self.product = Product.objects.create(
            name='Laptop',
            sku='SKU-001',
            category=self.category,
            supplier=self.supplier,
            unit_price=Decimal('1200.00'),
            stock_quantity=10,
            low_stock_threshold=3,
            created_by=self.admin,
        )

    def test_sale_item_reduces_stock_and_recalculates_total(self):
        sale = Sale.objects.create(customer_name='Jane Doe', created_by=self.staff)
        item = SaleItem.objects.create(
            sale=sale,
            product=self.product,
            quantity=3,
            unit_price=Decimal('1200.00'),
        )

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 7)
        sale.refresh_from_db()
        self.assertEqual(sale.total_amount, Decimal('3600.00'))
        self.assertEqual(item.line_total, Decimal('3600.00'))

    def test_sale_item_rejects_insufficient_stock(self):
        sale = Sale.objects.create(customer_name='Jane Doe', created_by=self.staff)
        item = SaleItem(sale=sale, product=self.product, quantity=999, unit_price=Decimal('10.00'))

        with self.assertRaises(ValidationError):
            item.full_clean()


class SalesAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.User = get_user_model()
        self.staff = self.User.objects.create_user(
            email='staff-api@example.com',
            full_name='Staff API',
            password='Password123',
            role='STAFF',
        )
        self.category = Category.objects.create(name='Office', description='Office goods')
        self.supplier = Supplier.objects.create(name='Office Supplier', email='office@example.com')
        self.product = Product.objects.create(
            name='Monitor',
            sku='SKU-API-001',
            category=self.category,
            supplier=self.supplier,
            unit_price=Decimal('250.00'),
            stock_quantity=6,
            low_stock_threshold=2,
            created_by=self.staff,
        )

    def test_staff_can_create_sale_with_items(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.post(
            '/api/sales/sales/',
            {
                'customer_name': 'Alpha Retail',
                'items': [
                    {
                        'product': self.product.id,
                        'quantity': 2,
                        'unit_price': '250.00',
                    }
                ],
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['total_amount'], '500.00')
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 4)

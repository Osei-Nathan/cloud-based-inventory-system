from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from products.models import Category, Product, Supplier
from sales.models import Sale, SaleItem


class AnalyticsAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email='viewer@example.com',
            full_name='Viewer User',
            password='Password123',
            role='VIEWER',
        )
        self.category = Category.objects.create(name='Accessories', description='Accessories')
        self.supplier = Supplier.objects.create(name='Accessory Supplier', email='accessories@example.com')
        self.product_a = Product.objects.create(
            name='Mouse',
            sku='ACC-001',
            category=self.category,
            supplier=self.supplier,
            unit_price=Decimal('30.00'),
            stock_quantity=20,
            low_stock_threshold=2,
            created_by=self.user,
        )
        self.product_b = Product.objects.create(
            name='Keyboard',
            sku='ACC-002',
            category=self.category,
            supplier=self.supplier,
            unit_price=Decimal('75.00'),
            stock_quantity=12,
            low_stock_threshold=2,
            created_by=self.user,
        )

        self.sale_1 = Sale.objects.create(customer_name='Customer A', created_by=self.user)
        SaleItem.objects.create(sale=self.sale_1, product=self.product_a, quantity=2, unit_price=Decimal('30.00'))
        SaleItem.objects.create(sale=self.sale_1, product=self.product_b, quantity=1, unit_price=Decimal('75.00'))

        self.sale_2 = Sale.objects.create(customer_name='Customer B', created_by=self.user)
        SaleItem.objects.create(sale=self.sale_2, product=self.product_a, quantity=3, unit_price=Decimal('30.00'))

    def test_sales_summary_api(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/analytics/sales-summary/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_sales'], 2)
        self.assertEqual(response.data['total_revenue'], '225.00')
        self.assertEqual(response.data['average_order_value'], '112.50')

    def test_top_products_api(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/analytics/top-products/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data[0]['product_name'], 'Mouse')
        self.assertEqual(response.data[0]['total_quantity_sold'], 5)

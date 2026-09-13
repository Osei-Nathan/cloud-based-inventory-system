from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Category, Supplier, Product
from .serializers import CategorySerializer, SupplierSerializer, ProductSerializer
from accounts.permissions import IsAdminUserRole, IsStaffUserRole, IsViewerOrReadOnly


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Product Categories
    
    - GET /api/products/categories/ - List all categories (all authenticated)
    - POST /api/products/categories/ - Create category (ADMIN only)
    - GET /api/products/categories/{id}/ - Get category details (all authenticated)
    - PATCH /api/products/categories/{id}/ - Update category (ADMIN only)
    - DELETE /api/products/categories/{id}/ - Delete category (ADMIN only)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """Enforce ADMIN-only for create/update/delete"""
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsAuthenticated, IsAdminUserRole]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class SupplierViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Suppliers
    
    - GET /api/products/suppliers/ - List all suppliers (all authenticated)
    - POST /api/products/suppliers/ - Create supplier (ADMIN only)
    - GET /api/products/suppliers/{id}/ - Get supplier details (all authenticated)
    - PATCH /api/products/suppliers/{id}/ - Update supplier (ADMIN only)
    - DELETE /api/products/suppliers/{id}/ - Delete supplier (ADMIN only)
    """
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'email', 'phone', 'contact_info']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """Enforce ADMIN-only for create/update/delete"""
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsAuthenticated, IsAdminUserRole]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Products
    
    - GET /api/products/products/ - List all products (paginated, searchable) (all authenticated)
    - POST /api/products/products/ - Create product (ADMIN only)
    - GET /api/products/products/{id}/ - Get product details (all authenticated)
    - PATCH /api/products/products/{id}/ - Update product (ADMIN only)
    - DELETE /api/products/products/{id}/ - Delete product (ADMIN only)
    
    Filtering:
    - ?category={id} - Filter by category
    - ?supplier={id} - Filter by supplier
    - ?search={name} - Search by name or SKU
    """
    queryset = Product.objects.select_related('category', 'supplier', 'created_by')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'supplier']
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'unit_price', 'stock_quantity', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """Enforce ADMIN-only for create/update/delete"""
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsAuthenticated, IsAdminUserRole]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products below low stock threshold"""
        products = Product.objects.filter(stock_quantity__lte=self.queryset.model._meta.get_field('low_stock_threshold').default)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """Get out of stock products"""
        products = Product.objects.filter(stock_quantity=0)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
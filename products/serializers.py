from rest_framework import serializers
from .models import Category, Supplier, Product


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Product Categories"""
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'created_at')
        read_only_fields = ('id', 'created_at')


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Suppliers"""
    class Meta:
        model = Supplier
        fields = ('id', 'name', 'contact_info', 'email', 'phone', 'address', 'created_at')
        read_only_fields = ('id', 'created_at')


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Products with nested relationships"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    stock_status = serializers.CharField(source='get_stock_status', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'description', 'sku', 'category', 'category_name',
            'supplier', 'supplier_name', 'unit_price', 'stock_quantity',
            'low_stock_threshold', 'is_low_stock', 'stock_status',
            'created_by', 'created_by_email', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'created_by', 'created_by_email', 'created_at', 
            'updated_at', 'stock_status', 'is_low_stock', 'category_name',
            'supplier_name', 'stock_quantity'  # Stock only changes via sales
        )
    
    def validate_low_stock_threshold(self, value):
        if value < 0:
            raise serializers.ValidationError("Low stock threshold cannot be negative.")
        return value
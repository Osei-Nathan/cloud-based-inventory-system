from rest_framework import serializers

from .models import Sale, SaleItem


class SaleItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = SaleItem
        fields = ['id', 'product', 'quantity', 'unit_price', 'line_total', 'created_at']
        read_only_fields = ['id', 'created_at', 'line_total']

    def validate(self, attrs):
        product = attrs.get('product')
        quantity = attrs.get('quantity')
        if product and quantity is not None:
            if quantity <= 0:
                raise serializers.ValidationError({'quantity': 'Quantity must be greater than zero.'})
            if product.stock_quantity < quantity:
                raise serializers.ValidationError({
                    'quantity': f'Not enough stock for {product.name}. Available: {product.stock_quantity}'
                })
        return attrs


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)

    class Meta:
        model = Sale
        fields = ['id', 'customer_name', 'created_by', 'total_amount', 'created_at', 'updated_at', 'items']
        read_only_fields = ['id', 'created_by', 'total_amount', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        sale = Sale.objects.create(**validated_data)

        for item_data in items_data:
            SaleItem.objects.create(sale=sale, **item_data)

        sale.recalculate_total()
        return sale

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance.customer_name = validated_data.get('customer_name', instance.customer_name)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                SaleItem.objects.create(sale=instance, **item_data)
            instance.recalculate_total()

        return instance

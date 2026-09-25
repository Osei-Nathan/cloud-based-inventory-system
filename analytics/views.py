from decimal import Decimal

from django.db.models import F, Sum
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sales.models import Sale, SaleItem


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sales_summary(request):
    sales = Sale.objects.prefetch_related('items')
    total_sales = sales.count()
    total_revenue = sum(
        (item.line_total for sale in sales for item in sale.items.all()),
        Decimal('0.00'),
    )
    average_order_value = (total_revenue / total_sales) if total_sales else Decimal('0.00')

    return Response({
        'total_sales': total_sales,
        'total_revenue': str(total_revenue.quantize(Decimal('0.01'))),
        'average_order_value': str(average_order_value.quantize(Decimal('0.01'))),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_products(request):
    top_products_qs = (
        SaleItem.objects.values('product_id', 'product__name')
        .annotate(
            total_quantity_sold=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('unit_price')),
        )
        .order_by('-total_quantity_sold', 'product__name')
    )

    data = []
    for item in top_products_qs:
        data.append({
            'product_id': item['product_id'],
            'product_name': item['product__name'],
            'total_quantity_sold': item['total_quantity_sold'],
            'total_revenue': str((item['total_revenue'] or Decimal('0.00')).quantize(Decimal('0.01'))),
        })

    return Response(data)

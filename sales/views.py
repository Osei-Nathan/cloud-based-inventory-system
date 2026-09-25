from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsStaffUserRole
from .models import Sale, SaleItem
from .serializers import SaleSerializer, SaleItemSerializer


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.select_related('created_by').prefetch_related('items__product')
    serializer_class = SaleSerializer

    def get_permissions(self):
        if self.request.method in ['POST', 'PATCH', 'PUT', 'DELETE']:
            return [IsAuthenticated(), IsStaffUserRole()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SaleItemViewSet(viewsets.ModelViewSet):
    queryset = SaleItem.objects.select_related('sale', 'product')
    serializer_class = SaleItemSerializer

    def get_permissions(self):
        if self.request.method in ['POST', 'PATCH', 'PUT', 'DELETE']:
            return [IsAuthenticated(), IsStaffUserRole()]
        return [IsAuthenticated()]

from django.urls import path

from .views import sales_summary, top_products

app_name = 'analytics'

urlpatterns = [
    path('sales-summary/', sales_summary, name='sales-summary'),
    path('top-products/', top_products, name='top-products'),
]

from rest_framework import viewsets
from .models import Product, Category, Brand
from .serializers import ProductSerializer, CategorySerializer, BrandSerializer

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing products.
    """
    queryset = Product.objects.filter(available=True)
    serializer_class = ProductSerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing brands.
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = 'slug'

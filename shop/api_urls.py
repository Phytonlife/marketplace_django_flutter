from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api

app_name = 'shop_api'

router = DefaultRouter()
router.register(r'products', api.ProductViewSet, basename='product')
router.register(r'categories', api.CategoryViewSet, basename='category')
router.register(r'brands', api.BrandViewSet, basename='brand')

urlpatterns = [
    path('', include(router.urls)),
]

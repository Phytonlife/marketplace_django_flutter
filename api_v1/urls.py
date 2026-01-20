from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    MyTokenObtainPairView,
    UserRegistrationView, UserProfileView, AddressViewSet,
    CategoryViewSet, BrandViewSet, ProductViewSet,
    ReviewViewSet, WishlistViewSet,
    CartViewSet,
    OrderViewSet
)

app_name = 'api_v1'

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')

# Nested router for reviews under products
products_router = routers.NestedDefaultRouter(router, r'products', lookup='product')
products_router.register(r'reviews', ReviewViewSet, basename='product-reviews')

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('', include(router.urls)),
    path('', include(products_router.urls)),
]
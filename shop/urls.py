from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('brand/<slug:brand_slug>/', views.product_list_by_brand, name='product_list_by_brand'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('review/<int:product_id>/', views.add_review, name='add_review'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
]
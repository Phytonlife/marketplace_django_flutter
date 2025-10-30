from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/seller/', views.seller_register, name='seller_register'),
    path('profile/', views.profile, name='profile'),
    path('address/add/', views.add_address, name='add_address'),
    path('address/delete/<int:address_id>/', views.delete_address, name='delete_address'),
]
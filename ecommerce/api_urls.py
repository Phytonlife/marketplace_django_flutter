from django.urls import path, include
from rest_framework.authtoken import views

app_name = 'api'

urlpatterns = [
    path('shop/', include('shop.api_urls')),
    path('auth-token/', views.obtain_auth_token, name='auth-token'),
]

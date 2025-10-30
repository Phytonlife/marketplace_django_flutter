from django.urls import path, include
from rest_framework.authtoken import views

app_name = 'api'

urlpatterns = [
    path('v1/', include('api_v1.urls')), # Added for API v1
    path('auth-token/', views.obtain_auth_token, name='auth-token'),
]

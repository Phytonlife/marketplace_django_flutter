from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    is_seller = models.BooleanField(default=False)

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=255, default='')
    address_line_1 = models.CharField(max_length=255, null=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.address_line_1}, {self.city}, {self.country}"
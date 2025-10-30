from django.db import models
from django.conf import settings
from shop.models import Product

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=250, default='')
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    payment_method = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        return self.total_price

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"WB-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity
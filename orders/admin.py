from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'paid', 'created']
    list_filter = ['paid', 'created']
    search_fields = ['id', 'user__email']
    inlines = [OrderItemInline]

from django import forms
from shop.models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'brand', 'name', 'slug', 'image', 'description', 'price', 'stock', 'available']

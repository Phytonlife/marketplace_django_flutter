from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'country', 'city',
                  'postal_code', 'address', 'payment_method', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
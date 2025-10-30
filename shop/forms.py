from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'advantages', 'disadvantages']
        widgets = {
            'rating': forms.RadioSelect(choices=Review.RATING_CHOICES),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ваш отзыв о товаре'}),
            'advantages': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Что вам понравилось'}),
            'disadvantages': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Что не понравилось'}),
        }
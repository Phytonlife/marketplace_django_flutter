from django import forms
from .models import User, Address


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'phone_number']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Пароли не совпадают')
        return cd['password2']


class UserLoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'profile_picture']


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ['user']
        fields = ['full_name', 'address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country', 'is_default']

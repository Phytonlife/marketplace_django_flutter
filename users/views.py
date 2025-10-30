from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, AddressForm
from .models import Address


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email'] # Set username to email
            user.set_password(form.cleaned_data['password'])
            user.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'  # Set backend
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('shop:product_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Вы успешно вошли в систему!')
                return redirect(request.GET.get('next', 'shop:product_list'))
            else:
                messages.error(request, 'Неверный email или пароль')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, 'Вы вышли из системы')
    return redirect('shop:product_list')


def seller_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password'])
            user.is_seller = True
            user.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            messages.success(request, 'Seller registration successful! Welcome to your dashboard.')
            return redirect('dashboard:home')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/seller_register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлен!')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)

    addresses = Address.objects.filter(user=request.user)
    return render(request, 'users/profile.html', {'form': form, 'addresses': addresses})


@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Адрес добавлен!')
            return redirect('users:profile')
    else:
        form = AddressForm()
    return render(request, 'users/add_address.html', {'form': form})


@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully.')
        return redirect('users:profile')
    # Redirect to profile if accessed via GET to prevent accidental deletion
    return redirect('users:profile')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from functools import wraps

from shop.models import Product
from .forms import ProductForm

# Custom decorator to check if user is a seller
def seller_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_seller:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('shop:product_list')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
@seller_required
def dashboard_home(request):
    products = Product.objects.filter(seller=request.user)
    return render(request, 'dashboard/home.html', {'products': products})

@login_required
@seller_required
def product_list(request):
    products = Product.objects.filter(seller=request.user)
    return render(request, 'dashboard/product_list.html', {'products': products})

@login_required
@seller_required
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, 'Product added successfully.')
            return redirect('dashboard:product_list')
    else:
        form = ProductForm()
    return render(request, 'dashboard/product_form.html', {'form': form, 'title': 'Add Product'})

@login_required
@seller_required
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('dashboard:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'dashboard/product_form.html', {'form': form, 'title': 'Edit Product'})

@login_required
@seller_required
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('dashboard:product_list')
    return render(request, 'dashboard/product_confirm_delete.html', {'product': product})
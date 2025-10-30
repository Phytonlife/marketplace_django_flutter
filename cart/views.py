from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from shop.models import Product
from .cart import Cart
from django.contrib import messages

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity)
    messages.success(request, f'{product.name} добавлен в корзину')
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, 'Товар удален из корзины')
    return redirect('cart:cart_detail')

@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity, override_quantity=True)
    messages.success(request, 'Cart updated')
    return redirect('cart:cart_detail')
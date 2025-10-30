from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cart.cart import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm
import uuid


@login_required
def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty')
        return redirect('shop:product_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # Store address in session and redirect to payment
            request.session['checkout_address'] = form.cleaned_data
            return redirect('orders:payment_process')
    else:
        initial_data = {}
        if hasattr(request.user, 'addresses') and request.user.addresses.filter(is_default=True).exists():
            address = request.user.addresses.filter(is_default=True).first()
            initial_data = {
                'full_name': address.full_name,
                'email': request.user.email,
                'phone': address.phone,
                'country': address.country,
                'city': address.city,
                'postal_code': address.postal_code,
                'address': address.address_line1,
            }
        form = OrderCreateForm(initial=initial_data)

    return render(request, 'orders/create.html', {'cart': cart, 'form': form})


@login_required
def payment_process(request):
    cart = Cart(request)
    address_data = request.session.get('checkout_address')

    if not address_data:
        messages.error(request, 'No address provided. Please complete the address form first.')
        return redirect('orders:order_create')

    if request.method == 'POST':
        # Simulate payment success
        order = Order.objects.create(
            user=request.user,
            full_name=address_data['full_name'],
            email=address_data['email'],
            phone=address_data['phone'],
            country=address_data['country'],
            city=address_data['city'],
            postal_code=address_data['postal_code'],
            address=address_data['address'],
            paid=True, # Simulate successful payment
            payment_method='Card (Simulated)',
            total_price=cart.get_total_price(),
        )

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity']
            )

        cart.clear()
        del request.session['checkout_address']

        messages.success(request, f'Payment successful! Your order #{order.order_number} has been created.')
        return redirect('orders:order_detail', order_id=order.id)

    return render(request, 'orders/payment.html', {'cart': cart})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/detail.html', {'order': order})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'orders/list.html', {'orders': orders})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'orders/history.html', {'orders': orders})

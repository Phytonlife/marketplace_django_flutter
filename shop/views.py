from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Product, Category, Brand, Review, Wishlist
from .forms import ReviewForm
import django_filters


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='Цена от')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='Цена до')
    brand = django_filters.ModelMultipleChoiceFilter(queryset=Brand.objects.all(), label='Бренд')

    class Meta:
        model = Product
        fields = ['brand', 'min_price', 'max_price']


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    wishlist_product_ids = []
    if request.user.is_authenticated:
        wishlist_product_ids = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Search
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Filters
    product_filter = ProductFilter(request.GET, queryset=products)
    products = product_filter.qs

    # Sorting
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('name')

    # Pagination
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'categories': categories,
        'page_obj': page_obj,
        'filter': product_filter,
        'search_query': search_query,
        'wishlist_product_ids': wishlist_product_ids,
    }
    return render(request, 'shop/product/list.html', context)


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)

    # Получаем отзывы
    reviews = product.reviews.all()

    # Похожие товары
    similar_products = Product.objects.filter(
        category=product.category,
        available=True
    ).exclude(id=product.id)[:8]

    # Проверка наличия в избранном
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    # Форма отзыва
    review_form = ReviewForm()
    user_has_reviewed = False
    if request.user.is_authenticated:
        user_has_reviewed = Review.objects.filter(user=request.user, product=product).exists()

    context = {
        'product': product,
        'reviews': reviews,
        'similar_products': similar_products,
        'in_wishlist': in_wishlist,
        'review_form': review_form,
        'user_has_reviewed': user_has_reviewed,
    }
    return render(request, 'shop/product/detail.html', context)


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if Review.objects.filter(user=request.user, product=product).exists():
        messages.warning(request, 'Вы уже оставили отзыв на этот товар')
        return redirect('shop:product_detail', id=product.id, slug=product.slug)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()

            messages.success(request, 'Спасибо за ваш отзыв!')
            return redirect('shop:product_detail', id=product.id, slug=product.slug)

    return redirect('shop:product_detail', id=product.id, slug=product.slug)


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if not created:
        wishlist_item.delete()
        messages.success(request, 'Товар удален из избранного')
    else:
        messages.success(request, 'Товар добавлен в избранное')

    return redirect(request.META.get('HTTP_REFERER', 'shop:product_list'))


@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'shop/wishlist.html', {'wishlist_items': wishlist_items})


def product_list_by_brand(request, brand_slug):
    brand = get_object_or_404(Brand, slug=brand_slug)
    products = Product.objects.filter(brand=brand, available=True)
    categories = Category.objects.all()

    # Search
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Filters
    product_filter = ProductFilter(request.GET, queryset=products)
    products = product_filter.qs

    # Sorting
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('name')

    # Pagination
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'brand': brand,
        'categories': categories,
        'page_obj': page_obj,
        'filter': product_filter,
        'search_query': search_query,
    }
    return render(request, 'shop/product/list.html', context)

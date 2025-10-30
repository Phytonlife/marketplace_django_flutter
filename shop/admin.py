from django.contrib import admin
from .models import Category, Brand, Product, Review, Wishlist

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'brand', 'price', 'stock', 'available']
    list_filter = ['available', 'category', 'brand']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating']
    list_filter = ['rating']
    search_fields = ['product__name', 'user__email']

admin.site.register(Wishlist)

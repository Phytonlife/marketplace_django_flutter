from .models import Category, Brand

def extras(request):
    categories = Category.objects.all()
    brands = Brand.objects.all()
    return {'categories': categories, 'brands': brands}

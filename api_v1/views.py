from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from users.models import User, Address
from shop.models import Product, Category, Brand, Review, Wishlist
from orders.models import Order, OrderItem # Added for Order
from .models import Cart, CartItem
from .serializers import (
    MyTokenObtainPairSerializer,
    UserSerializer, UserRegistrationSerializer, AddressSerializer,
    CategorySerializer, BrandSerializer, ProductSerializer,
    ReviewSerializer, WishlistSerializer,
    CartSerializer, CartItemSerializer,
    OrderSerializer, OrderItemSerializer # Added for Order
)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# Custom Permissions
class IsSellerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow sellers of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the seller of the product.
        return obj.seller == request.user

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "User registered successfully."
        }, status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.addresses.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# --- Shop API Views ---

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = 'slug'

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsSellerOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Allow sellers to see their unavailable products
        if self.request.user.is_authenticated and self.request.user.is_seller:
            if self.action in ['list', 'retrieve'] and self.request.query_params.get('seller_products') == 'true':
                return Product.objects.filter(seller=self.request.user)
        return queryset

    def perform_create(self, serializer):
        if not self.request.user.is_seller:
            raise permissions.PermissionDenied("Only sellers can create products.")
        serializer.save(seller=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_to_wishlist(self, request, pk=None):
        product = self.get_object()
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if created:
            return Response({'status': 'product added to wishlist'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'product already in wishlist'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def remove_from_wishlist(self, request, pk=None):
        product = self.get_object()
        Wishlist.objects.filter(user=request.user, product=product).delete()
        return Response({'status': 'product removed from wishlist'}, status=status.HTTP_204_NO_CONTENT)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        # Allow listing reviews for a specific product
        product_id = self.kwargs.get('product_pk')
        if product_id:
            return Review.objects.filter(product__id=product_id)
        return Review.objects.all() # Or raise an error if not product-specific

    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_pk')
        product = generics.get_object_or_404(Product, pk=product_id)
        if Review.objects.filter(user=self.request.user, product=product).exists():
            raise generics.ValidationError("You have already reviewed this product.")
        serializer.save(user=self.request.user, product=product)

class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        product_id = self.request.data.get('product')
        if not product_id:
            raise generics.ValidationError({"product": "This field is required."})
        product = generics.get_object_or_404(Product, pk=product_id)
        if Wishlist.objects.filter(user=self.request.user, product=product).exists():
            raise generics.ValidationError("Product already in wishlist.")
        serializer.save(user=self.request.user, product=product)

# --- Cart API Views ---

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete'] # Limit methods

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_object(self):
        # Ensure a cart exists for the user
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

    def list(self, request, *args, **kwargs):
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart = self.get_object()
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return Response({'product_id': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'product_id': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = int(quantity)
        cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'])
    def update_item(self, request):
        cart = self.get_object()
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')

        if not product_id or quantity is None:
            return Response({'detail': 'product_id and quantity are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart_item = CartItem.objects.get(cart=cart, product__id=product_id)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found in cart.'}, status=status.HTTP_404_NOT_FOUND)

        if int(quantity) <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = int(quantity)
            cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        cart = self.get_object()
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({'product_id': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart_item = CartItem.objects.get(cart=cart, product__id=product_id)
            cart_item.delete()
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found in cart.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def clear_cart(self, request):
        cart = self.get_object()
        cart.items.all().delete()
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

# --- Order API Views ---

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post'] # Only allow listing and creating orders

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        cart = generics.get_object_or_404(Cart, user=user)
        cart_items = cart.items.all()

        if not cart_items:
            raise generics.ValidationError("Your cart is empty.")

        # Get address from validated data
        address = serializer.validated_data.get('address')
        if not address:
            raise generics.ValidationError({"address_id": "Address is required to create an order."})

        # Create the order
        order = serializer.save(user=user, total_price=cart.total_price, paid=False)

        # Move cart items to order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                price=cart_item.product.price,
                quantity=cart_item.quantity
            )
        cart.items.all().delete() # Clear the cart

        return order

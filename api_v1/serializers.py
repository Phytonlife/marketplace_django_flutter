from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.models import User, Address
from shop.models import Product, Category, Brand, Review, Wishlist
from .models import Cart, CartItem
from orders.models import Order, OrderItem

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        return token

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError('Must include "email" and "password".')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('No user with this email address was found.')

        if not user.check_password(password):
            raise serializers.ValidationError('Incorrect password.')

        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')

        self.user = user
        refresh = self.get_token(self.user)

        data = {}
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'profile_picture', 'is_seller')
        read_only_fields = ('is_seller',)

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        return user

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('id', 'full_name', 'address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country', 'is_default')
        read_only_fields = ('user',)

# --- New Serializers for Shop App ---

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug']

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username') # Display username instead of user ID

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'comment', 'advantages', 'disadvantages', 'created']
        read_only_fields = ['user', 'product'] # Product will be set by the view

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True) # Nested reviews
    # Add a field to check if the product is in the user's wishlist
    is_in_wishlist = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'price',
            'stock',
            'available',
            'created',
            'updated',
            'image',
            'category',
            'brand',
            'seller',
            'reviews',
            'is_in_wishlist',
        ]
        read_only_fields = ['seller'] # Seller will be set by the view for creation/update

    def get_is_in_wishlist(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Wishlist.objects.filter(user=request.user, product=obj).exists()
        return False

class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True) # Nested product details

    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'user']
        read_only_fields = ['user'] # User will be set by the view

# --- Cart Serializers ---

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True) # Nested product details
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total_price']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'total_items']
        read_only_fields = ['user']

# --- Order Serializers ---

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True) # Nested product details

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'price', 'quantity', 'get_cost']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    address = AddressSerializer(read_only=True) # Nested address details
    address_id = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all(), source='address', write_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'total_price', 'full_name', 'email', 'phone',
            'address', 'address_id', 'postal_code', 'city', 'country', 'notes',
            'payment_method', 'created', 'paid', 'items'
        ]
        read_only_fields = ['user', 'order_number', 'total_price', 'created', 'paid']

    def create(self, validated_data):
        # This create method will be handled by the view, which will take items from the cart
        pass
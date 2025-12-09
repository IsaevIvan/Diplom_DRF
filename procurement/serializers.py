from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Contact, Order, OrderItem


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователей"""
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'company', 'position', 'type', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Сериализатор для входа пользователя"""
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Неверные учетные данные')
            if not user.is_active:
                raise serializers.ValidationError('Аккаунт не активирован')
            attrs['user'] = user
            return attrs
        raise serializers.ValidationError('Email и пароль обязательны')


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения пользователя"""

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'company', 'position', 'type']


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name', 'url', 'is_active']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category']


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ['id', 'name']


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = ParameterSerializer(read_only=True)

    class Meta:
        model = ProductParameter
        fields = ['id', 'parameter', 'value']


class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    shop = ShopSerializer(read_only=True)
    parameters = ProductParameterSerializer(many=True, read_only=True)

    class Meta:
        model = ProductInfo
        fields = ['id', 'product', 'shop', 'external_id', 'model', 'price', 'price_rrc', 'quantity', 'parameters']


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'city', 'street', 'house', 'building', 'apartment', 'phone']
        read_only_fields = ['id']


class OrderItemSerializer(serializers.ModelSerializer):
    product_info = ProductInfoSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_info', 'quantity']
        read_only_fields = ['id']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'created_at', 'contact', 'items']
        read_only_fields = ['id', 'created_at']
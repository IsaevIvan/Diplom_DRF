from django.contrib import admin
from .models import User, Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Contact, Order, OrderItem

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'type', 'is_active']
    list_filter = ['type', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    filter_horizontal = ['shops']  # для удобного выбора магазинов
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name']

@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ['product', 'shop', 'price', 'price_rrc', 'quantity']
    list_filter = ['shop']
    search_fields = ['product__name', 'shop__name']

@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ['product_info', 'parameter', 'value']
    list_filter = ['parameter']
    search_fields = ['product_info__product__name', 'parameter__name']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['user', 'city', 'street', 'house', 'phone']
    list_filter = ['city']
    search_fields = ['user__email', 'city', 'street']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_info', 'quantity']
    list_filter = ['order__status']
    search_fields = ['order__user__email', 'product_info__product__name']
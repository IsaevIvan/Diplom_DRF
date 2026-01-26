from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product, Category, ProductInfo, Shop

def clear_products_cache():
    """Очистка кэша товаров"""
    cache.delete_pattern('*.products.*')  # Удаляем все ключи с products
    cache.delete('products_list')
    print("✅ Кэш товаров очищен")

# Очищаем кэш при изменении товаров
@receiver([post_save, post_delete], sender=Product)
def clear_cache_on_product_change(sender, **kwargs):
    clear_products_cache()

# Очищаем кэш при изменении категорий
@receiver([post_save, post_delete], sender=Category)
def clear_cache_on_category_change(sender, **kwargs):
    clear_products_cache()

# Очищаем кэш при изменении информации о товарах
@receiver([post_save, post_delete], sender=ProductInfo)
def clear_cache_on_productinfo_change(sender, **kwargs):
    clear_products_cache()

# Очищаем кэш при изменении магазинов
@receiver([post_save, post_delete], sender=Shop)
def clear_cache_on_shop_change(sender, **kwargs):
    clear_products_cache()
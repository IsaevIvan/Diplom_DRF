from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

STATUS_CHOICES = (
    ('basket', 'В корзине'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)

USER_TYPES = (
    ('shop', 'Поставщик'),
    ('buyer', 'Покупатель'),
)


class UserManager(BaseUserManager):
    """
    Кастомный менеджер для модели User с email как username
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Создает и сохраняет пользователя с email и паролем
        """
        if not email:
            raise ValueError('Email должен быть указан')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Создает обычного пользователя
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Создает суперпользователя
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Кастомный пользователь системы с email как username
    """
    # Убираем обязательность username
    username = None
    email = models.EmailField('Email', unique=True)
    company = models.CharField('Название компании', max_length=100, blank=True)
    position = models.CharField('Должность', max_length=100, blank=True)
    type = models.CharField('Тип пользователя', choices=USER_TYPES, max_length=10, default='buyer')

    # Используем email как основной идентификатор
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # убираем username из обязательных полей

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Shop(models.Model):
    name = models.CharField('Название магазина', max_length=100)
    url = models.URLField('Сайт магазина', blank=True, null=True)
    user = models.OneToOneField(User, verbose_name='Владелец', on_delete=models.CASCADE,
                               related_name='shop', blank=True, null=True)
    is_active = models.BooleanField('Принимает заказы', default=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Категория товаров
    """
    name = models.CharField('Название категории', max_length=100)
    shops = models.ManyToManyField(Shop, verbose_name='Магазины', related_name='categories', blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Базовый продукт (без привязки к магазину)
    """
    name = models.CharField('Название товара', max_length=200)
    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE, related_name='products')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    """
    Информация о товаре в конкретном магазине
    """
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE, related_name='shop_items')
    shop = models.ForeignKey(Shop, verbose_name='Магазин', on_delete=models.CASCADE, related_name='products')
    external_id = models.PositiveIntegerField('ID у поставщика')
    model = models.CharField('Модель', max_length=100, blank=True)
    price = models.DecimalField('Цена закупки', max_digits=10, decimal_places=2)
    price_rrc = models.DecimalField('Рекомендуемая цена', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Количество на складе')

    class Meta:
        verbose_name = 'Информация о товаре'
        verbose_name_plural = 'Информация о товарах'
        unique_together = ('product', 'shop', 'external_id')

    def __str__(self):
        return f'{self.product.name} в {self.shop.name}'


class Parameter(models.Model):
    """
    Название параметра товара
    """
    name = models.CharField('Название параметра', max_length=100)

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    """
    Значение параметра для конкретного товара
    """
    product_info = models.ForeignKey(ProductInfo, verbose_name='Товар', on_delete=models.CASCADE,
                                     related_name='parameters')
    parameter = models.ForeignKey(Parameter, verbose_name='Параметр', on_delete=models.CASCADE)
    value = models.CharField('Значение', max_length=100)

    class Meta:
        verbose_name = 'Параметр товара'
        verbose_name_plural = 'Параметры товаров'
        unique_together = ('product_info', 'parameter')

    def __str__(self):
        return f'{self.parameter.name}: {self.value}'


class Contact(models.Model):
    """
    Контактная информация пользователя (адреса доставки)
    """
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE, related_name='contacts')
    city = models.CharField('Город', max_length=50)
    street = models.CharField('Улица', max_length=100)
    house = models.CharField('Дом', max_length=15, blank=True)
    building = models.CharField('Корпус/строение', max_length=15, blank=True)
    apartment = models.CharField('Квартира/офис', max_length=15, blank=True)
    phone = models.CharField('Телефон', max_length=20)

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'

    def __str__(self):
        return f'{self.city}, {self.street}, {self.house}'


class Order(models.Model):
    """
    Заказ пользователя
    """
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    # ИСПРАВЛЯЕМ: используем STATUS_CHOICES
    status = models.CharField('Статус', choices=STATUS_CHOICES, max_length=20, default='basket')
    contact = models.ForeignKey(Contact, verbose_name='Адрес доставки', on_delete=models.SET_NULL,
                                null=True, blank=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.id} от {self.user.email}'


class OrderItem(models.Model):
    """
    Товар в заказе
    """
    order = models.ForeignKey(Order, verbose_name='Заказ', on_delete=models.CASCADE, related_name='items')
    product_info = models.ForeignKey(ProductInfo, verbose_name='Товар', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField('Количество', default=1)

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'
        unique_together = ('order', 'product_info')

    def __str__(self):
        return f'{self.product_info.product.name} x {self.quantity}'

    @property
    def total_price(self):
        """Общая стоимость позиции"""
        return self.product_info.price * self.quantity
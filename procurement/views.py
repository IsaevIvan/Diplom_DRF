from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.db import transaction
import yaml
from django.utils import timezone

from .models import User, Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Contact, Order, OrderItem
from .serializers import *
from .services import send_order_confirmation_email, send_user_registration_email, send_order_status_email, \
    send_order_to_admin_email


# ==================== КОРНЕВОЙ API ENDPOINT ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """Корневой endpoint API с информацией о доступных endpoints"""
    endpoints = {
        "message": "Добро пожаловать в API Diplom Project DRF",
        "version": "1.0",
        "endpoints": {
            "authentication": {
                "register": {
                    "url": "/api/v1/user/register/",
                    "method": "POST",
                    "description": "Регистрация нового пользователя",
                    "auth_required": False
                },
                "login": {
                    "url": "/api/v1/user/login/",
                    "method": "POST",
                    "description": "Вход и получение токена",
                    "auth_required": False
                }
            },
            "products": {
                "list": {
                    "url": "/api/v1/products/",
                    "method": "GET",
                    "description": "Список товаров с фильтрацией",
                    "auth_required": False,
                    "parameters": {
                        "category_id": "Фильтр по категории",
                        "shop_id": "Фильтр по магазину"
                    }
                }
            },
            "cart": {
                "view": {
                    "url": "/api/v1/basket/",
                    "method": "GET",
                    "description": "Просмотр корзины",
                    "auth_required": True
                },
                "add": {
                    "url": "/api/v1/basket/add/",
                    "method": "POST",
                    "description": "Добавление товара в корзину",
                    "auth_required": True
                },
                "remove": {
                    "url": "/api/v1/basket/remove/",
                    "method": "POST",
                    "description": "Удаление товара из корзины",
                    "auth_required": True
                }
            },
            "contacts": {
                "list_create": {
                    "url": "/api/v1/user/contacts/",
                    "method": "GET, POST",
                    "description": "Просмотр и добавление контактов",
                    "auth_required": True
                },
                "detail": {
                    "url": "/api/v1/user/contacts/{id}/",
                    "method": "GET, PUT, DELETE",
                    "description": "Детали контакта",
                    "auth_required": True
                }
            },
            "orders": {
                "list": {
                    "url": "/api/v1/orders/",
                    "method": "GET",
                    "description": "История заказов",
                    "auth_required": True
                },
                "confirm": {
                    "url": "/api/v1/order/confirm/",
                    "method": "POST",
                    "description": "Подтверждение заказа",
                    "auth_required": True
                }
            },
            "partner": {
                "update": {
                    "url": "/api/v1/partner/update/",
                    "method": "POST",
                    "description": "Импорт товаров (только для поставщиков)",
                    "auth_required": True,
                    "user_type": "shop"
                }
            }
        },
        "authentication": "Используйте Token Authentication. Получите токен через /api/v1/user/login/",
        "docs": "Документация API доступна в README.md"
    }

    # Добавляем информацию о текущем пользователе если он аутентифицирован
    if request.user.is_authenticated:
        endpoints["user"] = {
            "email": request.user.email,
            "type": request.user.type,
            "is_authenticated": True
        }
    else:
        endpoints["user"] = {
            "is_authenticated": False,
            "message": "Для доступа к защищенным endpoints требуется аутентификация"
        }

    return Response(endpoints)


# ==================== АУТЕНТИФИКАЦИЯ ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Регистрация нового пользователя"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)

        # Отправляем приветственное письмо
        send_user_registration_email(user)

        return Response({
            'Status': True,
            'Message': 'Пользователь успешно зарегистрирован',
            'Token': token.key
        }, status=status.HTTP_201_CREATED)
    return Response({'Status': False, 'Errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Вход пользователя"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'Status': True,
            'Token': token.key,
            'User': UserSerializer(user).data
        })
    return Response({'Status': False, 'Errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# ==================== ТОВАРЫ ====================

class ProductListView(generics.ListAPIView):
    """Список товаров с фильтрацией"""
    serializer_class = ProductInfoSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = ProductInfo.objects.filter(shop__is_active=True, quantity__gt=0)

        # Фильтрация по категории
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(product__category_id=category_id)

        # Фильтрация по магазину
        shop_id = self.request.query_params.get('shop_id')
        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)

        return queryset.select_related('product', 'shop').prefetch_related('parameters__parameter')


# ==================== КОРЗИНА ====================

class CartView(generics.ListAPIView):
    """Просмотр корзины пользователя"""
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        order, created = Order.objects.get_or_create(
            user=self.request.user,
            status='basket'
        )
        return order.items.all()


class CartAddView(generics.CreateAPIView):
    """Добавление товара в корзину"""
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        product_info_id = request.data.get('product_info_id')
        quantity = request.data.get('quantity', 1)

        try:
            product_info = ProductInfo.objects.get(id=product_info_id)
        except ProductInfo.DoesNotExist:
            return Response({'Status': False, 'Error': 'Товар не найден'}, status=400)

        # Получаем или создаем корзину
        order, created = Order.objects.get_or_create(
            user=request.user,
            status='basket'
        )

        # Добавляем товар в корзину
        order_item, created = OrderItem.objects.get_or_create(
            order=order,
            product_info=product_info,
            defaults={'quantity': quantity}
        )

        if not created:
            order_item.quantity += quantity
            order_item.save()

        return Response({'Status': True, 'Message': 'Товар добавлен в корзину'})


class CartRemoveView(generics.DestroyAPIView):
    """Удаление товара из корзины"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        product_info_id = request.data.get('product_info_id')

        try:
            order = Order.objects.get(user=request.user, status='basket')
            order_item = OrderItem.objects.get(order=order, product_info_id=product_info_id)
            order_item.delete()
            return Response({'Status': True, 'Message': 'Товар удален из корзины'})
        except (Order.DoesNotExist, OrderItem.DoesNotExist):
            return Response({'Status': False, 'Error': 'Товар не найден в корзине'}, status=400)


# ==================== КОНТАКТЫ ====================

class ContactListView(generics.ListCreateAPIView):
    """Просмотр и добавление контактов"""
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Редактирование и удаление контактов"""
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)


# ==================== ЗАКАЗЫ ====================

class OrderListView(generics.ListAPIView):
    """Список заказов пользователя"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).exclude(status='basket')


class OrderConfirmView(generics.CreateAPIView):
    """Подтверждение заказа"""
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        contact_id = request.data.get('contact_id')

        try:
            contact = Contact.objects.get(id=contact_id, user=request.user)
        except Contact.DoesNotExist:
            return Response({'Status': False, 'Error': 'Контакт не найден'}, status=400)

        try:
            with transaction.atomic():
                # Получаем корзину
                order = Order.objects.get(user=request.user, status='basket')

                # Проверяем наличие товаров
                for item in order.items.all():
                    if item.quantity > item.product_info.quantity:
                        return Response({
                            'Status': False,
                            'Error': f'Недостаточно товара: {item.product_info.product.name}'
                        }, status=400)

                # Подтверждаем заказ
                order.status = 'new'
                order.contact = contact
                order.save()

                # Резервируем товары
                for item in order.items.all():
                    item.product_info.quantity -= item.quantity
                    item.product_info.save()

                # Отправляем email с подтверждением заказа
                send_order_confirmation_email(order)
                send_order_to_admin_email(order)

                return Response({
                    'Status': True,
                    'Message': 'Заказ подтвержден',
                    'OrderId': order.id
                })

        except Order.DoesNotExist:
            return Response({'Status': False, 'Error': 'Корзина пуста'}, status=400)


# ==================== ИМПОРТ ДЛЯ ПОСТАВЩИКОВ ====================

class PartnerUpdate(APIView):
    """
    Класс для обновления прайса от поставщика
    """

    def post(self, request, *args, **kwargs):
        # Проверяем аутентификацию
        if not request.user.is_authenticated:
            return Response({'Status': False, 'Error': 'Требуется авторизация'},
                            status=status.HTTP_403_FORBIDDEN)

        # Проверяем что пользователь - поставщик
        if request.user.type != 'shop':
            return Response({'Status': False, 'Error': 'Только для поставщиков'},
                            status=status.HTTP_403_FORBIDDEN)

        # Получаем файл из запроса
        yaml_file = request.FILES.get('file')
        if not yaml_file:
            return Response({'Status': False, 'Error': 'YAML файл не предоставлен'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # Читаем и парсим YAML
            data = yaml.safe_load(yaml_file.read().decode('utf-8'))

            # Импортируем данные
            result = self.import_data(data, request.user)
            return Response(result)

        except yaml.YAMLError as e:
            return Response({'Status': False, 'Error': f'Ошибка парсинга YAML: {str(e)}'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'Status': False, 'Error': f'Ошибка импорта: {str(e)}'},
                            status=status.HTTP_400_BAD_REQUEST)

    def import_data(self, data, user):
        """Импорт данных из YAML"""
        try:
            with transaction.atomic():
                # Получаем или создаем магазин
                shop, created = Shop.objects.get_or_create(
                    name=data['shop'],
                    defaults={'user': user, 'is_active': True}
                )

                # Если магазин уже существует, проверяем владельца
                if not created and shop.user != user:
                    return {'Status': False, 'Error': 'У вас нет прав на обновление этого магазина'}

                # Обрабатываем категории
                for category_data in data.get('categories', []):
                    category, _ = Category.objects.get_or_create(
                        id=category_data['id'],
                        defaults={'name': category_data['name']}
                    )
                    category.shops.add(shop)
                    category.save()

                # Удаляем старые товары магазина
                ProductInfo.objects.filter(shop=shop).delete()

                # Обрабатываем товары
                for product_data in data.get('goods', []):
                    # Создаем или получаем базовый продукт
                    product, _ = Product.objects.get_or_create(
                        name=product_data['name'],
                        category_id=product_data['category']
                    )

                    # Создаем информацию о товаре в магазине
                    product_info = ProductInfo.objects.create(
                        product=product,
                        shop=shop,
                        external_id=product_data['id'],
                        model=product_data.get('model', ''),
                        price=product_data['price'],
                        price_rrc=product_data['price_rrc'],
                        quantity=product_data['quantity']
                    )

                    # Обрабатываем параметры товара
                    for param_name, param_value in product_data.get('parameters', {}).items():
                        parameter, _ = Parameter.objects.get_or_create(name=param_name)
                        ProductParameter.objects.create(
                            product_info=product_info,
                            parameter=parameter,
                            value=str(param_value)
                        )

                return {
                    'Status': True,
                    'Message': f'Импорт завершен. Магазин: {shop.name}, Товаров: {len(data.get("goods", []))}'
                }

        except Exception as e:
            return {'Status': False, 'Error': f'Ошибка транзакции: {str(e)}'}


# ==================== УПРАВЛЕНИЕ СТАТУСОМ ЗАКАЗА ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    """Изменение статуса заказа (для администраторов/поставщиков)"""
    try:
        order = Order.objects.get(id=order_id)

        # Проверяем права
        user = request.user
        if user.type != 'shop' and not user.is_staff:
            return Response({'Status': False, 'Error': 'Недостаточно прав'}, status=403)

        new_status = request.data.get('status')
        if not new_status:
            return Response({'Status': False, 'Error': 'Статус не указан'}, status=400)

        # Проверяем валидность статуса
        valid_statuses = dict(Order._meta.get_field('status').choices).keys()
        if new_status not in valid_statuses:
            return Response({'Status': False, 'Error': f'Неверный статус. Допустимые: {list(valid_statuses)}'},
                            status=400)

        old_status = order.status
        order.status = new_status
        order.save()

        # Отправляем email об изменении статуса
        send_order_status_email(order, old_status, new_status)

        return Response({
            'Status': True,
            'Message': f'Статус заказа #{order_id} изменен: {old_status} -> {new_status}',
            'order_id': order_id,
            'old_status': old_status,
            'new_status': new_status
        })

    except Order.DoesNotExist:
        return Response({'Status': False, 'Error': 'Заказ не найден'}, status=404)
    except Exception as e:
        return Response({'Status': False, 'Error': str(e)}, status=400)
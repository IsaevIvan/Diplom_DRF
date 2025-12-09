# procurement/urls.py
from django.urls import path
from . import views
from django_rest_passwordreset.views import ResetPasswordRequestToken, ResetPasswordConfirm


urlpatterns = [
    # Корневой endpoint API
    path('', views.api_root, name='api-root'),

    # Аутентификация
    path('user/register/', views.register_view, name='user-register'),
    path('user/login/', views.login_view, name='user-login'),

    # Товары
    path('products/', views.ProductListView.as_view(), name='product-list'),

    # Корзина
    path('basket/', views.CartView.as_view(), name='basket'),
    path('basket/add/', views.CartAddView.as_view(), name='basket-add'),
    path('basket/remove/', views.CartRemoveView.as_view(), name='basket-remove'),

    # Контакты
    path('user/contacts/', views.ContactListView.as_view(), name='contact-list'),
    path('user/contacts/<int:pk>/', views.ContactDetailView.as_view(), name='contact-detail'),

    # Заказы
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('order/confirm/', views.OrderConfirmView.as_view(), name='order-confirm'),
    path('orders/<int:order_id>/status/', views.update_order_status, name='order-status-update'),

    # Импорт для поставщиков
    path('partner/update/', views.PartnerUpdate.as_view(), name='partner-update'),

    # Восстановление пароля
    path('user/password/reset/', ResetPasswordRequestToken.as_view(), name='password-reset'),
    path('user/password/reset/confirm/', ResetPasswordConfirm.as_view(), name='password-reset-confirm'),
]
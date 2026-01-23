from django.utils.translation import gettext_lazy as _


# Кастомизация меню админки
BATON_MENU = [
    {
        'type': 'title',
        'label': 'Основное',
        'items': [
            {
                'type': 'model',
                'label': _('Пользователи'),
                'name': 'user',
                'app': 'procurement',
                'icon': 'fa fa-user',
            },
            {
                'type': 'model',
                'label': _('Магазины'),
                'name': 'shop',
                'app': 'procurement',
                'icon': 'fa fa-store',
            },
            {
                'type': 'model',
                'label': _('Категории'),
                'name': 'category',
                'app': 'procurement',
                'icon': 'fa fa-tags',
            },
        ]
    },
    {
        'type': 'title',
        'label': 'Товары',
        'items': [
            {
                'type': 'model',
                'label': _('Товары'),
                'name': 'product',
                'app': 'procurement',
                'icon': 'fa fa-box',
            },
            {
                'type': 'model',
                'label': _('Информация о товарах'),
                'name': 'productinfo',
                'app': 'procurement',
                'icon': 'fa fa-info-circle',
            },
            {
                'type': 'model',
                'label': _('Параметры'),
                'name': 'parameter',
                'app': 'procurement',
                'icon': 'fa fa-list',
            },
        ]
    },
    {
        'type': 'title',
        'label': 'Заказы и доставка',
        'items': [
            {
                'type': 'model',
                'label': _('Заказы'),
                'name': 'order',
                'app': 'procurement',
                'icon': 'fa fa-shopping-cart',
            },
            {
                'type': 'model',
                'label': _('Контакты'),
                'name': 'contact',
                'app': 'procurement',
                'icon': 'fa fa-address-book',
            },
        ]
    },
    {
        'type': 'title',
        'label': 'Система',
        'items': [
            {
                'type': 'app',
                'name': 'auth',
                'label': _('Аутентификация'),
                'icon': 'fa fa-lock',
                'models': [
                    {
                        'name': 'user',
                        'label': _('Пользователи (система)')
                    },
                    {
                        'name': 'group',
                        'label': _('Группы')
                    },
                ]
            },
            {
                'type': 'link',
                'label': _('Документация API'),
                'url': '/swagger/',
                'icon': 'fa fa-book',
            },
            {
                'type': 'link',
                'label': _('Главная страница'),
                'url': '/',
                'icon': 'fa fa-home',
            },
        ]
    },
]

# Обновляем конфигурацию baton
BATON_CONFIG = {
    'MENU': BATON_MENU,
}
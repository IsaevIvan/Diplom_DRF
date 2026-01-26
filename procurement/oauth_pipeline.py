from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()


def create_drf_token(strategy, backend, user, response, details, is_new=False, *args, **kwargs):
    """
    Кастомный pipeline шаг для создания DRF токена
    после успешной OAuth аутентификации
    """
    # Создаем или получаем токен для пользователя
    token, created = Token.objects.get_or_create(user=user)

    # Сохраняем токен в extra_data для использования в view
    return {
        'drf_token': token.key,
        'is_new': is_new,
        'user': user
    }
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import redirect
from django.conf import settings
from rest_framework.authtoken.models import Token


class YandexOAuthLogin(APIView):
    """Начало OAuth процесса с Яндекс"""
    permission_classes = [AllowAny]

    def get(self, request):
        # Перенаправляем на страницу авторизации Яндекс
        return redirect(f'/oauth/login/yandex-oauth2/')


class OAuthSuccess(APIView):
    """Успешная OAuth аутентификация - возвращает DRF токен"""
    permission_classes = [AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            # Получаем токен пользователя
            token, created = Token.objects.get_or_create(user=request.user)

            return Response({
                'status': True,
                'message': 'Успешная авторизация через Яндекс',
                'token': token.key,
                'user': {
                    'id': request.user.id,
                    'email': request.user.email,
                    'first_name': request.user.first_name or '',
                    'last_name': request.user.last_name or '',
                    'type': request.user.type,
                }
            })
        return Response({
            'status': False,
            'message': 'Пользователь не аутентифицирован'
        }, status=401)


class OAuthError(APIView):
    """Ошибка OAuth аутентификации"""
    permission_classes = [AllowAny]

    def get(self, request):
        error = request.GET.get('error', 'Неизвестная ошибка')
        error_description = request.GET.get('error_description', '')

        return Response({
            'status': False,
            'message': f'Ошибка OAuth авторизации',
            'error': error,
            'error_description': error_description
        }, status=400)
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import include
from procurement import oauth_views


# Простая view для корневого URL
def home_view(request):
    return HttpResponse("""
    <h1>Diplom Project DRF</h1>
    <p><a href="/api/v1/">API</a> | <a href="/admin/">Admin</a> | <a href="/swagger/">Swagger</a></p>
    <p><strong>Админка теперь с django-baton!</strong></p>
    """)


# Swagger схема
schema_view = get_schema_view(
    openapi.Info(
        title="Diplom Project API",
        default_version='v1',
        description="API для системы закупок",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', home_view, name='home'),

    # Baton URLs
    path('admin/', include('baton.urls')),

    # Стандартная админка
    path('admin/', admin.site.urls),

    path('api/v1/', include('procurement.urls')),

    # Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),

    # OAuth аутентификация (социальная)
    path('oauth/', include('social_django.urls', namespace='social')),

    # Кастомные OAuth endpoints
    path('api/v1/user/oauth/yandex/login/', oauth_views.YandexOAuthLogin.as_view(), name='yandex-oauth-login'),
    path('api/v1/user/oauth/success/', oauth_views.OAuthSuccess.as_view(), name='oauth-success'),
    path('api/v1/user/oauth/error/', oauth_views.OAuthError.as_view(), name='oauth-error'),
]
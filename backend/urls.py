from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


# Простая view для корневого URL
def home_view(request):
    return HttpResponse("""
    <h1>Diplom Project DRF</h1>
    <p><a href="/api/v1/">API</a> | <a href="/admin/">Admin</a> | <a href="/swagger/">Swagger</a></p>
    """)


# Swagger схема (МИНИМАЛЬНАЯ)
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
    path('admin/', admin.site.urls),
    path('api/v1/', include('procurement.urls')),

    # Swagger (ВСЕГО 3 СТРОКИ)
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
]
"""
Django settings for backend project.
"""
import os
import socket
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key-for-dev')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'baton',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_rest_passwordreset',
    'corsheaders',
    'drf_yasg',
    'procurement',
    'baton.autodiscover',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# ==================== БАЗА ДАННЫХ ====================
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME', 'diplom_procurement_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# ==================== REDIS НАСТРОЙКИ ====================
# Определяем, находимся ли мы в Docker окружении
def is_running_in_docker():
    """Проверяем, запущено ли приложение в Docker"""
    try:
        # Пробуем разрешить имя сервиса redis
        socket.gethostbyname('redis')
        return True
    except socket.gaierror:
        return False

# Определяем хост Redis в зависимости от окружения
REDIS_HOST = 'redis' if is_running_in_docker() else 'localhost'
print(f"🔧 Redis хост: {REDIS_HOST}")

# ==================== CELERY НАСТРОЙКИ ====================
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:6379/0'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Moscow'

# Для разработки - синхронный режим (отладочный)
CELERY_TASK_ALWAYS_EAGER = False

print(f"🔧 Celery настроен: BROKER_URL={CELERY_BROKER_URL}")

# ==================== REDIS КЭШИРОВАНИЕ ====================
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:6379/1",  # Используем базу 1 для кэша
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "MAX_ENTRIES": 1000,  # Максимум записей в кэше
            "CULL_FREQUENCY": 3,   # Удалять 1/3 записей при достижении лимита
            "SOCKET_CONNECT_TIMEOUT": 5,  # Таймаут подключения
            "SOCKET_TIMEOUT": 5,  # Таймаут операций
        },
        "KEY_PREFIX": "diplom",  # Префикс для всех ключей кэша
    }
}

# Время жизни кэша по умолчанию (в секундах)
CACHE_TTL = 60 * 15  # 15 минут

# Кэширование сессий (опционально, но полезно)
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Custom user model
AUTH_USER_MODEL = 'procurement.User'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Для разработки
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.mail.ru')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '465'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'True') == 'True'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': int(os.getenv('PAGE_SIZE', '40')),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'procurement.throttles.RegisterThrottle',
        'procurement.throttles.LoginThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
        'register': '5/hour',    # 5 регистраций в час с одного IP
        'login': '10/hour',      # 10 попыток входа в час на email
        'burst': '30/minute',    # 30 запросов в минуту
    }
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # Для разработки, в production нужно ограничить

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Token': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}

# Baton admin panel settings
BATON = {
    'SITE_HEADER': 'Diplom Project DRF',
    'SITE_TITLE': 'Админ-панель закупок',
    'INDEX_TITLE': 'Управление системой закупок',
    'SUPPORT_HREF': 'mailto:devdreamer@yandex.com',
    'COPYRIGHT': '© 2024 Diplom Project DRF',
    'POWERED_BY': '<a href="https://github.com/IsaevIvan">Isaev Ivan</a>',
    'CONFIRM_UNSAVED_CHANGES': True,
    'SHOW_MULTIPART_UPLOADING': True,
    'ENABLE_IMAGES_PREVIEW': True,
    'CHANGELIST_FILTERS_IN_MODAL': True,
    'CHANGELIST_FILTERS_ALWAYS_OPEN': False,
    'CHANGELIST_FILTERS_FORM': True,
    'MENU_ALWAYS_COLLAPSED': False,
    'MENU_TITLE': 'Меню',
    'GRAVATAR_DEFAULT_IMG': 'retro',
    'GRAVATAR_ENABLED': False,
    'FORCE_THEME': None,
    'MESSAGES_TOASTS': True,
}

# Импортируем меню
try:
    from procurement.baton_config import BATON_CONFIG
    BATON.update(BATON_CONFIG)
except ImportError:
    pass

# ==================== ДОПОЛНИТЕЛЬНЫЕ ПРОВЕРКИ ====================
if DEBUG:
    print(f"🔧 Настройки Redis:")
    print(f"   - Хост: {REDIS_HOST}")
    print(f"   - Celery: {CELERY_BROKER_URL}")
    print(f"   - Кэш: {CACHES['default']['LOCATION']}")


# ==================== YANDEX OAUTH НАСТРОЙКИ ====================
INSTALLED_APPS += [
    'social_django',  # OAuth аутентификация
]

AUTHENTICATION_BACKENDS = (
    'social_core.backends.yandex.YandexOAuth2',  # Яндекс OAuth
    'django.contrib.auth.backends.ModelBackend',  # Стандартный бэкенд Django
)

# Яндекс OAuth настройки
SOCIAL_AUTH_YANDEX_OAUTH2_KEY = os.getenv('YANDEX_OAUTH_KEY', '')
SOCIAL_AUTH_YANDEX_OAUTH2_SECRET = os.getenv('YANDEX_OAUTH_SECRET', '')
SOCIAL_AUTH_YANDEX_OAUTH2_SCOPE = ['login:email', 'login:info']

# URL для редиректа
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/api/v1/user/oauth/success/'
SOCIAL_AUTH_LOGIN_ERROR_URL = '/api/v1/user/oauth/error/'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/api/v1/user/oauth/success/'

# Настройки для работы с кастомной User моделью
SOCIAL_AUTH_USER_MODEL = 'procurement.User'
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True

# Pipeline для обработки данных пользователя
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    # Кастомный шаг для генерации DRF токена
    'procurement.oauth_pipeline.create_drf_token',
)

# Настройки сессий для OAuth
SOCIAL_AUTH_RAISE_EXCEPTIONS = False
SOCIAL_AUTH_URLOPEN_TIMEOUT = 10
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Создаем Celery приложение
app = Celery('backend')

# Загружаем настройки из settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи в приложениях
app.autodiscover_tasks()

# Простая задача для проверки
@app.task(bind=True)
def debug_task(self):
    return 'Celery работает!'

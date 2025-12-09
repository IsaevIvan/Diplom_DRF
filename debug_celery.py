import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django

django.setup()

print("🔍 ДЕБАГ CELERY...")

# 1. Проверяем настройки
from django.conf import settings

print(f"1. Настройки Celery:")
print(f"   CELERY_BROKER_URL: {getattr(settings, 'CELERY_BROKER_URL', 'NOT SET')}")
print(f"   DEBUG: {settings.DEBUG}")
print(f"   CELERY_TASK_ALWAYS_EAGER: {getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', 'NOT SET')}")

# 2. Проверяем задачи
print(f"\n2. Проверяем задачи...")
try:
    from procurement.tasks import send_email_async

    print(f"   ✅ Задача send_email_async найдена")
except ImportError as e:
    print(f"   ❌ Ошибка импорта: {e}")

# 3. Проверяем Redis соединение
print(f"\n3. Проверяем Redis...")
try:
    import redis

    r = redis.Redis(host='localhost', port=6379, db=0)
    response = r.ping()
    print(f"   ✅ Redis подключен: {response}")
except Exception as e:
    print(f"   ❌ Ошибка Redis: {e}")

# 4. Пробуем отправить задачу
print(f"\n4. Пробуем отправить задачу...")
try:
    from procurement.tasks import send_email_async

    task = send_email_async.delay(
        subject="DEBUG тест",
        message="Это debug тест",
        recipient_list=["debug@test.com"]
    )
    print(f"   ✅ Задача отправлена! ID: {task.id}")
    print(f"   Статус: {task.status}")

    # Проверяем очередь в Redis
    import redis

    r = redis.Redis(host='localhost', port=6379, db=0)
    queue_length = r.llen('celery')
    print(f"   Длина очереди в Redis: {queue_length}")

except Exception as e:
    print(f"   ❌ Ошибка отправки задачи: {e}")
    import traceback

    traceback.print_exc()

print("\n🎯 ДЕБАГ ЗАВЕРШЕН")
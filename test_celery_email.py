import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from procurement.tasks import (
    send_email_async,
    send_welcome_email_async,
    send_order_email_async
)
from procurement.models import User, Order
from django.contrib.auth import get_user_model


def test_celery_email_workflow():
    """Тестирование отправки email через Celery для нашего проекта"""
    print("🚀 ТЕСТИРОВАНИЕ CELERY EMAIL ДЛЯ DIPLOM PROJECT\n")

    # 1. Простая тестовая отправка email
    print("1. 📧 Простая отправка email через Celery...")
    try:
        task = send_email_async.delay(
            subject="Тест Celery из Diplom Project",
            message="Это тестовое письмо, отправленное через Celery!\n\nЕсли вы видите это в консоли Celery - всё работает! 🎉",
            recipient_list=["test@example.com", "admin@example.com"]
        )
        print(f"   ✅ Задача поставлена в очередь. ID: {task.id}")
        print(f"   📋 Статус: {task.status}")

        # Ждем и проверяем
        time.sleep(3)
        if task.ready():
            result = task.get(timeout=2)
            print(f"   📦 Результат: {result}")
        else:
            print(f"   ⏳ Задача еще выполняется...")

    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # 2. Тест приветственного email
    print("\n2. 👤 Тест приветственного email (регистрация)...")
    try:
        # Создаем тестового пользователя или берем существующего
        User = get_user_model()
        test_email = f"test_celery_{int(time.time())}@example.com"

        user, created = User.objects.get_or_create(
            email=test_email,
            defaults={
                'first_name': 'Тестовый',
                'last_name': 'Пользователь',
                'type': 'buyer',
                'is_active': True
            }
        )

        if created:
            user.set_password('password123')
            user.save()
            print(f"   ✅ Создан тестовый пользователь: {user.email}")
        else:
            print(f"   ⚠️ Используем существующего пользователя: {user.email}")

        task = send_welcome_email_async.delay(
            user_email=user.email,
            user_name=f"{user.first_name} {user.last_name}"
        )
        print(f"   ✅ Задача отправки приветствия поставлена. ID: {task.id}")
        print(f"   👤 Пользователь: {user.email}")

    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

    # 3. Тест email подтверждения заказа
    print("\n3. 🛒 Тест email подтверждения заказа...")
    try:
        # Берем последний заказ или создаем тестовый
        order = Order.objects.exclude(status='basket').first()

        if order:
            print(f"   ✅ Найден заказ #{order.id} для пользователя {order.user.email}")
            task = send_order_email_async.delay(
                order_id=order.id,
                user_email=order.user.email
            )
            print(f"   ✅ Задача подтверждения заказа поставлена. ID: {task.id}")
            print(f"   📦 Заказ: #{order.id}, Пользователь: {order.user.email}")
        else:
            print("   ⚠️ Заказы не найдены, создаем тестовый...")

            # Создаем тестовый заказ
            user = User.objects.filter(type='buyer').first()
            if not user:
                user = User.objects.create_user(
                    email='test_order@example.com',
                    password='password123',
                    first_name='Тестовый',
                    last_name='Покупатель',
                    type='buyer'
                )
                print(f"   ✅ Создан тестовый покупатель: {user.email}")

            # Создаем тестовый заказ
            from procurement.models import Contact
            contact, _ = Contact.objects.get_or_create(
                user=user,
                defaults={
                    'city': 'Москва',
                    'street': 'Тестовая',
                    'house': '1',
                    'phone': '+79991112233'
                }
            )

            order = Order.objects.create(
                user=user,
                status='new',
                contact=contact
            )
            print(f"   ✅ Создан тестовый заказ #{order.id}")

            task = send_order_email_async.delay(
                order_id=order.id,
                user_email=user.email
            )
            print(f"   ✅ Задача подтверждения заказа поставлена. ID: {task.id}")

    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

    # 4. Массовая отправка (демонстрация асинхронности)
    print("\n4. 🔄 Массовая отправка email (демонстрация асинхронности)...")
    try:
        tasks = []
        for i in range(3):
            task = send_email_async.delay(
                subject=f"Массовый тест #{i + 1}",
                message=f"Это тестовое письмо #{i + 1}, отправленное асинхронно через Celery!",
                recipient_list=[f"test{i}@example.com"]
            )
            tasks.append(task)
            print(f"   📤 Задача #{i + 1} поставлена: {task.id}")

        # Проверяем статусы сразу после запуска
        print("\n   📊 Статусы задач сразу после запуска:")
        for i, task in enumerate(tasks, 1):
            print(f"   Задача #{i}: {task.id} -> {task.status}")

        # Ждем и проверяем снова
        print("\n   ⏳ Ждем 5 секунд...")
        time.sleep(5)

        print("   📊 Статусы задач после ожидания:")
        for i, task in enumerate(tasks, 1):
            if task.ready():
                result = task.get(timeout=1)
                print(f"   Задача #{i}: {task.id} -> {task.status} -> {result}")
            else:
                print(f"   Задача #{i}: {task.id} -> {task.status} (все еще выполняется)")

    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    print("\n" + "=" * 60)
    print("🎯 ТЕСТИРОВАНИЕ CELERY ЗАВЕРШЕНО!")
    print("=" * 60)

    print("\n📋 ЧТО ПРОВЕРИТЬ:")
    print("   1. ✅ В терминале с Celery worker должны быть сообщения:")
    print("      - '📧 Celery: Отправка email...'")
    print("      - '✅ Email отправлен успешно'")
    print("      - Задачи должны меняться: PENDING → STARTED → SUCCESS")
    print("\n   2. ✅ В терминале с Django НЕ должно быть сообщений об отправке email")
    print("\n   3. ✅ Скорость: Запросы к API должны отвечать моментально")

    print("\n🔧 КАК ПРОВЕРИТЬ СТАТУС ЗАДАЧ:")
    print("   python manage.py shell")
    print("   from celery.result import AsyncResult")
    print("   from backend.celery import app")
    print("   result = AsyncResult('ВАШ_TASK_ID', app=app)")
    print("   print(f'Статус: {result.status}, Результат: {result.result}')")

    print("\n🎉 Если всё работает - Celery успешно настроен!")


if __name__ == '__main__':
    test_celery_email_workflow()
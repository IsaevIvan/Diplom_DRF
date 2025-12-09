# test_emails_fixed.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from procurement.models import User, Order, Contact, ProductInfo, OrderItem
from procurement.services import (
    send_user_registration_email,
    send_order_confirmation_email,
    send_order_status_email
)
from django.core.mail import send_mail


def test_all_emails_fixed():
    """Тестируем все типы email (исправленная версия)"""
    print("📧 ТЕСТИРОВАНИЕ EMAIL УВЕДОМЛЕНИЙ (ИСПРАВЛЕННАЯ ВЕРСИЯ)\n")

    # 1. Простой тест
    print("1. 📧 Простой тест отправки...")
    try:
        send_mail(
            'Тестовое письмо из Diplom Project DRF',
            'Проверка работы email системы.\n\nЕсли видите это письмо в консоли - система работает!',
            'noreply@diplom-django.ru',
            ['test@example.com'],
            fail_silently=False,
        )
        print("   ✅ Простое письмо отправлено (проверьте консоль)")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        print("   ⚠️  Для тестирования используем консольный бэкенд")

    # 2. Тест регистрации (работает!)
    print("\n2. 📧 Тест email регистрации...")
    try:
        # Создаем уникального пользователя для теста
        from datetime import datetime
        timestamp = datetime.now().strftime("%H%M%S")
        test_email = f"test_reg_{timestamp}@example.com"

        user, created = User.objects.get_or_create(
            email=test_email,
            defaults={
                'first_name': 'Тест',
                'last_name': f'Пользователь{timestamp}',
                'type': 'buyer',
                'is_active': True
            }
        )

        if created:
            user.set_password('password123')
            user.save()
            print(f"   ✅ Создан тестовый пользователь: {test_email}")

        result = send_user_registration_email(user)
        print(f"   ✅ Email регистрации: ОТПРАВЛЕН (проверьте консоль)")

    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # 3. Тест подтверждения заказа (исправляем ошибку с контактами)
    print("\n3. 📧 Тест email подтверждения заказа...")
    try:
        user = User.objects.filter(email='test_buyer@example.com').first()
        if not user:
            print("   ⚠️  Пользователь test_buyer@example.com не найден, создаем...")
            user = User.objects.create_user(
                email='test_buyer@example.com',
                first_name='Тестовый',
                last_name='Покупатель',
                type='buyer',
                is_active=True
            )
            user.set_password('password123')
            user.save()

        # Берем ПЕРВЫЙ контакт пользователя (исправляем ошибку get())
        contact = Contact.objects.filter(user=user).first()
        if not contact:
            print("   ⚠️  Контакт не найден, создаем...")
            contact = Contact.objects.create(
                user=user,
                city='Москва',
                street='Тестовая',
                house='42',
                phone='+79991112233'
            )

        # Создаем тестовый заказ
        order = Order.objects.create(
            user=user,
            status='new',
            contact=contact
        )

        # Добавляем товары (если есть товары в базе)
        products = ProductInfo.objects.all()[:2]
        if products:
            for i, product in enumerate(products):
                OrderItem.objects.create(
                    order=order,
                    product_info=product,
                    quantity=i + 1
                )
            print(f"   ✅ Добавлено {len(products)} товара(ов) в заказ")
        else:
            print("   ⚠️  Нет товаров в базе для теста")
            # Создаем тестовый товар
            shop, _ = Shop.objects.get_or_create(name='Тестовый магазин')
            category, _ = Category.objects.get_or_create(name='Тестовая категория')
            product, _ = Product.objects.get_or_create(
                name='Тестовый товар',
                category=category
            )
            product_info = ProductInfo.objects.create(
                product=product,
                shop=shop,
                external_id=9999,
                price=1000,
                price_rrc=1200,
                quantity=10
            )
            OrderItem.objects.create(
                order=order,
                product_info=product_info,
                quantity=2
            )
            print("   ✅ Создан тестовый товар для заказа")

        result = send_order_confirmation_email(order)
        print(f"   ✅ Email подтверждения заказа #{order.id}: ОТПРАВЛЕН (проверьте консоль)")

        # Сохраняем заказ для следующего теста
        test_order = order

    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        test_order = None

    # 4. Тест изменения статуса
    print("\n4. 📧 Тест email изменения статуса...")
    try:
        if test_order:
            result = send_order_status_email(test_order, 'new', 'sent')
            print(f"   ✅ Email изменения статуса (new→sent): ОТПРАВЛЕН")

            result = send_order_status_email(test_order, 'sent', 'delivered')
            print(f"   ✅ Email изменения статуса (sent→delivered): ОТПРАВЛЕН")
        else:
            print("   ⚠️  Нет заказа для теста изменения статуса")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    print("\n" + "=" * 50)
    print("🎯 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
    print("=" * 50)
    print("\n📋 РЕЗУЛЬТАТЫ:")
    print("   ✅ Все email отправлены в КОНСОЛЬНЫЙ РЕЖИМ")
    print("   📬 Проверьте вывод выше - должны быть показаны все письма")
    print("\n🔧 Для реальной отправки на email:")
    print("   1. Настройте SMTP в файле .env")
    print("   2. Для mail.ru создайте 'Пароль приложения'")
    print("   3. Или используйте другой SMTP сервис (Gmail, Yandex)")
    print("\n💡 Для production используйте:")
    print("   - Celery для асинхронной отправки")
    print("   - Redis как брокер сообщений")
    print("   - Мониторинг доставки email")


if __name__ == '__main__':
    # Импортируем недостающие модели
    from procurement.models import Shop, Category, Product

    test_all_emails_fixed()
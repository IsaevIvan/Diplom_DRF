from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from celery import shared_task
from .tasks import send_email_async, send_welcome_email_async, send_order_email_async


def send_user_registration_email(user):
    """Отправка приветственного email (через Celery)"""
    try:
        # Запускаем асинхронно через Celery
        task = send_welcome_email_async.delay(
            user_email=user.email,
            user_name=f"{user.first_name} {user.last_name}"
        )

        print(f"✅ Приветственный email поставлен в очередь (Task ID: {task.id})")
        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def send_order_confirmation_email(order):
    """Отправка email с подтверждением заказа (через Celery)"""
    try:
        # Создаем сообщение
        items_text = "\n".join([
            f"- {item.product_info.product.name}: {item.quantity} шт."
            for item in order.items.all()
        ])

        message = f"""
        Ваш заказ #{order.id} подтвержден!

        Состав заказа:
        {items_text}

        Статус: {order.get_status_display()}
        Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}

        Спасибо за покупку!
        """

        # Отправляем через Celery
        task = send_email_async.delay(
            subject=f"Подтверждение заказа #{order.id}",
            message=message,
            recipient_list=[order.user.email]
        )

        print(f"✅ Email подтверждения заказа поставлен в очередь (Task ID: {task.id})")
        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def send_order_status_email(order, old_status, new_status):
    """Отправка email об изменении статуса заказа"""
    try:
        user = order.user

        # Получаем отображаемые названия статусов
        status_choices = dict(order._meta.get_field('status').choices)
        old_status_display = status_choices.get(old_status, old_status)
        new_status_display = status_choices.get(new_status, new_status)

        # Текст письма
        text_content = f"""
        Уважаемый(ая) {user.first_name} {user.last_name},

        Статус вашего заказа был обновлен.

        Изменение статуса заказа #{order.id}:
        Было: {old_status_display}
        Стало: {new_status_display}
        Дата изменения: {timezone.now().strftime('%d.%m.%Y %H:%M')}

        Информация о заказе:
        Номер заказа: #{order.id}
        Дата создания: {order.created_at.strftime('%d.%m.%Y %H:%M')}

        {f'Адрес доставки: {order.contact.city}, {order.contact.street}, {order.contact.house}' if order.contact else ''}

        Вы можете отслеживать статус заказа в вашем личном кабинете.

        С уважением,
        Команда Diplom Project DRF
        """

        # Отправляем через Celery
        task = send_email_async.delay(
            subject=f'Статус вашего заказа #{order.id} изменен',
            message=text_content,
            recipient_list=[user.email]
        )

        print(f"✅ Email о смене статуса поставлен в очередь (Task ID: {task.id})")
        return True

    except Exception as e:
        print(f"❌ Ошибка отправки email о статусе: {str(e)}")
        return False


def send_order_to_admin_email(order):
    """Отправка заказа администратору"""
    try:
        user = order.user
        items = order.items.all()

        # Рассчитываем общую сумму
        total_amount = sum(item.quantity * item.product_info.price for item in items)

        # Получаем email администратора из настроек
        admin_email = settings.ADMIN_EMAIL if hasattr(settings, 'ADMIN_EMAIL') else settings.DEFAULT_FROM_EMAIL

        text_content = f"""
        НОВЫЙ ЗАКАЗ #{order.id}

        Информация о клиенте:
        Пользователь: {user.first_name} {user.last_name} ({user.email})
        Компания: {user.company or 'Не указана'}
        Телефон: {order.contact.phone if order.contact else 'Не указан'}

        Адрес доставки:
        {order.contact.city}, {order.contact.street}, {order.contact.house} {order.contact.apartment or ''}

        Состав заказа:
        {chr(10).join([f'- {item.product_info.product.name} (магазин: {item.product_info.shop.name}) - {item.quantity} шт. × {item.product_info.price} руб.' for item in items])}

        Общая сумма: {total_amount} руб.
        Статус: {order.get_status_display()}
        Дата заказа: {order.created_at.strftime('%d.%m.%Y %H:%M')}

        Требуется выполнение заказа!
        """

        # Отправляем через Celery
        task = send_email_async.delay(
            subject=f'НОВЫЙ ЗАКАЗ #{order.id} - требуется выполнение',
            message=text_content,
            recipient_list=[admin_email]
        )

        print(f"✅ Email администратору поставлен в очередь (Task ID: {task.id})")
        return True

    except Exception as e:
        print(f"❌ Ошибка отправки email администратору: {str(e)}")
        return False


def send_test_email():
    """Функция для тестирования отправки email"""
    try:
        subject = 'Тестовое письмо из Diplom Project DRF'
        message = 'Это тестовое письмо для проверки работы email системы.'

        # Отправляем через Celery
        task = send_email_async.delay(
            subject=subject,
            message=message,
            recipient_list=['test@example.com']
        )

        print(f"✅ Тестовое письмо поставлено в очередь (Task ID: {task.id})")
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки тестового письма: {e}")
        return False
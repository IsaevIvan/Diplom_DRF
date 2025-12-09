from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_email_async(subject, message, recipient_list):
    """
    Простая асинхронная отправка email
    """
    print(f"📧 Celery: Отправка email '{subject}' на {recipient_list}")

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        print(f"✅ Email отправлен успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        return False


@shared_task
def send_welcome_email_async(user_email, user_name):
    """
    Отправка приветственного email через Celery
    """
    subject = "Добро пожаловать в нашу систему!"
    message = f"""
    Привет, {user_name}!

    Добро пожаловать в нашу систему закупок.

    Ваш email: {user_email}

    С уважением,
    Команда проекта
    """

    return send_email_async.delay(subject, message, [user_email])


@shared_task
def send_order_email_async(order_id, user_email):
    """
    Отправка email о заказе через Celery
    """
    subject = f"Ваш заказ #{order_id} принят"
    message = f"""
    Ваш заказ #{order_id} успешно принят.

    Мы свяжемся с вами для уточнения деталей.

    Спасибо за покупку!
    """

    return send_email_async.delay(subject, message, [user_email])
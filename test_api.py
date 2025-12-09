import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api/v1/'


def test_registration():
    """Тест регистрации пользователя"""
    data = {
        'email': 'test_buyer@example.com',
        'first_name': 'Тестовый',
        'last_name': 'Покупатель',
        'password': 'password123',
        'password_confirm': 'password123',
        'type': 'buyer'
    }

    response = requests.post(f'{BASE_URL}user/register/', json=data)
    print("=== РЕГИСТРАЦИЯ ===")
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    return response.json().get('Token') if response.status_code == 201 else None


def test_login():
    """Тест входа пользователя"""
    data = {
        'email': 'test_buyer@example.com',
        'password': 'password123'
    }

    response = requests.post(f'{BASE_URL}user/login/', json=data)
    print("\n=== ВХОД ===")
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    return response.json().get('Token') if response.status_code == 200 else None


def test_products(token):
    """Тест получения списка товаров"""
    headers = {'Authorization': f'Token {token}'} if token else {}

    response = requests.get(f'{BASE_URL}products/', headers=headers)
    print("\n=== СПИСОК ТОВАРОВ ===")
    print(f"Статус: {response.status_code}")
    data = response.json()

    # Обрабатываем пагинацию
    if isinstance(data, dict) and 'results' in data:
        products = data['results']
        print(f"Найдено товаров: {len(products)}")
        # Выводим первые 3 товара для информации
        for i, product in enumerate(products[:3]):
            print(f"{i + 1}. {product['product']['name']} - {product['price']} руб.")
        return products[0]['id'] if products else None
    else:
        # Если нет пагинации
        products = data if isinstance(data, list) else []
        print(f"Найдено товаров: {len(products)}")
        for i, product in enumerate(products[:3]):
            print(f"{i + 1}. {product['product']['name']} - {product['price']} руб.")
        return products[0]['id'] if products else None


def test_add_to_cart(token, product_info_id):
    """Тест добавления в корзину"""
    headers = {'Authorization': f'Token {token}'}
    data = {'product_info_id': product_info_id, 'quantity': 2}

    response = requests.post(f'{BASE_URL}basket/add/', json=data, headers=headers)
    print("\n=== ДОБАВЛЕНИЕ В КОРЗИНУ ===")
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")


def test_view_cart(token):
    """Тест просмотра корзины"""
    headers = {'Authorization': f'Token {token}'}

    response = requests.get(f'{BASE_URL}basket/', headers=headers)
    print("\n=== КОРЗИНА ===")
    print(f"Статус: {response.status_code}")
    data = response.json()

    # Обрабатываем пагинацию для корзины
    if isinstance(data, dict) and 'results' in data:
        cart_items = data['results']
    else:
        cart_items = data if isinstance(data, list) else []

    print(f"Товаров в корзине: {len(cart_items)}")
    for item in cart_items:
        product_name = item['product_info']['product']['name']
        quantity = item['quantity']
        print(f"- {product_name} x {quantity}")


def test_contacts(token):
    """Тест работы с контактами"""
    headers = {'Authorization': f'Token {token}'}

    # Добавление контакта
    contact_data = {
        'city': 'Москва',
        'street': 'Тверская',
        'house': '1',
        'phone': '+79991234567'
    }

    response = requests.post(f'{BASE_URL}user/contacts/', json=contact_data, headers=headers)
    print("\n=== ДОБАВЛЕНИЕ КОНТАКТА ===")
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")


def test_orders(token):
    """Тест просмотра заказов"""
    headers = {'Authorization': f'Token {token}'}

    response = requests.get(f'{BASE_URL}orders/', headers=headers)
    print("\n=== ЗАКАЗЫ ===")
    print(f"Статус: {response.status_code}")
    data = response.json()

    # Обрабатываем пагинацию для заказов
    if isinstance(data, dict) and 'results' in data:
        orders = data['results']
    else:
        orders = data if isinstance(data, list) else []

    print(f"Найдено заказов: {len(orders)}")
    for order in orders:
        print(f"- Заказ #{order['id']} - {order['status']}")


if __name__ == '__main__':
    # Запускаем тесты
    print("🚀 ЗАПУСК ТЕСТОВ API...")

    token = test_registration()

    if not token:
        print("Пробуем вход...")
        token = test_login()

    if token:
        print(f"✅ Токен получен: {token[:10]}...")
        product_id = test_products(token)
        if product_id:
            print(f"✅ ID товара для теста: {product_id}")
            test_add_to_cart(token, product_id)
            test_view_cart(token)
            test_contacts(token)
            test_orders(token)
        else:
            print("❌ Нет товаров для теста")
    else:
        print("❌ Не удалось получить токен авторизации")

    print("\n🎯 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
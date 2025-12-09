import requests
import json
import time

BASE_URL = 'http://127.0.0.1:8000/api/v1/'


def get_products_list(data):
    """Извлекаем список товаров из ответа API (с учетом пагинации)"""
    if isinstance(data, dict) and 'results' in data:
        return data['results']
    elif isinstance(data, list):
        return data
    else:
        return []


def test_full_order_scenario():
    """Полный тестовый сценарий заказа"""
    print("🚀 ЗАПУСК ПОЛНОГО СЦЕНАРИЯ ЗАКАЗА...")

    # 1. Вход пользователя
    login_data = {
        'email': 'test_buyer@example.com',
        'password': 'password123'
    }

    response = requests.post(f'{BASE_URL}user/login/', json=login_data)
    if response.status_code != 200:
        print("❌ Ошибка входа")
        return

    token = response.json().get('Token')
    print(f"✅ Пользователь вошел. Токен: {token[:10]}...")

    # 2. Получаем список товаров
    headers = {'Authorization': f'Token {token}'}
    response = requests.get(f'{BASE_URL}products/', headers=headers)
    products_data = response.json()
    products = get_products_list(products_data)

    print(f"✅ Найдено товаров: {len(products)}")

    if len(products) < 2:
        print("❌ Недостаточно товаров для теста")
        return

    # 3. Добавляем несколько товаров в корзину
    for i, product in enumerate(products[:2]):  # первые 2 товара
        cart_data = {
            'product_info_id': product['id'],
            'quantity': i + 1  # разное количество
        }
        response = requests.post(f'{BASE_URL}basket/add/', json=cart_data, headers=headers)
        if response.status_code == 200:
            print(f"✅ Добавлен товар: {product['product']['name']} x {i + 1}")
        else:
            print(f"❌ Ошибка добавления товара: {response.json()}")

    # 4. Проверяем корзину
    response = requests.get(f'{BASE_URL}basket/', headers=headers)
    cart_data = response.json()
    cart_items = get_products_list(cart_data)

    print(f"✅ Товаров в корзине: {len(cart_items)}")
    total_quantity = sum(item['quantity'] for item in cart_items)
    print(f"✅ Общее количество: {total_quantity}")

    # 5. Подтверждаем заказ
    order_data = {'contact_id': 1}
    response = requests.post(f'{BASE_URL}order/confirm/', json=order_data, headers=headers)

    if response.status_code == 200:
        order_result = response.json()
        print(f"🎉 ЗАКАЗ ПОДТВЕРЖДЕН! ID заказа: {order_result.get('OrderId')}")

        # 6. Проверяем список заказов
        response = requests.get(f'{BASE_URL}orders/', headers=headers)
        orders_data = response.json()
        orders = get_products_list(orders_data)
        print(f"✅ Заказов пользователя: {len(orders)}")

        # 7. Проверяем что корзина очистилась
        response = requests.get(f'{BASE_URL}basket/', headers=headers)
        cart_after = response.json()
        cart_items_after = get_products_list(cart_after)
        print(f"✅ Товаров в корзине после заказа: {len(cart_items_after)}")

        # 8. Выводим информацию о заказе
        if orders:
            latest_order = orders[0]
            print(f"📦 Последний заказ: #{latest_order['id']} - {latest_order['status']}")
            print(f"📅 Дата: {latest_order['created_at']}")
            print(f"📍 Адрес: {latest_order['contact']['city']}, {latest_order['contact']['street']}")

    else:
        print(f"❌ Ошибка подтверждения заказа: {response.json()}")

    print("\n🎯 ПОЛНЫЙ СЦЕНАРИЙ ЗАВЕРШЕН")


if __name__ == '__main__':
    test_full_order_scenario()

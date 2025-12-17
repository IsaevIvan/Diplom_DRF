import requests
import time

BASE_URL = 'http://localhost:8000/api/v1/'


def test_register_throttle():
    """Тестирование throttle для регистрации"""
    print("🧪 Тестирование Register Throttle...")

    for i in range(6):  # Пытаемся сделать 6 запросов (лимит 5/час)
        data = {
            'email': f'test_throttle_{i}@example.com',
            'first_name': 'Test',
            'last_name': 'Throttle',
            'password': 'password123',
            'password_confirm': 'password123',
            'type': 'buyer'
        }

        response = requests.post(f'{BASE_URL}user/register/', json=data)

        if response.status_code == 429:  # Too Many Requests
            print(f"   ✅ Запрос {i + 1}: THROTTLED (ожидаемо после 5 попыток)")
            print(f"   Сообщение: {response.json().get('detail', '')}")
            return True
        elif response.status_code == 201:
            print(f"   ✅ Запрос {i + 1}: Успешно")
        else:
            print(f"   ❌ Запрос {i + 1}: Ошибка {response.status_code}")

        time.sleep(0.5)  # Небольшая задержка

    print("   ❌ Throttle не сработал")
    return False


def test_login_throttle():
    """Тестирование throttle для входа"""
    print("\n🧪 Тестирование Login Throttle...")

    # Сначала регистрируем тестового пользователя
    register_data = {
        'email': 'throttle_test@example.com',
        'first_name': 'Throttle',
        'last_name': 'Test',
        'password': 'password123',
        'password_confirm': 'password123',
        'type': 'buyer'
    }

    requests.post(f'{BASE_URL}user/register/', json=register_data)

    # Теперь делаем много попыток входа с неверным паролем
    for i in range(12):  # Лимит 10/час
        login_data = {
            'email': 'throttle_test@example.com',
            'password': 'wrong_password'  # Неверный пароль
        }

        response = requests.post(f'{BASE_URL}user/login/', json=login_data)

        if response.status_code == 429:
            print(f"   ✅ Попытка {i + 1}: THROTTLED (ожидаемо после 10 попыток)")
            print(f"   Сообщение: {response.json().get('detail', '')}")
            return True
        elif response.status_code == 400:
            print(f"   ✅ Попытка {i + 1}: Неверные данные (ожидаемо)")

        time.sleep(0.5)

    print("   ❌ Login throttle не сработал")
    return False


def test_anon_throttle():
    """Тестирование анонимного throttle"""
    print("\n🧪 Тестирование Anonymous Throttle...")

    # Много запросов к публичному endpoint
    for i in range(65):  # Лимит 30/минуту для burst
        response = requests.get(f'{BASE_URL}products/')

        if response.status_code == 429:
            print(f"   ✅ Запрос {i + 1}: THROTTLED (burst limit 30/min)")
            return True
        elif response.status_code == 200:
            if i == 29:
                print(f"   ⚠️  Запрос {i + 1}: Последний перед лимитом")

        time.sleep(0.05)  # Быстрые запросы

    print("   ❌ Burst throttle не сработал")
    return False


if __name__ == '__main__':
    print("🚀 Тестирование DRF Throttling\n")

    # Запуск тестов
    results = [
        test_register_throttle(),
        test_login_throttle(),
        test_anon_throttle()
    ]

    print("\n" + "=" * 50)
    print(f"📊 Результаты: {sum(results)}/3 тестов пройдено")

    if all(results):
        print("🎉 Все throttles работают правильно!")
    else:
        print("⚠️  Некоторые throttles не сработали")
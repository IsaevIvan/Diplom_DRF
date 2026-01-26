# test_redis_connection.py
import redis
import time


def test_redis_connection():
    print("🔍 Тестирование подключения к Redis...")

    try:
        # Подключаемся к Redis
        r = redis.Redis(host='localhost', port=6379, db=1)

        # Тест ping
        if r.ping():
            print("✅ Redis доступен")

            # Тест записи/чтения
            r.set('test_key', 'test_value', ex=10)
            value = r.get('test_key')
            print(f"✅ Запись/чтение работает: {value.decode()}")

            # Проверяем ключи кэша Django
            keys = r.keys('*')
            print(f"✅ Найдено ключей в Redis: {len(keys)}")
            for key in keys[:5]:  # Покажем первые 5
                print(f"  - {key.decode()}")

        else:
            print("❌ Redis не отвечает на ping")

    except Exception as e:
        print(f"❌ Ошибка подключения к Redis: {e}")
Diplom Project DRF - Система автоматизации закупок

Cистема автоматизации бизнес-процессов закупок с REST API, асинхронной обработкой задач и контейнеризацией.

🎯 Основные возможности
🔐 Аутентификация и пользователи
Регистрация с подтверждением email

Вход по токену (Token Authentication)

Два типа пользователей: покупатели (buyer) и поставщики (shop)

Кастомная модель User с email как username

🛍️ Товары и каталог
Иерархия: Категории → Товары → Информация о товарах в магазинах

Фильтрация товаров по категориям и магазинам

Подробная информация о товарах с параметрами

Учет остатков на складе

🛒 Корзина и заказы
Добавление/удаление товаров в корзину

Подтверждение заказов с резервированием товаров

История заказов пользователя

7 статусов заказа: от "В корзине" до "Доставлен"

📧 Email уведомления (асинхронные)
Приветственное письмо после регистрации

Подтверждение заказа

Изменение статуса заказа

Уведомления администратору

🔄 Импорт данных для поставщиков
Загрузка YAML файлов с товарами

Автоматическое создание магазинов, категорий, товаров

Обновление цен и остатков

🏗️ Архитектура
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Клиент        │    │   Django        │    │   PostgreSQL    │
│   (Web/API)     │────│   REST API      │────│   База данных   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              │ RabbitMQ/Redis
                              │
                    ┌─────────────────┐
                    │   Celery        │
                    │   Worker        │
                    └─────────────────┘
                              │
                    ┌─────────────────┐
                    │   Email         │
                    │   Сервис        │
                    └─────────────────┘
🚀 Быстрый старт с Docker
Предварительные требования
Docker и Docker Compose

2 ГБ свободной памяти

Порты 8000, 5432, 6379 свободны

Запуск проекта
Клонировать репозиторий:

bash
git clone <repository-url>
cd Diplom_Django_DRF
Запустить все сервисы:

bash
docker-compose up -d
Применить миграции:

bash
docker-compose exec web python manage.py migrate
Создать суперпользователя:

bash
docker-compose exec web python manage.py createsuperuser
Проверить статус:

bash
docker-compose ps
🔍 Проверка работы
Откройте в браузере:

Главная: http://localhost:8000/

Админка: http://localhost:8000/admin/

API документация: http://localhost:8000/swagger/

ReDoc: http://localhost:8000/redoc/

🐳 Docker сервисы
Проект использует 4 контейнера:

Сервис	Порт	Назначение
web (Django)	8000	Основное приложение, REST API
db (PostgreSQL)	5432	База данных
redis	6379	Брокер сообщений для Celery
celery	-	Асинхронный обработчик задач

Управление Docker
bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Просмотр логов
docker-compose logs -f
docker-compose logs -f web      # Только Django
docker-compose logs -f celery   # Только Celery

# Выполнение команд в контейнере
docker-compose exec web python manage.py <команда>
docker-compose exec web bash    # Войти в контейнер
⚙️ Ручная установка (без Docker)
1. Установка зависимостей
bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
2. Настройка базы данных
bash
# Установите PostgreSQL и создайте базу
sudo apt install postgresql redis
sudo -u postgres psql -c "CREATE DATABASE diplom_db;"
sudo -u postgres psql -c "CREATE USER django_user WITH PASSWORD 'django_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE diplom_db TO django_user;"

# Запустите Redis
redis-server --daemonize yes
3. Настройка переменных окружения
bash
cp .env.example .env
# Отредактируйте .env с вашими настройками
4. Настройка Django
bash
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
5. Запуск сервисов
bash
# Терминал 1: Django
python manage.py runserver

# Терминал 2: Celery Worker
celery -A backend worker --loglevel=info --pool=solo

# Терминал 3: Celery Beat (опционально)
celery -A backend beat --loglevel=info
📚 API Endpoints
🔐 Аутентификация
POST /api/v1/user/register/ - Регистрация пользователя

POST /api/v1/user/login/ - Вход и получение токена

POST /api/v1/user/password/reset/ - Сброс пароля

🛍️ Товары
GET /api/v1/products/ - Список товаров (фильтры: category_id, shop_id)

🛒 Корзина
GET /api/v1/basket/ - Просмотр корзины

POST /api/v1/basket/add/ - Добавить товар в корзину

POST /api/v1/basket/remove/ - Удалить товар из корзины

📋 Контакты
GET /api/v1/user/contacts/ - Список контактов

POST /api/v1/user/contacts/ - Добавить контакт

GET/PUT/DELETE /api/v1/user/contacts/{id}/ - Работа с конкретным контактом

📦 Заказы
GET /api/v1/orders/ - История заказов

POST /api/v1/order/confirm/ - Подтвердить заказ

🏪 Для поставщиков
POST /api/v1/partner/update/ - Импорт товаров через YAML

📧 Email уведомления
Система отправляет 4 типа email через Celery:

Приветственное письмо - после регистрации

Подтверждение заказа - после оформления заказа

Изменение статуса - при изменении статуса заказа

Уведомление администратору - о новом заказе

Важно: Email отправляются асинхронно через Celery, не блокируя основной поток.

📁 Структура проекта
text
Diplom_Django_DRF/
├── backend/                    # Основной проект Django
│   ├── settings.py            # Настройки проекта
│   ├── urls.py                # Корневые URL
│   ├── celery.py              # Конфигурация Celery
│   └── __init__.py
├── procurement/               # Основное приложение
│   ├── models.py             # Все модели данных
│   ├── serializers.py        # Сериализаторы DRF
│   ├── views.py              # View-функции и классы
│   ├── urls.py               # URL приложения
│   ├── services.py           # Логика email уведомлений
│   ├── tasks.py              # Celery задачи
│   ├── admin.py              # Админка Django
│   └── tests.py
├── docker-compose.yml        # Docker Compose конфигурация
├── Dockerfile                # Docker образ
├── requirements.txt          # Зависимости Python
├── .env.example              # Пример переменных окружения
├── manage.py
└── README.md                 

👨‍💻 Автор
Иван Исаев

Email: devdreamer@yandex.com

GitHub: @Isaev_Ivan

🙏 Благодарности
Netology за образовательную программу

Сообщество Django и DRF

Разработчикам Celery и Redis

⭐ Если этот проект был полезен, поставьте звезду на GitHub!

📞 Поддержка
Если у вас есть вопросы или предложения:

Создайте Issue на GitHub

Напишите на email: devdreamer@yandex.com


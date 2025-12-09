# Минимальный Dockerfile для разработки
FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Запуск от обычного пользователя (не root)
RUN useradd -m -u 1000 django && chown -R django:django /app
USER django

EXPOSE 8000
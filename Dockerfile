# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Устанавливаем Python зависимости
RUN pip install --timeout=600 --retries=5 --force-reinstall --prefer-binary poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Копируем исходный код
COPY . .

# Создаем пользователя для безопасности
RUN useradd --create-home --shell /bin/bash bot && \
    chown -R bot:bot /app
USER bot

# Открываем порт (если понадобится для health check)
EXPOSE 8000

# Команда запуска
CMD ["python", "-m", "bot.bot"]

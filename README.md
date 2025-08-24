# Time Tracker Telegram Bot

Телеграм бот для отслеживания времени, проведенного в дипворке (deep work), с базой данных PostgreSQL и автоматическими уведомлениями.

## 🚀 Возможности

- **Отслеживание дипворка**: Нажмите кнопку для начала/остановки сессии
- **Автоматические отчеты**: Ежедневный отчет о времени дипворка в 23:59
- **Подсчет дней жизни**: Утреннее уведомление в 6:00 о количестве прожитых дней
- **Статистика**: Просмотр статистики за день, неделю, месяц
- **База данных**: PostgreSQL для хранения всех данных и аналитики

## 📋 Требования

- Python 3.10+
- PostgreSQL 12+
- Telegram Bot Token

## 🛠 Установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd time_tracker_tg_bot
```

### 2. Создание виртуального окружения

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate  # Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка базы данных PostgreSQL

1. Установите PostgreSQL на вашу систему
2. Создайте пользователя и базу данных:

```sql
CREATE USER time_tracker_user WITH PASSWORD 'your_password';
CREATE DATABASE time_tracker OWNER time_tracker_user;
GRANT ALL PRIVILEGES ON DATABASE time_tracker TO time_tracker_user;
```

### 5. Настройка переменных окружения

Создайте файл `.env` на основе `env_example.txt`:

```bash
cp env_example.txt .env
```

Отредактируйте `.env` файл:

```env
# Telegram Bot Token
TELEGRAM_TOKEN=your_telegram_bot_token_here

# PostgreSQL Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=time_tracker
DB_USER=time_tracker_user
DB_PASSWORD=your_password

# Bot Settings
ADMIN_USER_ID=your_telegram_user_id
TIMEZONE=Europe/Moscow
```

### 6. Получение Telegram Bot Token

1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в `.env` файл

### 7. Получение вашего User ID

1. Найдите @userinfobot в Telegram
2. Отправьте любое сообщение
3. Скопируйте ваш ID в переменную `ADMIN_USER_ID`

## 🚀 Запуск

### Вариант 1: Запуск с Docker (рекомендуется)

#### Предварительные требования
- Docker и Docker Compose установлены
- Файл `.env` настроен

#### Быстрый запуск

**Linux/Mac:**
```bash
chmod +x docker-run.sh
./docker-run.sh
```

**Windows:**
```cmd
docker-run.bat
```

#### Ручной запуск с Docker
```bash
# Сборка и запуск
docker-compose up --build -d

# Просмотр логов
docker-compose logs -f bot

# Остановка
docker-compose down
```

### Вариант 2: Локальный запуск

#### 1. Настройка базы данных

```bash
python setup_database.py
```

#### 2. Запуск бота

```bash
python bot_aiogram.py
```

## 📱 Использование

### Основные команды

- `/start` - Запуск бота и главное меню
- **🎯 Начать дипворк** - Начать отсчет времени
- **⏹ Остановить дипворк** - Остановить сессию и записать время
- **📊 Статистика за сегодня** - Просмотр статистики за день
- **🎂 Установить дату рождения** - Настройка для подсчета дней жизни

### Как работает отслеживание

1. Нажмите "🎯 Начать дипворк" когда начинаете работу
2. Бот начнет отсчет времени
3. Нажмите "⏹ Остановить дипворк" когда закончите
4. Время автоматически запишется в базу данных
5. В 23:59 вы получите отчет о времени за день

### Автоматические уведомления

- **23:59** - Ежедневный отчет о дипворке
- **06:00** - Сообщение о количестве прожитых дней

## 🗄 Структура базы данных

### Таблицы

- **user_birthday** - Дата рождения пользователя
- **deepwork_sessions** - Сессии дипворка
- **daily_stats** - Ежедневная статистика

### Основные поля

```sql
-- Сессии дипворка
CREATE TABLE deepwork_sessions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ежедневная статистика
CREATE TABLE daily_stats (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    date DATE NOT NULL,
    total_minutes INTEGER DEFAULT 0,
    session_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);
```

## 📊 Аналитика

Данные в базе позволяют анализировать:

- Время дипворка по дням/неделям/месяцам
- Продуктивность в разные дни недели
- Тренды и прогресс
- Количество сессий и их длительность

### Примеры SQL запросов

```sql
-- Общее время дипворка за неделю
SELECT 
    DATE_TRUNC('week', date) as week,
    SUM(total_minutes) as total_minutes,
    COUNT(*) as days_with_work
FROM daily_stats 
WHERE user_id = 123456
GROUP BY DATE_TRUNC('week', date)
ORDER BY week DESC;

-- Среднее время дипворка по дням недели
SELECT 
    EXTRACT(DOW FROM date) as day_of_week,
    AVG(total_minutes) as avg_minutes
FROM daily_stats 
WHERE user_id = 123456
GROUP BY EXTRACT(DOW FROM date)
ORDER BY day_of_week;
```

## 🐳 Docker

### Преимущества использования Docker

- **Изолированная среда**: Все зависимости и настройки в контейнерах
- **Простота развертывания**: Один команда для запуска всей инфраструктуры
- **Масштабируемость**: Легко переносить между серверами
- **Управление данными**: Автоматическое создание и настройка базы данных

### Сервисы в Docker Compose

- **postgres**: PostgreSQL 15 с автоматической инициализацией
- **bot**: Time Tracker Bot на aiogram
- **pgadmin**: Веб-интерфейс для управления базой данных

### Переменные окружения для Docker

```env
# Обязательные
TELEGRAM_TOKEN=your_telegram_bot_token_here
ADMIN_USER_ID=your_telegram_user_id

# Опциональные
TIMEZONE=Europe/Moscow
```

### Управление контейнерами

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f bot
docker-compose logs -f postgres

# Остановка
docker-compose down

# Пересборка и запуск
docker-compose up --build -d

# Очистка данных (осторожно!)
docker-compose down -v
```

## 🔧 Настройка

### Изменение времени уведомлений

Отредактируйте файл `bot_aiogram.py`:

```python
def _run_scheduler(self):
    # Отправка отчета о дипворке в 23:59
    schedule.every().day.at("23:59").do(self.send_daily_report)
    # Отправка сообщения о днях жизни в 6:00
    schedule.every().day.at("06:00").do(self.send_birthday_message)
```

### Изменение часового пояса

```env
TIMEZONE=Europe/Moscow
```

## 🐛 Устранение неполадок

### Ошибка подключения к базе данных

1. Проверьте, что PostgreSQL запущен
2. Убедитесь в правильности данных в `.env`
3. Проверьте права доступа пользователя

### Бот не отвечает

1. Проверьте правильность токена в `.env`
2. Убедитесь, что бот не заблокирован
3. Проверьте логи на наличие ошибок

### Планировщик не работает

1. Убедитесь, что бот запущен
2. Проверьте системное время
3. Перезапустите бота

## 📝 Логирование

Бот ведет подробные логи всех операций:

```
2024-01-15 10:30:15 - __main__ - INFO - Бот запущен...
2024-01-15 10:30:16 - database - INFO - Успешно подключились к базе данных
2024-01-15 10:30:16 - database - INFO - Таблицы успешно созданы
```

## 🤝 Разработка

### Структура проекта

```
time_tracker_tg_bot/
├── bot.py                 # Основной файл бота (python-telegram-bot)
├── bot_aiogram.py        # Основной файл бота (aiogram)
├── database.py           # Модуль для работы с базой данных
├── setup_database.py     # Скрипт настройки базы данных
├── requirements.txt      # Зависимости Python
├── .env                  # Переменные окружения
├── env_example.txt       # Пример переменных окружения
├── Dockerfile            # Docker образ для бота
├── docker-compose.yml    # Docker Compose конфигурация
├── init.sql              # Инициализация базы данных
├── docker-run.sh         # Скрипт запуска Docker (Linux/Mac)
├── docker-run.bat        # Скрипт запуска Docker (Windows)
└── README.md            # Документация
```

### Добавление новых функций

1. Создайте новую таблицу в `database.py`
2. Добавьте обработчики в `bot_improved.py`
3. Обновите интерфейс пользователя

## 📄 Лицензия

Этот проект распространяется под лицензией MIT.

## 🆘 Поддержка

При возникновении проблем:

1. Проверьте логи бота
2. Убедитесь в правильности настроек
3. Проверьте документацию PostgreSQL
4. Создайте issue в репозитории

---

**Удачного использования! 🚀**

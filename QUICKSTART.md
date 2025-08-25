# 🚀 Быстрый старт Time Tracker Bot

## ⚡ За 5 минут к работающему боту

### 1. 📋 Предварительные требования

- Docker и Docker Compose установлены
- Telegram аккаунт

### 2. 🔑 Получение Telegram Bot Token

1. Найдите @BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. **Сохраните токен!**

### 3. 🆔 Получение вашего User ID

1. Найдите @userinfobot в Telegram
2. Отправьте любое сообщение
3. **Сохраните ваш ID!**

### 4. ⚙️ Настройка

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd time_tracker_tg_bot

# Создайте .env файл
cp env_example.txt .env

# Отредактируйте .env
nano .env  # или любой текстовый редактор
```

**Содержимое .env:**
```env
TELEGRAM_TOKEN=ваш_токен_здесь
ADMIN_USER_ID=ваш_id_здесь
TIMEZONE=Europe/Moscow
```

### 5. 🚀 Запуск

**Linux/Mac:**
```bash
chmod +x docker-run.sh
./docker-run.sh
```

**Windows:**
```cmd
docker-run.bat
```

**Вручную:**
```bash
docker-compose up --build -d
```

**Локальный запуск (без Docker):**
```bash
# Настройка БД
python setup_db.py

# Запуск бота
python main.py
```

### 6. ✅ Проверка

```bash
# Статус контейнеров
docker-compose ps

# Логи бота
docker-compose logs -f bot
```

### 7. 🎯 Тестирование

1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Нажмите "🎯 Начать дипворк"
4. Подождите немного
5. Нажмите "⏹ Остановить дипворк"

## 🌐 Доступные сервисы

- **Бот**: Работает в Telegram
- **PostgreSQL**: `localhost:5432`
- **pgAdmin**: `http://localhost:5050` (admin@timetracker.com / admin123)

## 🛑 Остановка

```bash
docker-compose down
```

## 🔄 Перезапуск

```bash
docker-compose restart
```

## 📊 Мониторинг

```bash
# Логи в реальном времени
docker-compose logs -f

# Использование ресурсов
docker stats

# Статус сервисов
docker-compose ps
```

## 🆘 Если что-то не работает

1. **Проверьте .env файл**
   ```bash
   cat .env
   ```

2. **Проверьте логи**
   ```bash
   docker-compose logs bot
   docker-compose logs postgres
   ```

3. **Перезапустите**
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

4. **Проверьте Docker**
   ```bash
   docker --version
   docker-compose --version
   ```

## 📱 Использование бота

### Основные команды

- `/start` - Главное меню
- 🎯 **Начать дипворк** - Начать отсчет времени
- ⏹ **Остановить дипворк** - Завершить сессию
- 📊 **Статистика за сегодня** - Просмотр статистики
- 🎂 **Установить дату рождения** - Настройка для подсчета дней

### Автоматические уведомления

- **23:59** - Ежедневный отчет о дипворке
- **06:00** - Сообщение о количестве прожитых дней

## 🎯 Цели

- **Минимум**: 2 часа дипворка в день
- **Цель**: 4-6 часов дипворка в день
- **Отлично**: 6+ часов дипворка в день

## 📈 Аналитика

Откройте pgAdmin (`http://localhost:5050`) и используйте SQL запросы из `analytics_examples.sql` для детального анализа вашей продуктивности.

---

**🎉 Готово! Ваш Time Tracker Bot работает!**

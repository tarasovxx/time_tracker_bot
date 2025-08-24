# 🚀 Руководство по развертыванию Time Tracker Bot

## 📋 Обзор

Это руководство поможет вам развернуть Time Tracker Bot с использованием Docker и PostgreSQL. Бот будет отслеживать время дипворка и отправлять автоматические уведомления.

## 🎯 Варианты развертывания

### 1. Локальное развертывание (для разработки)
- Бот и база данных запускаются на вашем компьютере
- Подходит для тестирования и разработки

### 2. Docker развертывание (рекомендуется)
- Все сервисы в контейнерах
- Простота управления и переноса
- Изолированная среда

### 3. Серверное развертывание
- Бот работает на удаленном сервере
- Постоянная доступность
- Возможность масштабирования

## 🐳 Docker развертывание

### Предварительные требования

1. **Установите Docker**
   ```bash
   # Ubuntu/Debian
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   
   # macOS
   brew install --cask docker
   
   # Windows
   # Скачайте Docker Desktop с официального сайта
   ```

2. **Установите Docker Compose**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install docker-compose-plugin
   
   # macOS (уже включен в Docker Desktop)
   # Windows (уже включен в Docker Desktop)
   ```

### Шаги развертывания

#### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd time_tracker_tg_bot
```

#### 2. Настройка переменных окружения
```bash
# Скопируйте пример файла
cp env_example.txt .env

# Отредактируйте .env файл
nano .env
```

**Содержимое .env файла:**
```env
# Telegram Bot Token (обязательно)
TELEGRAM_TOKEN=your_telegram_bot_token_here

# Ваш Telegram User ID (обязательно)
ADMIN_USER_ID=123456789

# Часовой пояс (опционально)
TIMEZONE=Europe/Moscow
```

#### 3. Получение Telegram Bot Token
1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям
4. Скопируйте полученный токен в `.env`

#### 4. Получение вашего User ID
1. Найдите @userinfobot в Telegram
2. Отправьте любое сообщение
3. Скопируйте ваш ID в `ADMIN_USER_ID`

#### 5. Запуск с Docker
```bash
# Сделайте скрипт исполняемым (Linux/Mac)
chmod +x docker-run.sh

# Запустите
./docker-run.sh

# Или вручную
docker-compose up --build -d
```

#### 6. Проверка работы
```bash
# Статус контейнеров
docker-compose ps

# Логи бота
docker-compose logs -f bot

# Логи базы данных
docker-compose logs -f postgres
```

## 🌐 Доступные сервисы

После успешного запуска:

- **PostgreSQL**: `localhost:5432`
  - База данных: `time_tracker`
  - Пользователь: `time_tracker_user`
  - Пароль: `time_tracker_password`

- **pgAdmin**: `http://localhost:5050`
  - Email: `admin@timetracker.com`
  - Пароль: `admin123`

## 🔧 Управление

### Основные команды Docker

```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Просмотр логов
docker-compose logs -f [service_name]

# Обновление и пересборка
docker-compose up --build -d

# Очистка (удаляет все данные!)
docker-compose down -v
```

### Управление данными

```bash
# Резервное копирование базы данных
docker exec time_tracker_postgres pg_dump -U time_tracker_user time_tracker > backup.sql

# Восстановление из резервной копии
docker exec -i time_tracker_postgres psql -U time_tracker_user time_tracker < backup.sql

# Просмотр размера данных
docker exec time_tracker_postgres du -sh /var/lib/postgresql/data
```

## 🚀 Серверное развертывание

### Требования к серверу

- **ОС**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM**: Минимум 2GB, рекомендуется 4GB+
- **Диск**: Минимум 10GB свободного места
- **Сеть**: Доступ к интернету для Telegram API

### Установка на сервере

#### 1. Подключение к серверу
```bash
ssh user@your-server-ip
```

#### 2. Установка Docker
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo apt install docker-compose-plugin

# Перезагрузка сессии
exit
ssh user@your-server-ip
```

#### 3. Клонирование и настройка
```bash
# Клонирование
git clone <repository-url>
cd time_tracker_tg_bot

# Настройка .env
cp env_example.txt .env
nano .env

# Запуск
./docker-run.sh
```

#### 4. Настройка автозапуска
```bash
# Создание systemd сервиса
sudo nano /etc/systemd/system/time-tracker-bot.service
```

**Содержимое файла:**
```ini
[Unit]
Description=Time Tracker Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/user/time_tracker_tg_bot
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
# Активация сервиса
sudo systemctl enable time-tracker-bot
sudo systemctl start time-tracker-bot
```

## 📊 Мониторинг и логирование

### Логи

```bash
# Логи бота
docker-compose logs -f bot

# Логи базы данных
docker-compose logs -f postgres

# Все логи
docker-compose logs -f
```

### Мониторинг ресурсов

```bash
# Использование ресурсов контейнерами
docker stats

# Статус сервисов
docker-compose ps

# Проверка здоровья
docker-compose exec postgres pg_isready -U time_tracker_user
```

### Алерты и уведомления

Бот автоматически отправляет:
- **23:59** - Ежедневный отчет о дипворке
- **06:00** - Сообщение о количестве прожитых дней

## 🔒 Безопасность

### Рекомендации

1. **Измените пароли по умолчанию**
   ```bash
   # В docker-compose.yml измените пароли
   POSTGRES_PASSWORD: your_secure_password
   PGADMIN_DEFAULT_PASSWORD: your_secure_password
   ```

2. **Ограничьте доступ к портам**
   ```bash
   # Настройте firewall
   sudo ufw allow 22    # SSH
   sudo ufw allow 5432  # PostgreSQL (только для локального доступа)
   sudo ufw enable
   ```

3. **Регулярные обновления**
   ```bash
   # Обновление образов
   docker-compose pull
   docker-compose up -d
   ```

## 🐛 Устранение неполадок

### Частые проблемы

#### 1. Бот не отвечает
```bash
# Проверьте токен
docker-compose logs bot | grep "TELEGRAM_TOKEN"

# Проверьте права пользователя
docker-compose exec bot id
```

#### 2. Ошибки подключения к базе данных
```bash
# Проверьте статус PostgreSQL
docker-compose exec postgres pg_isready

# Проверьте логи
docker-compose logs postgres
```

#### 3. Планировщик не работает
```bash
# Проверьте системное время
docker-compose exec bot date

# Проверьте логи планировщика
docker-compose logs bot | grep "scheduler"
```

### Восстановление после сбоя

```bash
# Полная перезагрузка
docker-compose down
docker-compose up --build -d

# Проверка статуса
docker-compose ps
docker-compose logs -f
```

## 📈 Масштабирование

### Горизонтальное масштабирование

```bash
# Запуск нескольких экземпляров бота
docker-compose up --scale bot=3 -d

# Балансировка нагрузки (требует настройки nginx)
```

### Вертикальное масштабирование

```yaml
# В docker-compose.yml
services:
  bot:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

## 🔄 Обновления

### Обновление бота

```bash
# Остановка
docker-compose down

# Получение обновлений
git pull origin main

# Пересборка и запуск
docker-compose up --build -d
```

### Обновление базы данных

```bash
# Создание резервной копии
docker exec time_tracker_postgres pg_dump -U time_tracker_user time_tracker > backup_$(date +%Y%m%d_%H%M%S).sql

# Обновление
docker-compose down
docker-compose up --build -d
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `docker-compose logs -f`
2. Убедитесь в правильности настроек в `.env`
3. Проверьте статус контейнеров: `docker-compose ps`
4. Создайте issue в репозитории

---

**Удачного развертывания! 🚀**

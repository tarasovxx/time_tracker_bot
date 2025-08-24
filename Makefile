.PHONY: help install setup run test clean docker-build docker-up docker-down docker-logs

help: ## Показать справку
	@echo "🚀 Time Tracker Bot - Команды управления"
	@echo "========================================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	@echo "📦 Установка зависимостей..."
	poetry install

setup: ## Настроить базу данных
	@echo "🗄️ Настройка базы данных..."
	python setup_db.py

run: ## Запустить бота локально
	@echo "🤖 Запуск бота..."
	python run_bot.py

test: ## Запустить тесты
	@echo "🧪 Запуск тестов..."
	python -m pytest

clean: ## Очистить временные файлы
	@echo "🧹 Очистка временных файлов..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

docker-build: ## Собрать Docker образ
	@echo "🐳 Сборка Docker образа..."
	docker-compose build

docker-up: ## Запустить Docker контейнеры
	@echo "🚀 Запуск Docker контейнеров..."
	docker-compose up -d

docker-down: ## Остановить Docker контейнеры
	@echo "🛑 Остановка Docker контейнеров..."
	docker-compose down

docker-logs: ## Показать логи Docker контейнеров
	@echo "📝 Логи Docker контейнеров..."
	docker-compose logs -f

docker-restart: ## Перезапустить Docker контейнеры
	@echo "🔄 Перезапуск Docker контейнеров..."
	docker-compose restart

docker-clean: ## Очистить Docker (удалить все контейнеры и образы)
	@echo "🧹 Очистка Docker..."
	docker-compose down -v --remove-orphans
	docker system prune -f

dev: ## Запуск в режиме разработки
	@echo "🔧 Запуск в режиме разработки..."
	poetry run python run_bot.py

prod: ## Запуск в продакшн режиме (Docker)
	@echo "🚀 Запуск в продакшн режиме..."
	docker-compose up -d --build

status: ## Показать статус сервисов
	@echo "📊 Статус сервисов..."
	docker-compose ps

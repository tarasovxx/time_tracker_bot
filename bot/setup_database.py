#!/usr/bin/env python3
"""
Скрипт для настройки базы данных PostgreSQL для Time Tracker Bot
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def create_database():
    """Создание базы данных если она не существует"""
    try:
        # Подключаемся к postgres для создания новой базы данных
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database='postgres',
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        conn.autocommit = True
        
        with conn.cursor() as cursor:
            # Проверяем существование базы данных
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (os.getenv('DB_NAME', 'time_tracker'),))
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(f"CREATE DATABASE {os.getenv('DB_NAME', 'time_tracker')}")
                print(f"✅ База данных '{os.getenv('DB_NAME', 'time_tracker')}' успешно создана")
            else:
                print(f"ℹ️ База данных '{os.getenv('DB_NAME', 'time_tracker')}' уже существует")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании базы данных: {e}")
        return False

def test_connection():
    """Тестирование подключения к базе данных"""
    try:
        from .database import Database
        db = Database()
        print("✅ Подключение к базе данных успешно")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return False

def main():
    """Основная функция"""
    print("🚀 Настройка базы данных для Time Tracker Bot")
    print("=" * 50)
    
    # Проверяем переменные окружения
    required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")
        print("Пожалуйста, создайте файл .env на основе env_example.txt")
        return
    
    print("📋 Переменные окружения:")
    print(f"   Host: {os.getenv('DB_HOST')}")
    print(f"   Port: {os.getenv('DB_PORT', '5432')}")
    print(f"   Database: {os.getenv('DB_NAME')}")
    print(f"   User: {os.getenv('DB_USER')}")
    print()
    
    # Создаем базу данных
    if create_database():
        print("✅ База данных готова")
        
        # Тестируем подключение
        if test_connection():
            print("🎉 Настройка завершена успешно!")
            print("\nТеперь вы можете запустить бота командой: python bot.py")
        else:
            print("❌ Проблема с подключением к базе данных")
    else:
        print("❌ Не удалось настроить базу данных")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Скрипт для тестирования импортов
"""

import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Тестирование всех импортов"""
    try:
        print("🧪 Тестирование импортов...")
        
        # Тест импорта базы данных
        print("  📊 Импорт database...")
        from bot.database import Database
        print("    ✅ Database импортирован успешно")
        
        # Тест импорта бота
        print("  🤖 Импорт bot...")
        from bot.bot import TimeTrackerBot
        print("    ✅ TimeTrackerBot импортирован успешно")
        
        # Тест импорта setup_database
        print("  🗄️ Импорт setup_database...")
        from bot.setup_database import create_database, test_connection
        print("    ✅ setup_database импортирован успешно")
        
        print("\n🎉 Все импорты работают корректно!")
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)

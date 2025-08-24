#!/usr/bin/env python3
"""
Скрипт для запуска Time Tracker Bot локально
"""

import asyncio
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot import TimeTrackerBot

async def main():
    """Основная функция"""
    try:
        bot = TimeTrackerBot()
        await bot.start()
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Запуск Time Tracker Bot...")
    asyncio.run(main())

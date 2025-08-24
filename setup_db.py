#!/usr/bin/env python3
"""
Скрипт для настройки базы данных PostgreSQL для Time Tracker Bot
"""

import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.setup_database import main

if __name__ == "__main__":
    main()

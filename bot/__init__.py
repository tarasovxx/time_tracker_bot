"""
Time Tracker Bot - Telegram bot for tracking deep work sessions
"""

from .bot import TimeTrackerBot
from .database import Database

__version__ = "0.1.0"
__author__ = "Tarasov Artem"
__email__ = "almtara550@gmail.com"

__all__ = ["TimeTrackerBot", "Database"]

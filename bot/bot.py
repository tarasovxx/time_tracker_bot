import os
import logging
import asyncio
import schedule
import time
import threading
from datetime import datetime, date
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from .database import Database

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TimeTrackerBot:
    def __init__(self):
        self.db = Database()
        self.timezone = os.getenv('TIMEZONE', 'Europe/Moscow')
        self.bot = None
        self.dp = None
        
        # Словарь для хранения активных сессий пользователей
        self.active_sessions = {}
        
        # Запускаем планировщик задач в отдельном потоке
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
    
    def _run_scheduler(self):
        """Запуск планировщика задач"""
        # Отправка отчета о дипворке в 23:59
        schedule.every().day.at("23:59").do(self._send_daily_report_sync)
        # Отправка сообщения о днях жизни в 6:00
        schedule.every().day.at("06:00").do(self._send_birthday_message_sync)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def _send_daily_report_sync(self):
        """Синхронная отправка ежедневного отчета (для планировщика)"""
        if self.bot:
            asyncio.create_task(self.send_daily_report())
    
    def _send_birthday_message_sync(self):
        """Синхронная отправка сообщения о днях жизни (для планировщика)"""
        if self.bot:
            asyncio.create_task(self.send_birthday_message())
    
    async def start_command(self, message: types.Message):
        """Обработчик команды /start"""
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="🎯 Начать дипворк", callback_data="start_deepwork"))
        keyboard.add(InlineKeyboardButton(text="⏹ Остановить дипворк", callback_data="stop_deepwork"))
        keyboard.row()
        keyboard.add(InlineKeyboardButton(text="📊 Статистика за сегодня", callback_data="today_stats"))
        keyboard.add(InlineKeyboardButton(text="🎂 Установить дату рождения", callback_data="set_birthday"))
        
        await message.answer(
            "🚀 Добро пожаловать в Time Tracker Bot!\n\n"
            "Этот бот поможет вам отслеживать время, проведенное в дипворке.\n\n"
            "Выберите действие:",
            reply_markup=keyboard.as_markup()
        )
    
    async def button_callback(self, callback: types.CallbackQuery):
        """Обработчик нажатий на кнопки"""
        await callback.answer()
        
        if callback.data == "start_deepwork":
            await self.start_deepwork(callback)
        elif callback.data == "stop_deepwork":
            await self.stop_deepwork(callback)
        elif callback.data == "today_stats":
            await self.show_today_stats(callback)
        elif callback.data == "set_birthday":
            await self.ask_birthday(callback)
        elif callback.data == "back_to_main":
            await self.back_to_main(callback)
    
    async def start_deepwork(self, callback: types.CallbackQuery):
        """Начало сессии дипворка"""
        user_id = callback.from_user.id
        
        # Проверяем, есть ли уже активная сессия
        if user_id in self.active_sessions:
            keyboard = InlineKeyboardBuilder()
            keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"))
            
            await callback.message.edit_text(
                "⚠️ У вас уже есть активная сессия дипворка!\n"
                "Сначала остановите текущую сессию.",
                reply_markup=keyboard.as_markup()
            )
            return
        
        # Создаем новую сессию в базе данных
        session_id = self.db.start_session(user_id)
        if session_id:
            self.active_sessions[user_id] = session_id
            start_time = datetime.now().strftime("%H:%M")
            
            keyboard = InlineKeyboardBuilder()
            keyboard.add(InlineKeyboardButton(text="⏹ Остановить дипворк", callback_data="stop_deepwork"))
            keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"))
            
            await callback.message.edit_text(
                f"🎯 Сессия дипворка началась в {start_time}\n\n"
                "Время идет... ⏰\n"
                "Нажмите 'Остановить дипворк' когда закончите.",
                reply_markup=keyboard.as_markup()
            )
        else:
            await callback.message.edit_text("❌ Ошибка при создании сессии. Попробуйте еще раз.")
    
    async def stop_deepwork(self, callback: types.CallbackQuery):
        """Остановка сессии дипворка"""
        user_id = callback.from_user.id
        
        if user_id not in self.active_sessions:
            keyboard = InlineKeyboardBuilder()
            keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"))
            
            await callback.message.edit_text(
                "⚠️ У вас нет активной сессии дипворка.\n"
                "Сначала начните новую сессию.",
                reply_markup=keyboard.as_markup()
            )
            return
        
        session_id = self.active_sessions[user_id]
        
        # Завершаем сессию в базе данных
        if self.db.end_session(session_id):
            # Получаем статистику за сегодня
            stats = self.db.get_today_stats(user_id)
            
            # Удаляем сессию из активных
            del self.active_sessions[user_id]
            
            keyboard = InlineKeyboardBuilder()
            keyboard.add(InlineKeyboardButton(text="🎯 Начать дипворк", callback_data="start_deepwork"))
            keyboard.add(InlineKeyboardButton(text="📊 Статистика за сегодня", callback_data="today_stats"))
            keyboard.row()
            keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"))
            
            await callback.message.edit_text(
                f"✅ Сессия дипворка завершена!\n\n"
                f"📊 Статистика за сегодня:\n"
                f"⏱ Общее время: {stats['hours']}ч {stats['minutes']}м\n"
                f"🔄 Количество сессий: {stats['session_count']}\n\n"
                "Отличная работа! 🎉",
                reply_markup=keyboard.as_markup()
            )
        else:
            await callback.message.edit_text("❌ Ошибка при завершении сессии. Попробуйте еще раз.")
    
    async def show_today_stats(self, callback: types.CallbackQuery):
        """Показать статистику за сегодня"""
        user_id = callback.from_user.id
        stats = self.db.get_today_stats(user_id)
        
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="🎯 Начать дипворк", callback_data="start_deepwork"))
        keyboard.add(InlineKeyboardButton(text="⏹ Остановить дипворк", callback_data="stop_deepwork"))
        keyboard.row()
        keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"))
        
        await callback.message.edit_text(
            f"📊 Статистика за сегодня ({date.today().strftime('%d.%m.%Y')}):\n\n"
            f"⏱ Общее время дипворка: {stats['hours']}ч {stats['minutes']}м\n"
            f"🔄 Количество сессий: {stats['session_count']}\n\n"
            f"Цель: 4-6 часов дипворка в день 🎯",
            reply_markup=keyboard.as_markup()
        )
    
    async def ask_birthday(self, callback: types.CallbackQuery):
        """Запрос даты рождения"""
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"))
        
        await callback.message.edit_text(
            "🎂 Пожалуйста, отправьте вашу дату рождения в формате ДД.ММ.ГГГГ\n\n"
            "Например: 15.03.1990\n\n"
            "Это нужно для подсчета количества прожитых дней.",
            reply_markup=keyboard.as_markup()
        )
    
    async def handle_birthday_input(self, message: types.Message):
        """Обработка введенной даты рождения"""
        user_id = message.from_user.id

        try:
            # Парсим дату рождения
            birthday_str = message.text
            birthday = datetime.strptime(birthday_str, "%d.%m.%Y").date()
            
            # Сохраняем в базу данных
            if self.db.set_user_birthday(user_id, birthday):
                # Вычисляем количество прожитых дней
                days_lived = (date.today() - birthday).days
                
                keyboard = InlineKeyboardBuilder()
                keyboard.add(InlineKeyboardButton(text="🎯 Начать дипворк", callback_data="start_deepwork"))
                keyboard.add(InlineKeyboardButton(text="📊 Статистика за сегодня", callback_data="today_stats"))
                keyboard.row()
                keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"))
                
                await message.answer(
                    f"✅ Дата рождения успешно установлена!\n\n"
                    f"🎂 Ваш день рождения: {birthday.strftime('%d.%m.%Y')}\n"
                    f"🌍 Вы прожили на этой планете: {days_lived} дней\n\n"
                    "Теперь каждое утро в 6:00 вы будете получать обновление о количестве прожитых дней!",
                    reply_markup=keyboard.as_markup()
                )
            else:
                await message.answer("❌ Ошибка при сохранении даты рождения. Попробуйте еще раз.")
                
        except ValueError:
            await message.answer(
                "❌ Неверный формат даты. Используйте формат ДД.ММ.ГГГГ\n"
                "Например: 15.03.1990"
            )
    
    async def back_to_main(self, callback: types.CallbackQuery):
        """Возврат к главному меню"""
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="🎯 Начать дипворк", callback_data="start_deepwork"))
        keyboard.add(InlineKeyboardButton(text="⏹ Остановить дипворк", callback_data="stop_deepwork"))
        keyboard.row()
        keyboard.add(InlineKeyboardButton(text="📊 Статистика за сегодня", callback_data="today_stats"))
        keyboard.add(InlineKeyboardButton(text="🎂 Установить дату рождения", callback_data="set_birthday"))
        
        await callback.message.edit_text(
            "🚀 Главное меню Time Tracker Bot\n\n"
            "Выберите действие:",
            reply_markup=keyboard.as_markup()
        )
    
    async def send_daily_report(self):
        """Отправка ежедневного отчета о дипворке"""
        if not self.admin_user_id or not self.bot:
            return
        
        try:
            stats = self.db.get_today_stats(self.admin_user_id)
            
            if stats['total_minutes'] > 0:
                message = (
                    f"📊 Ежедневный отчет о дипворке\n"
                    f"📅 {date.today().strftime('%d.%m.%Y')}\n\n"
                    f"⏱ Общее время: {stats['hours']}ч {stats['minutes']}м\n"
                    f"🔄 Количество сессий: {stats['session_count']}\n\n"
                )
                
                # Оценка продуктивности
                if stats['total_minutes'] >= 240:  # 4+ часов
                    message += "🎉 Отличный день! Вы достигли цели!"
                elif stats['total_minutes'] >= 180:  # 3+ часов
                    message += "👍 Хороший результат! Продолжайте в том же духе!"
                elif stats['total_minutes'] >= 120:  # 2+ часов
                    message += "👌 Неплохо! Завтра постарайтесь больше."
                else:
                    message += "💪 Завтра новый день! Поставьте цель и достигните её!"
                
                await self.bot.send_message(chat_id=self.admin_user_id, text=message)
                logger.info("Ежедневный отчет отправлен")
        except Exception as e:
            logger.error(f"Ошибка отправки ежедневного отчета: {e}")
    
    async def send_birthday_message(self):
        """Отправка сообщения о количестве прожитых дней"""
        if not self.admin_user_id or not self.bot:
            return
        
        try:
            birthday = self.db.get_user_birthday(self.admin_user_id)
            if birthday:
                days_lived = (date.today() - birthday).days
                message = (
                    f"🌅 Доброе утро!\n\n"
                    f"🎂 Сегодня вы прожили на этой планете: {days_lived} дней\n\n"
                    f"💫 Каждый новый день - это возможность стать лучше!\n"
                    f"🎯 Начните день с дипворка и достигните своих целей!"
                )
                
                await self.bot.send_message(chat_id=self.admin_user_id, text=message)
                logger.info("Сообщение о днях жизни отправлено")
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения о днях жизни: {e}")
    
    async def start(self):
        """Запуск бота"""
        # Получаем токен бота
        token = os.getenv('TELEGRAM_TOKEN')
        if not token:
            logger.error("TELEGRAM_TOKEN не найден в переменных окружения!")
            return
        
        # Создаем бота и диспетчер
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        
        # Регистрируем обработчики
        self.dp.message.register(self.start_command, Command("start"))
        self.dp.callback_query.register(self.button_callback)
        self.dp.message.register(self.handle_birthday_input, F.text)
        
        # Запускаем бота
        logger.info("Бот запущен...")
        await self.dp.start_polling(self.bot)

async def main():
    """Основная функция"""
    bot = TimeTrackerBot()
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())

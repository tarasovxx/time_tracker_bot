import psycopg2
import psycopg2.extras
from datetime import datetime, date
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.conn = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Подключение к базе данных PostgreSQL"""
        try:
            self.conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'time_tracker'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD')
            )
            print("Успешно подключились к базе данных")
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")
            raise
    
    def create_tables(self):
        """Создание необходимых таблиц"""
        try:
            with self.conn.cursor() as cursor:
                # Таблица для хранения даты рождения пользователя
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_birthday (
                        user_id BIGINT PRIMARY KEY,
                        birthday DATE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Таблица для хранения сессий дипворка
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS deepwork_sessions (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL,
                        start_time TIMESTAMP NOT NULL,
                        end_time TIMESTAMP,
                        duration_minutes INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Таблица для ежедневной статистики
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS daily_stats (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL,
                        date DATE NOT NULL,
                        total_minutes INTEGER DEFAULT 0,
                        session_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, date)
                    )
                """)
                
                self.conn.commit()
                print("Таблицы успешно созданы")
        except Exception as e:
            print(f"Ошибка создания таблиц: {e}")
            self.conn.rollback()
    
    def set_user_birthday(self, user_id: int, birthday: date):
        """Установка даты рождения пользователя"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO user_birthday (user_id, birthday) 
                    VALUES (%s, %s) 
                    ON CONFLICT (user_id) 
                    DO UPDATE SET birthday = EXCLUDED.birthday
                """, (user_id, birthday))
                self.conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка установки даты рождения: {e}")
            self.conn.rollback()
            return False
    
    def get_user_birthday(self, user_id: int) -> date:
        """Получение даты рождения пользователя"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT birthday FROM user_birthday WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Ошибка получения даты рождения: {e}")
            return None
    
    def start_session(self, user_id: int) -> int:
        """Начало новой сессии дипворка"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO deepwork_sessions (user_id, start_time) 
                    VALUES (%s, %s) RETURNING id
                """, (user_id, datetime.now()))
                session_id = cursor.fetchone()[0]
                self.conn.commit()
                return session_id
        except Exception as e:
            print(f"Ошибка начала сессии: {e}")
            self.conn.rollback()
            return None
    
    def end_session(self, session_id: int) -> bool:
        """Завершение сессии дипворка"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE deepwork_sessions 
                    SET end_time = %s, duration_minutes = EXTRACT(EPOCH FROM (%s - start_time)) / 60
                    WHERE id = %s
                """, (datetime.now(), datetime.now(), session_id))
                
                # Обновляем ежедневную статистику
                cursor.execute("""
                    SELECT user_id, duration_minutes FROM deepwork_sessions WHERE id = %s
                """, (session_id,))
                result = cursor.fetchone()
                if result:
                    user_id, duration = result[0], result[1]
                    self._update_daily_stats(user_id, duration)
                
                self.conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка завершения сессии: {e}")
            self.conn.rollback()
            return False
    
    def _update_daily_stats(self, user_id: int, duration_minutes: int):
        """Обновление ежедневной статистики"""
        try:
            today = date.today()
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO daily_stats (user_id, date, total_minutes, session_count) 
                    VALUES (%s, %s, %s, 1)
                    ON CONFLICT (user_id, date) 
                    DO UPDATE SET 
                        total_minutes = daily_stats.total_minutes + EXCLUDED.total_minutes,
                        session_count = daily_stats.session_count + 1
                """, (user_id, today, duration_minutes))
        except Exception as e:
            print(f"Ошибка обновления статистики: {e}")
    
    def get_today_stats(self, user_id: int) -> dict:
        """Получение статистики за сегодня"""
        try:
            today = date.today()
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT total_minutes, session_count 
                    FROM daily_stats 
                    WHERE user_id = %s AND date = %s
                """, (user_id, today))
                result = cursor.fetchone()
                
                if result:
                    total_minutes, session_count = result
                    hours = total_minutes // 60
                    minutes = total_minutes % 60
                    return {
                        'total_minutes': total_minutes,
                        'hours': hours,
                        'minutes': minutes,
                        'session_count': session_count
                    }
                return {'total_minutes': 0, 'hours': 0, 'minutes': 0, 'session_count': 0}
        except Exception as e:
            print(f"Ошибка получения статистики: {e}")
            return {'total_minutes': 0, 'hours': 0, 'minutes': 0, 'session_count': 0}
    
    def get_active_session(self, user_id: int) -> int:
        """Получение активной сессии пользователя"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id FROM deepwork_sessions 
                    WHERE user_id = %s AND end_time IS NULL
                    ORDER BY start_time DESC LIMIT 1
                """, (user_id,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Ошибка получения активной сессии: {e}")
            return None
    
    def close(self):
        """Закрытие соединения с базой данных"""
        if self.conn:
            self.conn.close()

-- Инициализация базы данных Time Tracker Bot
-- Этот файл выполняется автоматически при первом запуске PostgreSQL контейнера

-- Создание расширений
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Создание таблиц
CREATE TABLE IF NOT EXISTS user_birthday (
    user_id BIGINT PRIMARY KEY,
    birthday DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS deepwork_sessions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS daily_stats (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    date DATE NOT NULL,
    total_minutes INTEGER DEFAULT 0,
    session_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

-- Создание индексов для оптимизации
CREATE INDEX IF NOT EXISTS idx_deepwork_sessions_user_id ON deepwork_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_deepwork_sessions_start_time ON deepwork_sessions(start_time);
CREATE INDEX IF NOT EXISTS idx_deepwork_sessions_end_time ON deepwork_sessions(end_time);
CREATE INDEX IF NOT EXISTS idx_daily_stats_user_id ON daily_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON daily_stats(date);

-- Создание триггеров для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_birthday_updated_at 
    BEFORE UPDATE ON user_birthday 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_deepwork_sessions_updated_at 
    BEFORE UPDATE ON deepwork_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_stats_updated_at 
    BEFORE UPDATE ON daily_stats 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Создание представления для удобного просмотра статистики
CREATE OR REPLACE VIEW weekly_stats AS
SELECT 
    user_id,
    DATE_TRUNC('week', date) as week_start,
    DATE_TRUNC('week', date) + INTERVAL '6 days' as week_end,
    SUM(total_minutes) as total_minutes,
    SUM(session_count) as total_sessions,
    COUNT(*) as days_with_work,
    ROUND(AVG(total_minutes), 2) as avg_minutes_per_day
FROM daily_stats 
GROUP BY user_id, DATE_TRUNC('week', date)
ORDER BY week_start DESC;

CREATE OR REPLACE VIEW monthly_stats AS
SELECT 
    user_id,
    DATE_TRUNC('month', date) as month_start,
    DATE_TRUNC('month', date) + INTERVAL '1 month - 1 day' as month_end,
    SUM(total_minutes) as total_minutes,
    SUM(session_count) as total_sessions,
    COUNT(*) as days_with_work,
    ROUND(AVG(total_minutes), 2) as avg_minutes_per_day
FROM daily_stats 
GROUP BY user_id, DATE_TRUNC('month', date)
ORDER BY month_start DESC;

-- Создание пользователя и предоставление прав (если не существует)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'time_tracker_user') THEN
        CREATE USER time_tracker_user WITH PASSWORD 'time_tracker_password';
    END IF;
END
$$;

-- Предоставление прав на базу данных
GRANT ALL PRIVILEGES ON DATABASE time_tracker TO time_tracker_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO time_tracker_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO time_tracker_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO time_tracker_user;

-- Предоставление прав на будущие таблицы
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO time_tracker_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO time_tracker_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO time_tracker_user;

-- Логирование успешной инициализации
INSERT INTO pg_stat_statements_info (dealloc) VALUES (1);

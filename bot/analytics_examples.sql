-- 📊 Примеры SQL запросов для аналитики Time Tracker Bot
-- Используйте эти запросы в pgAdmin или любом SQL клиенте

-- =====================================================
-- 🎯 ОСНОВНАЯ СТАТИСТИКА
-- =====================================================

-- Общее время дипворка за все время
SELECT 
    user_id,
    SUM(total_minutes) as total_minutes,
    ROUND(SUM(total_minutes) / 60.0, 2) as total_hours,
    SUM(session_count) as total_sessions,
    COUNT(*) as total_days
FROM daily_stats 
GROUP BY user_id;

-- Статистика за текущий месяц
SELECT 
    DATE_TRUNC('month', date) as month,
    SUM(total_minutes) as total_minutes,
    ROUND(SUM(total_minutes) / 60.0, 2) as total_hours,
    SUM(session_count) as total_sessions,
    COUNT(*) as days_with_work,
    ROUND(AVG(total_minutes), 2) as avg_minutes_per_day
FROM daily_stats 
WHERE DATE_TRUNC('month', date) = DATE_TRUNC('month', CURRENT_DATE)
GROUP BY DATE_TRUNC('month', date);

-- Статистика за текущую неделю
SELECT 
    DATE_TRUNC('week', date) as week_start,
    DATE_TRUNC('week', date) + INTERVAL '6 days' as week_end,
    SUM(total_minutes) as total_minutes,
    ROUND(SUM(total_minutes) / 60.0, 2) as total_hours,
    SUM(session_count) as total_sessions,
    COUNT(*) as days_with_work,
    ROUND(AVG(total_minutes), 2) as avg_minutes_per_day
FROM daily_stats 
WHERE DATE_TRUNC('week', date) = DATE_TRUNC('week', CURRENT_DATE)
GROUP BY DATE_TRUNC('week', date);

-- =====================================================
-- 📈 ТРЕНДЫ И ПРОГРЕСС
-- =====================================================

-- Прогресс по неделям (последние 12 недель)
SELECT 
    DATE_TRUNC('week', date) as week_start,
    DATE_TRUNC('week', date) + INTERVAL '6 days' as week_end,
    SUM(total_minutes) as total_minutes,
    ROUND(SUM(total_minutes) / 60.0, 2) as total_hours,
    COUNT(*) as days_with_work,
    ROUND(AVG(total_minutes), 2) as avg_minutes_per_day
FROM daily_stats 
WHERE date >= CURRENT_DATE - INTERVAL '12 weeks'
GROUP BY DATE_TRUNC('week', date)
ORDER BY week_start DESC;

-- Прогресс по месяцам (последние 12 месяцев)
SELECT 
    DATE_TRUNC('month', date) as month_start,
    DATE_TRUNC('month', date) + INTERVAL '1 month - 1 day' as month_end,
    SUM(total_minutes) as total_minutes,
    ROUND(SUM(total_minutes) / 60.0, 2) as total_hours,
    COUNT(*) as days_with_work,
    ROUND(AVG(total_minutes), 2) as avg_minutes_per_day
FROM daily_stats 
WHERE date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', date)
ORDER BY month_start DESC;

-- Сравнение с предыдущим периодом
WITH current_period AS (
    SELECT 
        SUM(total_minutes) as total_minutes,
        COUNT(*) as days_count
    FROM daily_stats 
    WHERE date >= DATE_TRUNC('week', CURRENT_DATE)
),
previous_period AS (
    SELECT 
        SUM(total_minutes) as total_minutes,
        COUNT(*) as days_count
    FROM daily_stats 
    WHERE date >= DATE_TRUNC('week', CURRENT_DATE - INTERVAL '1 week')
    AND date < DATE_TRUNC('week', CURRENT_DATE)
)
SELECT 
    cp.total_minutes as current_minutes,
    ROUND(cp.total_minutes / 60.0, 2) as current_hours,
    pp.total_minutes as previous_minutes,
    ROUND(pp.total_minutes / 60.0, 2) as previous_hours,
    CASE 
        WHEN pp.total_minutes > 0 THEN 
            ROUND(((cp.total_minutes - pp.total_minutes) / pp.total_minutes::float) * 100, 2)
        ELSE NULL 
    END as change_percent
FROM current_period cp
CROSS JOIN previous_period pp;

-- =====================================================
-- 🗓️ АНАЛИЗ ПО ДНЯМ НЕДЕЛИ
-- =====================================================

-- Продуктивность по дням недели
SELECT 
    EXTRACT(DOW FROM date) as day_of_week,
    CASE EXTRACT(DOW FROM date)
        WHEN 0 THEN 'Воскресенье'
        WHEN 1 THEN 'Понедельник'
        WHEN 2 THEN 'Вторник'
        WHEN 3 THEN 'Среда'
        WHEN 4 THEN 'Четверг'
        WHEN 5 THEN 'Пятница'
        WHEN 6 THEN 'Суббота'
    END as day_name,
    COUNT(*) as days_count,
    SUM(total_minutes) as total_minutes,
    ROUND(SUM(total_minutes) / 60.0, 2) as total_hours,
    ROUND(AVG(total_minutes), 2) as avg_minutes,
    ROUND(AVG(total_minutes) / 60.0, 2) as avg_hours
FROM daily_stats 
GROUP BY EXTRACT(DOW FROM date)
ORDER BY day_of_week;

-- Лучшие и худшие дни недели
WITH day_stats AS (
    SELECT 
        EXTRACT(DOW FROM date) as day_of_week,
        CASE EXTRACT(DOW FROM date)
            WHEN 0 THEN 'Воскресенье'
            WHEN 1 THEN 'Понедельник'
            WHEN 2 THEN 'Вторник'
            WHEN 3 THEN 'Среда'
            WHEN 4 THEN 'Четверг'
            WHEN 5 THEN 'Пятница'
            WHEN 6 THEN 'Суббота'
        END as day_name,
        AVG(total_minutes) as avg_minutes
    FROM daily_stats 
    GROUP BY EXTRACT(DOW FROM date)
)
SELECT 
    day_name,
    ROUND(avg_minutes, 2) as avg_minutes,
    ROUND(avg_minutes / 60.0, 2) as avg_hours,
    CASE 
        WHEN avg_minutes = (SELECT MAX(avg_minutes) FROM day_stats) THEN '🏆 Лучший'
        WHEN avg_minutes = (SELECT MIN(avg_minutes) FROM day_stats) THEN '⚠️ Худший'
        ELSE '📊 Средний'
    END as performance
FROM day_stats
ORDER BY avg_minutes DESC;

-- =====================================================
-- 🎯 ЦЕЛИ И ДОСТИЖЕНИЯ
-- =====================================================

-- Дни, когда достигнута цель (4+ часов дипворка)
SELECT 
    date,
    total_minutes,
    ROUND(total_minutes / 60.0, 2) as hours,
    session_count,
    CASE 
        WHEN total_minutes >= 240 THEN '🎉 Отлично!'
        WHEN total_minutes >= 180 THEN '👍 Хорошо'
        WHEN total_minutes >= 120 THEN '👌 Неплохо'
        ELSE '💪 Можно лучше'
    END as achievement
FROM daily_stats 
WHERE total_minutes > 0
ORDER BY date DESC;

-- Процент дней, когда достигнута цель
SELECT 
    COUNT(CASE WHEN total_minutes >= 240 THEN 1 END) as days_with_goal,
    COUNT(*) as total_days,
    ROUND(
        (COUNT(CASE WHEN total_minutes >= 240 THEN 1 END)::float / COUNT(*)) * 100, 
        2
    ) as goal_percentage
FROM daily_stats 
WHERE total_minutes > 0;

-- Текущая серия дней с достижением цели
WITH goal_days AS (
    SELECT 
        date,
        total_minutes,
        CASE WHEN total_minutes >= 240 THEN 1 ELSE 0 END as goal_achieved
    FROM daily_stats 
    WHERE total_minutes > 0
    ORDER BY date DESC
),
streak AS (
    SELECT 
        date,
        goal_achieved,
        SUM(CASE WHEN goal_achieved = 0 THEN 1 ELSE 0 END) 
            OVER (ORDER BY date DESC) as streak_group
    FROM goal_days
)
SELECT 
    COUNT(*) as current_streak_days
FROM streak 
WHERE streak_group = 0;

-- =====================================================
-- 📊 ДЕТАЛЬНАЯ АНАЛИТИКА СЕССИЙ
-- =====================================================

-- Статистика по длительности сессий
SELECT 
    CASE 
        WHEN duration_minutes < 30 THEN 'Короткие (< 30 мин)'
        WHEN duration_minutes < 60 THEN 'Средние (30-60 мин)'
        WHEN duration_minutes < 120 THEN 'Длинные (1-2 часа)'
        WHEN duration_minutes < 240 THEN 'Очень длинные (2-4 часа)'
        ELSE 'Марафонские (4+ часа)'
    END as session_type,
    COUNT(*) as session_count,
    ROUND(AVG(duration_minutes), 2) as avg_duration,
    ROUND(MIN(duration_minutes), 2) as min_duration,
    ROUND(MAX(duration_minutes), 2) as max_duration
FROM deepwork_sessions 
WHERE duration_minutes IS NOT NULL
GROUP BY 
    CASE 
        WHEN duration_minutes < 30 THEN 'Короткие (< 30 мин)'
        WHEN duration_minutes < 60 THEN 'Средние (30-60 мин)'
        WHEN duration_minutes < 120 THEN 'Длинные (1-2 часа)'
        WHEN duration_minutes < 240 THEN 'Очень длинные (2-4 часа)'
        ELSE 'Марафонские (4+ часа)'
    END
ORDER BY avg_duration DESC;

-- Время начала сессий по часам
SELECT 
    EXTRACT(HOUR FROM start_time) as hour,
    COUNT(*) as session_count,
    ROUND(AVG(duration_minutes), 2) as avg_duration
FROM deepwork_sessions 
WHERE duration_minutes IS NOT NULL
GROUP BY EXTRACT(HOUR FROM start_time)
ORDER BY hour;

-- Самые продуктивные часы
SELECT 
    EXTRACT(HOUR FROM start_time) as hour,
    COUNT(*) as session_count,
    SUM(duration_minutes) as total_minutes,
    ROUND(SUM(duration_minutes) / 60.0, 2) as total_hours,
    ROUND(AVG(duration_minutes), 2) as avg_duration
FROM deepwork_sessions 
WHERE duration_minutes IS NOT NULL
GROUP BY EXTRACT(HOUR FROM start_time)
ORDER BY total_minutes DESC;

-- =====================================================
-- 🔄 СРАВНЕНИЯ И БЕНЧМАРКИ
-- =====================================================

-- Сравнение с предыдущими периодами
WITH period_comparison AS (
    SELECT 
        CASE 
            WHEN date >= CURRENT_DATE - INTERVAL '7 days' THEN 'Текущая неделя'
            WHEN date >= CURRENT_DATE - INTERVAL '14 days' THEN 'Предыдущая неделя'
            WHEN date >= CURRENT_DATE - INTERVAL '21 days' THEN '2 недели назад'
            WHEN date >= CURRENT_DATE - INTERVAL '28 days' THEN '3 недели назад'
        END as period,
        SUM(total_minutes) as total_minutes,
        COUNT(*) as days_count
    FROM daily_stats 
    WHERE date >= CURRENT_DATE - INTERVAL '28 days'
    GROUP BY 
        CASE 
            WHEN date >= CURRENT_DATE - INTERVAL '7 days' THEN 'Текущая неделя'
            WHEN date >= CURRENT_DATE - INTERVAL '14 days' THEN 'Предыдущая неделя'
            WHEN date >= CURRENT_DATE - INTERVAL '21 days' THEN '2 недели назад'
            WHEN date >= CURRENT_DATE - INTERVAL '28 days' THEN '3 недели назад'
        END
)
SELECT 
    period,
    total_minutes,
    ROUND(total_minutes / 60.0, 2) as total_hours,
    days_count,
    ROUND(total_minutes / days_count, 2) as avg_minutes_per_day
FROM period_comparison
ORDER BY 
    CASE period
        WHEN 'Текущая неделя' THEN 1
        WHEN 'Предыдущая неделя' THEN 2
        WHEN '2 недели назад' THEN 3
        WHEN '3 недели назад' THEN 4
    END;

-- =====================================================
-- 📈 ПРОГНОЗЫ И РЕКОМЕНДАЦИИ
-- =====================================================

-- Прогноз на следующую неделю (на основе средних значений)
SELECT 
    'Прогноз на следующую неделю' as info,
    ROUND(AVG(total_minutes) * 7, 2) as predicted_minutes,
    ROUND(AVG(total_minutes) * 7 / 60.0, 2) as predicted_hours,
    ROUND(AVG(session_count) * 7, 2) as predicted_sessions
FROM daily_stats 
WHERE date >= CURRENT_DATE - INTERVAL '4 weeks';

-- Рекомендации по улучшению
SELECT 
    CASE 
        WHEN avg_daily < 120 THEN '💪 Увеличьте время дипворка до 2+ часов в день'
        WHEN avg_daily < 240 THEN '👍 Хорошо! Стремитесь к 4+ часам в день'
        WHEN avg_daily < 360 THEN '🎉 Отлично! Вы на правильном пути'
        ELSE '🏆 Превосходно! Вы мастер дипворка!'
    END as recommendation,
    ROUND(avg_daily, 2) as current_avg_minutes,
    ROUND(avg_daily / 60.0, 2) as current_avg_hours
FROM (
    SELECT AVG(total_minutes) as avg_daily
    FROM daily_stats 
    WHERE date >= CURRENT_DATE - INTERVAL '2 weeks'
) as stats;

-- =====================================================
-- 🎨 СОЗДАНИЕ ОТЧЕТОВ
-- =====================================================

-- Еженедельный отчет
CREATE OR REPLACE VIEW weekly_report AS
SELECT 
    DATE_TRUNC('week', date) as week_start,
    DATE_TRUNC('week', date) + INTERVAL '6 days' as week_end,
    SUM(total_minutes) as total_minutes,
    ROUND(SUM(total_minutes) / 60.0, 2) as total_hours,
    SUM(session_count) as total_sessions,
    COUNT(*) as days_with_work,
    ROUND(AVG(total_minutes), 2) as avg_minutes_per_day,
    COUNT(CASE WHEN total_minutes >= 240 THEN 1 END) as days_with_goal,
    ROUND(
        (COUNT(CASE WHEN total_minutes >= 240 THEN 1 END)::float / COUNT(*)) * 100, 
        2
    ) as goal_percentage
FROM daily_stats 
GROUP BY DATE_TRUNC('week', date)
ORDER BY week_start DESC;

-- Месячный отчет
CREATE OR REPLACE VIEW monthly_report AS
SELECT 
    DATE_TRUNC('month', date) as month_start,
    DATE_TRUNC('month', date) + INTERVAL '1 month - 1 day' as month_end,
    SUM(total_minutes) as total_minutes,
    ROUND(SUM(total_minutes) / 60.0, 2) as total_hours,
    SUM(session_count) as total_sessions,
    COUNT(*) as days_with_work,
    ROUND(AVG(total_minutes), 2) as avg_minutes_per_day,
    COUNT(CASE WHEN total_minutes >= 240 THEN 1 END) as days_with_goal,
    ROUND(
        (COUNT(CASE WHEN total_minutes >= 240 THEN 1 END)::float / COUNT(*)) * 100, 
        2
    ) as goal_percentage
FROM daily_stats 
GROUP BY DATE_TRUNC('month', date)
ORDER BY month_start DESC;

-- =====================================================
-- 🔍 ПОЛЕЗНЫЕ ЗАПРОСЫ ДЛЯ ОТЛАДКИ
-- =====================================================

-- Проверка целостности данных
SELECT 
    'Сессии без времени окончания' as issue,
    COUNT(*) as count
FROM deepwork_sessions 
WHERE end_time IS NULL
UNION ALL
SELECT 
    'Сессии с отрицательной длительностью' as issue,
    COUNT(*) as count
FROM deepwork_sessions 
WHERE duration_minutes < 0
UNION ALL
SELECT 
    'Дни без статистики' as issue,
    COUNT(*) as count
FROM generate_series(
    CURRENT_DATE - INTERVAL '30 days', 
    CURRENT_DATE, 
    '1 day'::interval
)::date as date
LEFT JOIN daily_stats ds ON ds.date = date
WHERE ds.date IS NULL;

-- Статистика по пользователям
SELECT 
    ub.user_id,
    ub.birthday,
    (CURRENT_DATE - ub.birthday) as days_lived,
    COUNT(ds.date) as tracking_days,
    SUM(ds.total_minutes) as total_minutes,
    ROUND(SUM(ds.total_minutes) / 60.0, 2) as total_hours
FROM user_birthday ub
LEFT JOIN daily_stats ds ON ub.user_id = ds.user_id
GROUP BY ub.user_id, ub.birthday;

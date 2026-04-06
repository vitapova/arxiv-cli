"""
Утилиты для работы с датами

Функции:
- parse_date(str) - парсинг строки с датой в datetime
- format_date(date) - форматирование даты для вывода
- get_date_range(days) - получение диапазона дат (от X дней назад до сегодня)
"""

from datetime import datetime, timedelta
from dateutil import parser


def parse_date(date_str):
    """
    Парсинг строки с датой.
    
    Args:
        date_str: строка с датой
        
    Returns:
        datetime: объект даты
    """
    # TODO: реализация
    pass


def format_date(date, format='%Y-%m-%d'):
    """
    Форматирование даты.
    
    Args:
        date: объект datetime
        format: формат вывода
        
    Returns:
        str: отформатированная дата
    """
    # TODO: реализация
    pass


def get_date_range(days):
    """
    Получение диапазона дат.
    
    Args:
        days: количество дней назад
        
    Returns:
        tuple: (start_date, end_date)
    """
    # TODO: реализация
    pass

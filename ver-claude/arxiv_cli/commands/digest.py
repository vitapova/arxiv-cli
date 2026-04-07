"""
Команда digest - формирование дайджеста новых публикаций

Параметры:
- period: период (day/week/month)
- category: категории для фильтрации
- query: ключевые слова для поиска
- format: формат вывода (text/markdown)
"""

from datetime import datetime, timedelta
from collections import defaultdict
from arxiv_cli.api.client import ArxivClient
from arxiv_cli.commands.search import search_articles


def get_period_dates(period):
    """
    Преобразовать период в диапазон дат.
    
    Args:
        period: day, week, month
        
    Returns:
        tuple: (date_from, date_to) в формате YYYY-MM-DD
    """
    now = datetime.now()
    
    if period == 'day':
        delta = timedelta(days=1)
    elif period == 'week':
        delta = timedelta(days=7)
    elif period == 'month':
        delta = timedelta(days=30)
    else:
        delta = timedelta(days=7)  # По умолчанию неделя
    
    date_from = (now - delta).strftime('%Y-%m-%d')
    date_to = now.strftime('%Y-%m-%d')
    
    return date_from, date_to


def group_by_category(entries):
    """
    Группировка статей по категориям.
    
    Args:
        entries: список статей
        
    Returns:
        dict: {category: [entries]}
    """
    grouped = defaultdict(list)
    
    for entry in entries:
        primary = entry.get('primary_category', 'unknown')
        grouped[primary].append(entry)
    
    return dict(grouped)


def get_statistics(entries):
    """
    Статистика по категориям.
    
    Args:
        entries: список статей
        
    Returns:
        dict: статистика
    """
    category_counts = defaultdict(int)
    
    for entry in entries:
        for cat in entry.get('categories', []):
            category_counts[cat] += 1
    
    return {
        'total': len(entries),
        'by_category': dict(sorted(category_counts.items(), key=lambda x: -x[1]))
    }


def create_digest(period='week', categories=None, query='', max_results=50):
    """
    Создание дайджеста новых публикаций.
    
    Args:
        period: период (day/week/month)
        categories: список категорий для фильтрации
        query: ключевые слова для поиска
        max_results: максимальное количество результатов
        
    Returns:
        dict: дайджест с данными
    """
    # Определяем период
    date_from, date_to = get_period_dates(period)
    
    # Формируем поисковый запрос
    if not query and not categories:
        # Если ничего не указано, ищем по всем категориям за период
        query = 'all:*'
    
    # Выполняем поиск
    results = search_articles(
        query=query,
        max_results=max_results,
        sort_by='submittedDate',
        sort_order='descending',
        categories=categories,
        date_from=date_from,
        date_to=date_to
    )
    
    entries = results['entries']
    
    # Группируем по категориям
    grouped = group_by_category(entries)
    
    # Статистика
    stats = get_statistics(entries)
    
    return {
        'period': period,
        'date_from': date_from,
        'date_to': date_to,
        'total': stats['total'],
        'entries': entries,
        'grouped': grouped,
        'statistics': stats
    }

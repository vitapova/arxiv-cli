"""
Команда search - поиск статей в arXiv

Параметры:
- query: поисковый запрос (авторы, ключевые слова, категории)
- from/to: диапазон дат
- max: максимальное количество результатов
- sort: сортировка (relevance/date)
"""

from arxiv_cli.api.client import ArxivClient, ArxivAPIError
from arxiv_cli.api.parser import parse_search_results


def build_search_query(query, categories=None, authors=None, title=None, date_from=None, date_to=None):
    """
    Построение поискового запроса для arXiv API.
    
    Args:
        query: базовый поисковый запрос
        categories: список категорий для фильтрации
        authors: список авторов для фильтрации
        title: поиск в названии
        date_from: начальная дата (YYYY-MM-DD)
        date_to: конечная дата (YYYY-MM-DD)
        
    Returns:
        str: сформированный запрос
    """
    parts = []
    
    # Базовый запрос (поиск везде)
    if query:
        parts.append(f'all:{query}')
    
    # Фильтр по категории
    if categories:
        cat_query = ' OR '.join([f'cat:{cat}' for cat in categories])
        parts.append(f'({cat_query})')
    
    # Фильтр по автору
    if authors:
        auth_query = ' OR '.join([f'au:{auth}' for auth in authors])
        parts.append(f'({auth_query})')
    
    # Поиск в названии
    if title:
        parts.append(f'ti:{title}')
    
    # Фильтр по датам (используем submittedDate)
    if date_from and date_to:
        # Формат YYYYMMDD0000 для arXiv API
        from_str = date_from.replace('-', '') + '0000'
        to_str = date_to.replace('-', '') + '2359'
        parts.append(f'submittedDate:[{from_str} TO {to_str}]')
    elif date_from:
        from_str = date_from.replace('-', '') + '0000'
        parts.append(f'submittedDate:[{from_str} TO 99991231235959]')
    elif date_to:
        to_str = date_to.replace('-', '') + '2359'
        parts.append(f'submittedDate:[19910101000000 TO {to_str}]')
    
    return ' AND '.join(parts) if parts else 'all:*'


def search_articles(query, max_results=10, sort_by='relevance', sort_order='descending',
                   categories=None, authors=None, title=None, start=0, 
                   date_from=None, date_to=None, verbose=False):
    """
    Поиск статей в arXiv.
    
    Args:
        query: поисковый запрос
        max_results: максимальное количество результатов
        sort_by: сортировка (relevance, lastUpdatedDate, submittedDate)
        sort_order: порядок (ascending, descending)
        categories: список категорий для фильтрации
        authors: список авторов для фильтрации
        title: поиск в названии
        start: смещение для пагинации
        date_from: начальная дата (YYYY-MM-DD)
        date_to: конечная дата (YYYY-MM-DD)
        verbose: выводить информацию о повторах
        
    Returns:
        dict: результаты поиска с метаданными
    """
    client = ArxivClient()
    
    # Формируем запрос
    search_query = build_search_query(query, categories, authors, title, date_from, date_to)
    
    # Выполняем поиск
    xml = client.search(
        query=search_query,
        start=start,
        max_results=max_results,
        sort_by=sort_by,
        sort_order=sort_order,
        verbose=verbose
    )
    
    # Парсим результаты
    results = parse_search_results(xml)
    
    return results

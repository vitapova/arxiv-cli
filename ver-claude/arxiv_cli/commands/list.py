"""
Команда list - вывод локальной библиотеки статей

Параметры:
- status: фильтр по статусу (read/unread/starred)
- category: фильтр по категории
- tag: фильтр по тегам
- search: полнотекстовый поиск
- sort: сортировка
"""

from arxiv_cli.utils.library import get_entries, update_status, toggle_starred


def list_library(status=None, category=None, tags=None, search_query=None, 
                 starred=None, sort_by='added_at', sort_order='desc'):
    """
    Вывод библиотеки с фильтрацией и сортировкой.
    
    Args:
        status: фильтр по статусу (read/unread)
        category: фильтр по категории
        tags: фильтр по тегам
        search_query: поиск по названию/аннотации
        starred: фильтр по избранным
        sort_by: поле сортировки
        sort_order: порядок сортировки
        
    Returns:
        list: отфильтрованные статьи
    """
    # Специальная обработка status='starred'
    if status == 'starred':
        starred = True
        status = None
    
    entries = get_entries(
        category=category,
        tags=tags,
        status=status,
        starred=starred,
        search_query=search_query,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return entries


def mark_as_read(arxiv_id):
    """Отметить статью как прочитанную."""
    update_status(arxiv_id, 'read')


def mark_as_unread(arxiv_id):
    """Отметить статью как непрочитанную."""
    update_status(arxiv_id, 'unread')


def toggle_star(arxiv_id):
    """Переключить избранное для статьи."""
    return toggle_starred(arxiv_id)

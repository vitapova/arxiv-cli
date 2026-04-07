"""
Команда track - отслеживание версий статей

Подкоманды:
- add: добавить статью в отслеживание
- remove: убрать из отслеживания
- update: проверить обновления
- versions: показать историю версий
- list: показать все отслеживаемые статьи
"""

from arxiv_cli.utils.tracking import (
    add_to_tracking,
    remove_from_tracking,
    check_for_updates,
    get_version_history,
    get_tracked_entries
)


def track_add(arxiv_id, tags=None):
    """
    Добавить статью в отслеживание.
    
    Args:
        arxiv_id: идентификатор статьи
        tags: теги для статьи
        
    Returns:
        dict: данные статьи
    """
    return add_to_tracking(arxiv_id, tags=tags)


def track_remove(arxiv_id):
    """
    Убрать статью из отслеживания.
    
    Args:
        arxiv_id: идентификатор статьи
        
    Returns:
        bool: успешно ли убрано
    """
    return remove_from_tracking(arxiv_id)


def track_update(arxiv_id=None):
    """
    Проверить обновления отслеживаемых статей.
    
    Args:
        arxiv_id: проверить конкретную статью (опционально)
        
    Returns:
        list: список обновлений
    """
    return check_for_updates(arxiv_id=arxiv_id)


def track_versions(arxiv_id):
    """
    Показать историю версий статьи.
    
    Args:
        arxiv_id: идентификатор статьи
        
    Returns:
        dict: данные статьи с историей или None
    """
    return get_version_history(arxiv_id)


def track_list():
    """
    Показать все отслеживаемые статьи.
    
    Returns:
        list: отслеживаемые статьи
    """
    return get_tracked_entries()

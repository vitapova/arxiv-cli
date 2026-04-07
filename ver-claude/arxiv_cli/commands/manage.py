"""
Команды управления библиотекой: add, remove, info

- add: добавить статью в библиотеку без скачивания PDF
- remove: удалить статью из библиотеки
- info: показать детальную информацию о статье
"""

from arxiv_cli.api.client import ArxivClient, ArxivAPIError
from arxiv_cli.api.parser import parse_search_results
from arxiv_cli.utils.library import add_entry, remove_entry, get_entry, add_tags, remove_tags


def add_to_library(arxiv_id, tags=None, status='unread'):
    """
    Добавить статью в библиотеку без скачивания PDF.
    
    Args:
        arxiv_id: идентификатор статьи
        tags: список тегов
        status: статус статьи (read/unread)
        
    Returns:
        dict: данные добавленной статьи
    """
    client = ArxivClient()
    
    # Получаем метаданные статьи
    xml = client.get_by_id(arxiv_id)
    results = parse_search_results(xml)
    
    if not results['entries']:
        raise ArxivAPIError(f'Статья {arxiv_id} не найдена')
    
    entry = results['entries'][0]
    
    # Добавляем в библиотеку
    add_entry(entry, tags=tags, status=status)
    
    return entry


def remove_from_library(arxiv_id):
    """
    Удалить статью из библиотеки.
    
    Args:
        arxiv_id: идентификатор статьи
        
    Returns:
        bool: True если удалена, False если не найдена
    """
    return remove_entry(arxiv_id)


def get_info(arxiv_id, from_library=False):
    """
    Получить информацию о статье.
    
    Args:
        arxiv_id: идентификатор статьи
        from_library: получить из библиотеки или из API
        
    Returns:
        dict: данные статьи
    """
    if from_library:
        entry = get_entry(arxiv_id)
        if not entry:
            raise ArxivAPIError(f'Статья {arxiv_id} не найдена в библиотеке')
        return entry
    else:
        # Получаем из API
        client = ArxivClient()
        xml = client.get_by_id(arxiv_id)
        results = parse_search_results(xml)
        
        if not results['entries']:
            raise ArxivAPIError(f'Статья {arxiv_id} не найдена')
        
        return results['entries'][0]


def manage_tags(arxiv_id, add=None, remove=None):
    """
    Управление тегами статьи.
    
    Args:
        arxiv_id: идентификатор статьи
        add: теги для добавления
        remove: теги для удаления
    """
    if add:
        add_tags(arxiv_id, add)
    
    if remove:
        remove_tags(arxiv_id, remove)

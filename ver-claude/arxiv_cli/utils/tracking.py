"""
Отслеживание версий статей

Функциональность:
- Добавление статьи в отслеживание
- Проверка обновлений
- История версий
"""

from datetime import datetime
from arxiv_cli.api.client import ArxivClient, ArxivAPIError
from arxiv_cli.api.parser import parse_search_results
from arxiv_cli.utils.library import load_library, save_library, get_entry, add_entry


def add_to_tracking(arxiv_id, tags=None):
    """
    Добавить статью в отслеживание.
    
    Args:
        arxiv_id: идентификатор статьи
        tags: теги для статьи
        
    Returns:
        dict: данные статьи
    """
    client = ArxivClient()
    
    # Получаем метаданные
    xml = client.get_by_id(arxiv_id)
    results = parse_search_results(xml)
    
    if not results['entries']:
        raise ArxivAPIError(f'Статья {arxiv_id} не найдена')
    
    entry = results['entries'][0]
    
    # Добавляем поля отслеживания
    entry['tracked'] = True
    entry['version_history'] = [{
        'id': entry['id'],
        'updated': entry['updated'],
        'checked_at': datetime.now().isoformat(),
        'is_new': True
    }]
    
    # Добавляем в библиотеку
    add_entry(entry, tags=tags)
    
    return entry


def remove_from_tracking(arxiv_id):
    """
    Убрать статью из отслеживания.
    
    Args:
        arxiv_id: идентификатор статьи
        
    Returns:
        bool: успешно ли убрано
    """
    library = load_library()
    
    for entry in library['entries']:
        if entry['id'] == arxiv_id or entry['id'].startswith(arxiv_id.split('v')[0]):
            entry['tracked'] = False
            save_library(library)
            return True
    
    return False


def get_tracked_entries():
    """
    Получить все отслеживаемые статьи.
    
    Returns:
        list: отслеживаемые статьи
    """
    library = load_library()
    return [e for e in library['entries'] if e.get('tracked', False)]


def check_for_updates(arxiv_id=None):
    """
    Проверить обновления для отслеживаемых статей.
    
    Args:
        arxiv_id: проверить конкретную статью (опционально)
        
    Returns:
        list: список обновлённых статей (id, old_version, new_version)
    """
    library = load_library()
    client = ArxivClient()
    updates = []
    
    # Список статей для проверки
    if arxiv_id:
        entries = [e for e in library['entries'] if e['id'].startswith(arxiv_id.split('v')[0])]
    else:
        entries = [e for e in library['entries'] if e.get('tracked', False)]
    
    for entry in entries:
        # Получаем базовый ID без версии
        base_id = entry['id'].split('v')[0].rstrip('v')
        
        try:
            # Запрашиваем свежие данные
            xml = client.get_by_id(base_id)
            results = parse_search_results(xml)
            
            if not results['entries']:
                continue
            
            new_entry = results['entries'][0]
            
            # Сравниваем версии или даты обновления
            old_updated = entry['updated']
            new_updated = new_entry['updated']
            
            if new_updated > old_updated:
                # Найдено обновление!
                old_version = entry['id']
                new_version = new_entry['id']
                
                # Обновляем метаданные в библиотеке
                for key in ['title', 'authors', 'abstract', 'categories', 'primary_category', 'updated']:
                    entry[key] = new_entry[key]
                
                # Обновляем ID на новую версию
                entry['id'] = new_version
                
                # Добавляем в историю
                if 'version_history' not in entry:
                    entry['version_history'] = []
                
                entry['version_history'].append({
                    'id': new_version,
                    'updated': new_updated,
                    'checked_at': datetime.now().isoformat(),
                    'is_new': True
                })
                
                updates.append({
                    'base_id': base_id,
                    'old_version': old_version,
                    'new_version': new_version,
                    'old_date': old_updated[:10],
                    'new_date': new_updated[:10],
                    'title': entry['title']
                })
        
        except ArxivAPIError:
            continue
    
    if updates:
        save_library(library)
    
    return updates


def get_version_history(arxiv_id):
    """
    Получить историю версий статьи.
    
    Args:
        arxiv_id: идентификатор статьи
        
    Returns:
        dict: данные статьи с историей или None
    """
    library = load_library()
    
    # Ищем статью по базовому ID
    base_id = arxiv_id.split('v')[0].rstrip('v')
    
    for entry in library['entries']:
        if entry['id'].startswith(base_id):
            return entry
    
    return None

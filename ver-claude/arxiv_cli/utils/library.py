"""
Управление библиотекой статей

Хранение метаданных скачанных статей для экспорта.
Файл библиотеки: ~/.arxiv-cli/library.json
"""

import json
import os
from pathlib import Path
from datetime import datetime


LIBRARY_FILE = Path.home() / '.arxiv-cli' / 'library.json'


def ensure_library_dir():
    """Создание директории библиотеки если не существует."""
    LIBRARY_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_library():
    """
    Загрузка библиотеки статей.
    
    Returns:
        dict: библиотека с метаданными статей
    """
    ensure_library_dir()
    
    if not LIBRARY_FILE.exists():
        return {'entries': [], 'updated': None}
    
    with open(LIBRARY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_library(library):
    """
    Сохранение библиотеки.
    
    Args:
        library: dict с метаданными
    """
    ensure_library_dir()
    
    library['updated'] = datetime.now().isoformat()
    
    with open(LIBRARY_FILE, 'w', encoding='utf-8') as f:
        json.dump(library, f, indent=2, ensure_ascii=False)


def add_entry(entry, tags=None, status='unread'):
    """
    Добавление статьи в библиотеку.
    
    Args:
        entry: метаданные статьи
        tags: список тегов (опционально)
        status: статус статьи (read/unread)
    """
    library = load_library()
    
    # Проверяем, что статья ещё не добавлена
    existing_ids = [e['id'] for e in library['entries']]
    if entry['id'] in existing_ids:
        # Обновляем существующую
        for i, e in enumerate(library['entries']):
            if e['id'] == entry['id']:
                # Сохраняем существующие поля статуса
                existing_status = e.get('status', 'unread')
                existing_starred = e.get('starred', False)
                existing_read_at = e.get('read_at')
                
                library['entries'][i] = entry
                library['entries'][i]['status'] = existing_status
                library['entries'][i]['starred'] = existing_starred
                if existing_read_at:
                    library['entries'][i]['read_at'] = existing_read_at
                
                if tags:
                    library['entries'][i]['tags'] = tags
                break
    else:
        # Добавляем новую
        if tags:
            entry['tags'] = tags
        else:
            entry['tags'] = []
        
        entry['added_at'] = datetime.now().isoformat()
        entry['status'] = status
        entry['starred'] = False
        library['entries'].append(entry)
    
    save_library(library)


def get_entries(category=None, tags=None, status=None, starred=None, 
                search_query=None, sort_by='added_at', sort_order='desc'):
    """
    Получение статей из библиотеки с фильтрацией и сортировкой.
    
    Args:
        category: фильтр по категории
        tags: фильтр по тегам (список)
        status: фильтр по статусу (read/unread)
        starred: фильтр по starred (True/False)
        search_query: полнотекстовый поиск по title и abstract
        sort_by: поле сортировки (added_at, published, title)
        sort_order: порядок сортировки (asc/desc)
        
    Returns:
        list: отфильтрованные и отсортированные статьи
    """
    library = load_library()
    entries = library['entries']
    
    # Фильтр по категории
    if category:
        entries = [e for e in entries if category in e.get('categories', [])]
    
    # Фильтр по тегам
    if tags:
        entries = [e for e in entries if any(tag in e.get('tags', []) for tag in tags)]
    
    # Фильтр по статусу
    if status:
        entries = [e for e in entries if e.get('status', 'unread') == status]
    
    # Фильтр по starred
    if starred is not None:
        entries = [e for e in entries if e.get('starred', False) == starred]
    
    # Полнотекстовый поиск
    if search_query:
        query_lower = search_query.lower()
        entries = [
            e for e in entries 
            if query_lower in e.get('title', '').lower() 
            or query_lower in e.get('abstract', '').lower()
        ]
    
    # Сортировка
    reverse = (sort_order == 'desc')
    
    if sort_by == 'added_at':
        entries.sort(key=lambda e: e.get('added_at', ''), reverse=reverse)
    elif sort_by == 'published':
        entries.sort(key=lambda e: e.get('published', ''), reverse=reverse)
    elif sort_by == 'title':
        entries.sort(key=lambda e: e.get('title', '').lower(), reverse=reverse)
    elif sort_by == 'read_at':
        entries.sort(key=lambda e: e.get('read_at', ''), reverse=reverse)
    
    return entries


def remove_entry(arxiv_id):
    """
    Удаление статьи из библиотеки.
    
    Args:
        arxiv_id: идентификатор статьи
    """
    library = load_library()
    library['entries'] = [e for e in library['entries'] if e['id'] != arxiv_id]
    save_library(library)


def add_tags(arxiv_id, tags):
    """
    Добавление тегов к статье.
    
    Args:
        arxiv_id: идентификатор статьи
        tags: список тегов
    """
    library = load_library()
    
    for entry in library['entries']:
        if entry['id'] == arxiv_id:
            current_tags = set(entry.get('tags', []))
            current_tags.update(tags)
            entry['tags'] = list(current_tags)
            break
    
    save_library(library)


def remove_tags(arxiv_id, tags):
    """
    Удаление тегов у статьи.
    
    Args:
        arxiv_id: идентификатор статьи
        tags: список тегов для удаления
    """
    library = load_library()
    
    for entry in library['entries']:
        if entry['id'] == arxiv_id:
            current_tags = set(entry.get('tags', []))
            current_tags.difference_update(tags)
            entry['tags'] = list(current_tags)
            break
    
    save_library(library)


def update_status(arxiv_id, status):
    """
    Обновление статуса статьи.
    
    Args:
        arxiv_id: идентификатор статьи
        status: новый статус (read/unread)
    """
    library = load_library()
    
    for entry in library['entries']:
        if entry['id'] == arxiv_id:
            entry['status'] = status
            if status == 'read':
                entry['read_at'] = datetime.now().isoformat()
            break
    
    save_library(library)


def toggle_starred(arxiv_id):
    """
    Переключение флага starred для статьи.
    
    Args:
        arxiv_id: идентификатор статьи
        
    Returns:
        bool: новое значение starred
    """
    library = load_library()
    
    for entry in library['entries']:
        if entry['id'] == arxiv_id:
            current = entry.get('starred', False)
            entry['starred'] = not current
            save_library(library)
            return entry['starred']
    
    return False


def get_stats():
    """
    Статистика библиотеки.
    
    Returns:
        dict: статистика (количество статей, категории, теги, статусы)
    """
    library = load_library()
    entries = library['entries']
    
    categories = {}
    all_tags = set()
    statuses = {'read': 0, 'unread': 0}
    starred_count = 0
    
    for entry in entries:
        # Подсчёт категорий
        for cat in entry.get('categories', []):
            categories[cat] = categories.get(cat, 0) + 1
        
        # Сбор тегов
        all_tags.update(entry.get('tags', []))
        
        # Подсчёт статусов
        status = entry.get('status', 'unread')
        statuses[status] = statuses.get(status, 0) + 1
        
        # Подсчёт starred
        if entry.get('starred', False):
            starred_count += 1
    
    return {
        'total': len(entries),
        'categories': categories,
        'tags': sorted(all_tags),
        'statuses': statuses,
        'starred': starred_count,
        'updated': library.get('updated')
    }

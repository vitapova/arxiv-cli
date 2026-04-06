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


def add_entry(entry, tags=None):
    """
    Добавление статьи в библиотеку.
    
    Args:
        entry: метаданные статьи
        tags: список тегов (опционально)
    """
    library = load_library()
    
    # Проверяем, что статья ещё не добавлена
    existing_ids = [e['id'] for e in library['entries']]
    if entry['id'] in existing_ids:
        # Обновляем существующую
        for i, e in enumerate(library['entries']):
            if e['id'] == entry['id']:
                library['entries'][i] = entry
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
        library['entries'].append(entry)
    
    save_library(library)


def get_entries(category=None, tags=None):
    """
    Получение статей из библиотеки с фильтрацией.
    
    Args:
        category: фильтр по категории
        tags: фильтр по тегам (список)
        
    Returns:
        list: отфильтрованные статьи
    """
    library = load_library()
    entries = library['entries']
    
    # Фильтр по категории
    if category:
        entries = [e for e in entries if category in e.get('categories', [])]
    
    # Фильтр по тегам
    if tags:
        entries = [e for e in entries if any(tag in e.get('tags', []) for tag in tags)]
    
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


def get_stats():
    """
    Статистика библиотеки.
    
    Returns:
        dict: статистика (количество статей, категории, теги)
    """
    library = load_library()
    entries = library['entries']
    
    categories = {}
    all_tags = set()
    
    for entry in entries:
        # Подсчёт категорий
        for cat in entry.get('categories', []):
            categories[cat] = categories.get(cat, 0) + 1
        
        # Сбор тегов
        all_tags.update(entry.get('tags', []))
    
    return {
        'total': len(entries),
        'categories': categories,
        'tags': sorted(all_tags),
        'updated': library.get('updated')
    }

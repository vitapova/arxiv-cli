"""
Управление подписками на поисковые запросы

Функциональность:
- Создание подписки
- Проверка обновлений
- Список подписок
- Удаление подписок
"""

import json
import os
from pathlib import Path
from datetime import datetime
from arxiv_cli.commands.search import search_articles


SUBSCRIPTIONS_FILE = Path.home() / '.arxiv-cli' / 'subscriptions.json'


def ensure_subscriptions_dir():
    """Создание директории для подписок."""
    SUBSCRIPTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_subscriptions():
    """
    Загрузка подписок.
    
    Returns:
        dict: подписки с метаданными
    """
    ensure_subscriptions_dir()
    
    if not SUBSCRIPTIONS_FILE.exists():
        return {'subscriptions': [], 'updated': None}
    
    with open(SUBSCRIPTIONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_subscriptions(data):
    """
    Сохранение подписок.
    
    Args:
        data: dict с подписками
    """
    ensure_subscriptions_dir()
    
    data['updated'] = datetime.now().isoformat()
    
    with open(SUBSCRIPTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def add_subscription(query, categories=None, name=None, max_results=20):
    """
    Добавить подписку.
    
    Args:
        query: поисковый запрос
        categories: список категорий
        name: имя подписки (опционально)
        max_results: максимум результатов
        
    Returns:
        dict: созданная подписка
    """
    data = load_subscriptions()
    
    # Генерируем ID
    sub_id = len(data['subscriptions']) + 1
    
    # Формируем имя
    if not name:
        if query:
            name = query[:30]
        elif categories:
            name = ', '.join(categories[:2])
        else:
            name = f'Подписка #{sub_id}'
    
    subscription = {
        'id': sub_id,
        'name': name,
        'query': query,
        'categories': categories or [],
        'max_results': max_results,
        'created_at': datetime.now().isoformat(),
        'last_checked': None,
        'last_results': []  # ID последних результатов
    }
    
    data['subscriptions'].append(subscription)
    save_subscriptions(data)
    
    return subscription


def list_subscriptions():
    """
    Список всех подписок.
    
    Returns:
        list: подписки
    """
    data = load_subscriptions()
    return data['subscriptions']


def get_subscription(sub_id):
    """
    Получить подписку по ID.
    
    Args:
        sub_id: ID подписки
        
    Returns:
        dict: подписка или None
    """
    data = load_subscriptions()
    
    for sub in data['subscriptions']:
        if sub['id'] == sub_id:
            return sub
    
    return None


def remove_subscription(sub_id):
    """
    Удалить подписку.
    
    Args:
        sub_id: ID подписки
        
    Returns:
        bool: успешно ли удалено
    """
    data = load_subscriptions()
    initial_count = len(data['subscriptions'])
    
    data['subscriptions'] = [s for s in data['subscriptions'] if s['id'] != sub_id]
    
    if len(data['subscriptions']) < initial_count:
        save_subscriptions(data)
        return True
    
    return False


def check_subscription(sub_id, verbose=False):
    """
    Проверить обновления для подписки.
    
    Args:
        sub_id: ID подписки
        verbose: выводить информацию о повторах
        
    Returns:
        dict: новые статьи и статистика
    """
    sub = get_subscription(sub_id)
    if not sub:
        return None
    
    # Выполняем поиск
    results = search_articles(
        query=sub['query'],
        max_results=sub['max_results'],
        sort_by='submittedDate',
        sort_order='descending',
        categories=sub['categories'] if sub['categories'] else None,
        verbose=verbose
    )
    
    # Получаем ID текущих результатов
    current_ids = [e['id'] for e in results['entries']]
    
    # Получаем ID прошлых результатов
    previous_ids = set(sub.get('last_results', []))
    
    # Новые статьи = текущие - прошлые
    new_ids = [id for id in current_ids if id not in previous_ids]
    new_entries = [e for e in results['entries'] if e['id'] in new_ids]
    
    # Обновляем подписку
    data = load_subscriptions()
    for s in data['subscriptions']:
        if s['id'] == sub_id:
            s['last_checked'] = datetime.now().isoformat()
            s['last_results'] = current_ids
            break
    
    save_subscriptions(data)
    
    return {
        'subscription': sub,
        'total': len(results['entries']),
        'new': len(new_entries),
        'new_entries': new_entries
    }


def check_all_subscriptions(verbose=False):
    """
    Проверить все подписки.
    
    Args:
        verbose: выводить информацию о повторах
        
    Returns:
        list: результаты проверки для каждой подписки
    """
    subscriptions = list_subscriptions()
    results = []
    
    for sub in subscriptions:
        result = check_subscription(sub['id'], verbose=verbose)
        if result:
            results.append(result)
    
    return results

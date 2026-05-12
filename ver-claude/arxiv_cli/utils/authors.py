"""
Отслеживание авторов

Функциональность для мониторинга публикаций конкретных исследователей
"""

import json
from pathlib import Path
from datetime import datetime
from arxiv_cli.commands.search import search_articles


AUTHORS_FILE = Path.home() / '.arxiv-cli' / 'authors.json'


def ensure_authors_dir():
    """Создание директории."""
    AUTHORS_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_authors():
    """Загрузка списка авторов."""
    ensure_authors_dir()
    
    if not AUTHORS_FILE.exists():
        return {'authors': [], 'updated': None}
    
    with open(AUTHORS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_authors(data):
    """Сохранение списка авторов."""
    ensure_authors_dir()
    
    data['updated'] = datetime.now().isoformat()
    
    with open(AUTHORS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def follow_author(name, tags=None, max_results=10):
    """
    Добавить автора в отслеживание.
    
    Args:
        name: имя автора
        tags: теги для категоризации
        max_results: количество статей для проверки
        
    Returns:
        dict: данные автора
    """
    data = load_authors()
    
    # Проверяем что автор ещё не отслеживается
    for author in data['authors']:
        if author['name'].lower() == name.lower():
            return None  # Уже отслеживается
    
    author_data = {
        'name': name,
        'tags': tags or [],
        'max_results': max_results,
        'added_at': datetime.now().isoformat(),
        'last_checked': None,
        'last_papers': []  # ID последних статей
    }
    
    data['authors'].append(author_data)
    save_authors(data)
    
    return author_data


def list_authors():
    """Список отслеживаемых авторов."""
    data = load_authors()
    return data['authors']


def unfollow_author(name):
    """
    Убрать автора из отслеживания.
    
    Args:
        name: имя автора
        
    Returns:
        bool: успешно ли удалено
    """
    data = load_authors()
    initial_count = len(data['authors'])
    
    data['authors'] = [a for a in data['authors'] if a['name'].lower() != name.lower()]
    
    if len(data['authors']) < initial_count:
        save_authors(data)
        return True
    
    return False


def check_author_updates(name=None):
    """
    Проверить новые публикации авторов.
    
    Args:
        name: имя автора (опционально, если None — проверяет всех)
        
    Returns:
        list: результаты для каждого автора
    """
    data = load_authors()
    
    if name:
        authors = [a for a in data['authors'] if a['name'].lower() == name.lower()]
    else:
        authors = data['authors']
    
    results = []
    
    for author in authors:
        # Поиск по автору
        search_results = search_articles(
            query='',
            authors=[author['name']],
            max_results=author['max_results'],
            sort_by='submittedDate',
            sort_order='descending',
            verbose=True
        )
        
        current_ids = [e['id'] for e in search_results['entries']]
        previous_ids = set(author.get('last_papers', []))
        
        # Новые статьи
        new_ids = [id for id in current_ids if id not in previous_ids]
        new_papers = [e for e in search_results['entries'] if e['id'] in new_ids]
        
        # Обновляем данные автора
        for a in data['authors']:
            if a['name'].lower() == author['name'].lower():
                a['last_checked'] = datetime.now().isoformat()
                a['last_papers'] = current_ids
                break
        
        results.append({
            'author': author['name'],
            'total': len(search_results['entries']),
            'new': len(new_papers),
            'new_papers': new_papers
        })
    
    save_authors(data)
    
    return results


def get_author_stats():
    """Статистика по авторам."""
    data = load_authors()
    
    return {
        'total': len(data['authors']),
        'authors': data['authors']
    }

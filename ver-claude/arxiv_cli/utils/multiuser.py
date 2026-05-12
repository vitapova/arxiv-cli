"""
Multiuser support

Управление библиотеками для разных пользователей
"""

from pathlib import Path


BASE_DIR = Path.home() / '.arxiv-cli'
USERS_DIR = BASE_DIR / 'users'


def get_user_dir(user_id=None):
    """
    Получить директорию пользователя.
    
    Args:
        user_id: ID пользователя (Telegram user_id, email, etc.)
                 Если None — используется общая библиотека (для CLI)
    
    Returns:
        Path: путь к директории пользователя
    """
    if user_id is None:
        # Обратная совместимость — общая библиотека для CLI
        return BASE_DIR
    
    # Пользовательская директория
    user_dir = USERS_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    
    return user_dir


def get_library_file(user_id=None):
    """Путь к файлу библиотеки."""
    return get_user_dir(user_id) / 'library.json'


def get_subscriptions_file(user_id=None):
    """Путь к файлу подписок."""
    return get_user_dir(user_id) / 'subscriptions.json'


def get_authors_file(user_id=None):
    """Путь к файлу авторов."""
    return get_user_dir(user_id) / 'authors.json'


def list_users():
    """
    Список всех пользователей.
    
    Returns:
        list: ID пользователей
    """
    if not USERS_DIR.exists():
        return []
    
    return [d.name for d in USERS_DIR.iterdir() if d.is_dir()]


def get_user_stats(user_id):
    """
    Статистика пользователя.
    
    Args:
        user_id: ID пользователя
        
    Returns:
        dict: статистика
    """
    from arxiv_cli.utils.library import get_stats
    
    stats = get_stats(user_id=user_id)
    
    return {
        'user_id': user_id,
        'total_papers': stats['total'],
        'read': stats['statuses']['read'],
        'unread': stats['statuses']['unread'],
        'starred': stats['starred'],
        'tags_count': len(stats['tags']),
        'categories_count': len(stats['categories'])
    }


def migrate_to_multiuser(user_id='default'):
    """
    Миграция существующей библиотеки в multiuser режим.
    
    Args:
        user_id: ID для миграции существующих данных
    """
    import shutil
    
    old_library = BASE_DIR / 'library.json'
    old_subs = BASE_DIR / 'subscriptions.json'
    old_authors = BASE_DIR / 'authors.json'
    
    if old_library.exists() or old_subs.exists() or old_authors.exists():
        user_dir = get_user_dir(user_id)
        
        if old_library.exists():
            shutil.copy(old_library, user_dir / 'library.json')
            print(f"✓ Библиотека мигрирована для пользователя {user_id}")
        
        if old_subs.exists():
            shutil.copy(old_subs, user_dir / 'subscriptions.json')
            print(f"✓ Подписки мигрированы для пользователя {user_id}")
        
        if old_authors.exists():
            shutil.copy(old_authors, user_dir / 'authors.json')
            print(f"✓ Авторы мигрированы для пользователя {user_id}")

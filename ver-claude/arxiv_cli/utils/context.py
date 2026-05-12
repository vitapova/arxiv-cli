"""
User context для multiuser режима

Хранит текущего пользователя в thread-local переменной
"""

import threading

_context = threading.local()


def set_user(user_id):
    """
    Установить текущего пользователя.
    
    Args:
        user_id: ID пользователя
    """
    _context.user_id = user_id


def get_user():
    """
    Получить ID текущего пользователя.
    
    Returns:
        str или None: ID пользователя
    """
    return getattr(_context, 'user_id', None)


def clear_user():
    """Очистить контекст пользователя."""
    if hasattr(_context, 'user_id'):
        del _context.user_id

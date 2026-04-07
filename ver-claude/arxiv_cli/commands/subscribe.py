"""
Команда subscribe - управление подписками

Подкоманды:
- add: создать подписку
- list: показать все подписки
- check: проверить обновления
- remove: удалить подписку
"""

from arxiv_cli.utils.subscriptions import (
    add_subscription,
    list_subscriptions,
    check_subscription,
    check_all_subscriptions,
    remove_subscription
)


def subscribe_add(query, categories=None, name=None, max_results=20):
    """
    Создать подписку.
    
    Args:
        query: поисковый запрос
        categories: список категорий
        name: имя подписки
        max_results: максимум результатов
        
    Returns:
        dict: созданная подписка
    """
    return add_subscription(query, categories=categories, name=name, max_results=max_results)


def subscribe_list():
    """
    Список всех подписок.
    
    Returns:
        list: подписки
    """
    return list_subscriptions()


def subscribe_check(sub_id=None):
    """
    Проверить обновления.
    
    Args:
        sub_id: ID подписки (опционально, если None — проверяет все)
        
    Returns:
        list или dict: результаты проверки
    """
    if sub_id:
        return check_subscription(sub_id)
    else:
        return check_all_subscriptions()


def subscribe_remove(sub_id):
    """
    Удалить подписку.
    
    Args:
        sub_id: ID подписки
        
    Returns:
        bool: успешно ли удалено
    """
    return remove_subscription(sub_id)

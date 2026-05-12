"""
Команды для отслеживания авторов
"""

from arxiv_cli.utils.authors import (
    follow_author,
    list_authors,
    unfollow_author,
    check_author_updates,
    get_author_stats
)


def authors_follow(name, tags=None, max_results=10):
    """Добавить автора в отслеживание."""
    return follow_author(name, tags=tags, max_results=max_results)


def authors_list():
    """Список отслеживаемых авторов."""
    return list_authors()


def authors_unfollow(name):
    """Убрать автора из отслеживания."""
    return unfollow_author(name)


def authors_check(name=None):
    """Проверить новые публикации."""
    return check_author_updates(name=name)


def authors_stats():
    """Статистика."""
    return get_author_stats()

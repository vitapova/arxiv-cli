"""
Команды для заметок к статьям
"""

from arxiv_cli.utils.library import add_note, get_notes


def note_add(arxiv_id, text):
    """Добавить заметку."""
    add_note(arxiv_id, text)


def note_list(arxiv_id=None):
    """Список заметок."""
    return get_notes(arxiv_id=arxiv_id)


def note_search(query):
    """Поиск по заметкам."""
    return get_notes(search_query=query)

"""
Команда export - экспорт библиографических данных

Параметры:
- arxiv_id: идентификатор статьи (опционально)
- format: формат экспорта (bibtex/csl)
- output: путь для сохранения
- category: фильтр по категории
- tag: фильтр по тегу
- all: экспорт всей библиотеки
"""

import json
from arxiv_cli.api.client import ArxivClient, ArxivAPIError
from arxiv_cli.api.parser import parse_search_results
from arxiv_cli.utils.formatter import format_bibtex, format_csl
from arxiv_cli.utils.library import get_entries, get_stats


def export_single(arxiv_id, format='bibtex'):
    """
    Экспорт одной статьи по ID.
    
    Args:
        arxiv_id: идентификатор статьи
        format: формат экспорта ('bibtex' или 'csl')
        
    Returns:
        str: экспортированные данные
    """
    client = ArxivClient()
    
    # Получаем метаданные
    xml = client.get_by_id(arxiv_id)
    results = parse_search_results(xml)
    
    if not results['entries']:
        raise ArxivAPIError(f'Статья {arxiv_id} не найдена')
    
    entry = results['entries'][0]
    
    if format == 'bibtex':
        return format_bibtex(entry)
    elif format == 'csl':
        return json.dumps(format_csl(entry), indent=2, ensure_ascii=False)
    else:
        raise ValueError(f'Неизвестный формат: {format}')


def export_library(format='bibtex', category=None, tags=None):
    """
    Экспорт библиотеки с фильтрацией.
    
    Args:
        format: формат экспорта ('bibtex' или 'csl')
        category: фильтр по категории
        tags: фильтр по тегам
        
    Returns:
        str: экспортированные данные
    """
    entries = get_entries(category=category, tags=tags)
    
    if not entries:
        return "# Библиотека пуста или не найдено статей по фильтру"
    
    if format == 'bibtex':
        # BibTeX — каждая запись отдельно
        bibtex_entries = [format_bibtex(entry) for entry in entries]
        return '\n\n'.join(bibtex_entries)
    
    elif format == 'csl':
        # CSL JSON — массив объектов
        csl_entries = [format_csl(entry) for entry in entries]
        return json.dumps(csl_entries, indent=2, ensure_ascii=False)
    
    else:
        raise ValueError(f'Неизвестный формат: {format}')

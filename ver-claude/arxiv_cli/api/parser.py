"""
Парсер XML-ответов от arXiv API

arXiv API возвращает данные в формате Atom XML.
Этот модуль отвечает за парсинг и преобразование в удобную структуру.

Функции:
- parse_search_results(xml) - парсинг результатов поиска
- parse_entry(entry) - парсинг отдельной статьи
"""

import feedparser
from datetime import datetime


def parse_search_results(xml_text):
    """
    Парсинг результатов поиска из XML.
    
    Args:
        xml_text: XML-ответ от arXiv API
        
    Returns:
        dict: распарсенные результаты с метаданными
    """
    feed = feedparser.parse(xml_text)
    
    return {
        'total_results': int(feed.feed.get('opensearch_totalresults', 0)),
        'start_index': int(feed.feed.get('opensearch_startindex', 0)),
        'items_per_page': int(feed.feed.get('opensearch_itemsperpage', 0)),
        'entries': [parse_entry(entry) for entry in feed.entries]
    }


def parse_entry(entry):
    """
    Парсинг отдельной статьи из XML.
    
    Args:
        entry: элемент entry из Atom feed
        
    Returns:
        dict: данные статьи (id, title, authors, abstract, etc.)
    """
    # Извлекаем arXiv ID из ссылки
    arxiv_id = entry.id.split('/abs/')[-1]
    
    # Парсим авторов
    authors = [author.name for author in entry.get('authors', [])]
    
    # Парсим категории
    categories = [tag.term for tag in entry.get('tags', [])]
    
    # Парсим даты
    published = entry.get('published', '')
    updated = entry.get('updated', '')
    
    return {
        'id': arxiv_id,
        'title': entry.get('title', '').strip(),
        'authors': authors,
        'abstract': entry.get('summary', '').strip(),
        'categories': categories,
        'primary_category': categories[0] if categories else None,
        'published': published,
        'updated': updated,
        'pdf_url': entry.get('link', '').replace('/abs/', '/pdf/'),
        'abs_url': entry.get('link', ''),
        'comment': entry.get('arxiv_comment', ''),
        'journal_ref': entry.get('arxiv_journal_ref', ''),
        'doi': entry.get('arxiv_doi', '')
    }

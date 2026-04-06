"""
Тесты для парсера XML
"""

import pytest
from arxiv_cli.api.parser import parse_search_results, parse_entry
from arxiv_cli.api.client import ArxivClient


class TestParser:
    """Тесты для парсера."""
    
    def test_parse_search_results_structure(self):
        """Тест структуры результатов парсинга."""
        client = ArxivClient()
        xml = client.search('quantum', max_results=2)
        
        results = parse_search_results(xml)
        
        # Проверяем структуру
        assert 'total_results' in results
        assert 'start_index' in results
        assert 'items_per_page' in results
        assert 'entries' in results
        
        # Проверяем типы
        assert isinstance(results['total_results'], int)
        assert isinstance(results['entries'], list)
        assert results['total_results'] > 0
    
    def test_parse_entry_fields(self):
        """Тест полей распарсенной статьи."""
        client = ArxivClient()
        xml = client.get_by_id('1706.03762')
        
        results = parse_search_results(xml)
        assert len(results['entries']) > 0
        
        entry = results['entries'][0]
        
        # Обязательные поля
        assert 'id' in entry
        assert 'title' in entry
        assert 'authors' in entry
        assert 'abstract' in entry
        assert 'categories' in entry
        assert 'primary_category' in entry
        assert 'published' in entry
        assert 'updated' in entry
        assert 'pdf_url' in entry
        assert 'abs_url' in entry
        
        # Проверяем типы
        assert isinstance(entry['authors'], list)
        assert isinstance(entry['categories'], list)
        assert len(entry['authors']) > 0
        assert len(entry['categories']) > 0
    
    def test_parse_known_paper(self):
        """Тест парсинга известной статьи."""
        client = ArxivClient()
        xml = client.get_by_id('1706.03762')
        
        results = parse_search_results(xml)
        entry = results['entries'][0]
        
        # Проверяем конкретные данные
        assert 'Attention Is All You Need' in entry['title']
        assert 'Vaswani' in entry['authors'][0]
        assert entry['primary_category'] == 'cs.CL'
        assert '2017' in entry['published']
    
    def test_parse_multiple_entries(self):
        """Тест парсинга нескольких статей."""
        client = ArxivClient()
        xml = client.search('transformer', max_results=5)
        
        results = parse_search_results(xml)
        
        # Проверяем количество
        assert len(results['entries']) <= 5
        
        # Проверяем, что все статьи имеют нужные поля
        for entry in results['entries']:
            assert 'id' in entry
            assert 'title' in entry
            assert len(entry['authors']) > 0

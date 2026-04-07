"""
Тесты для команды list
"""

import pytest
import tempfile
from pathlib import Path
from arxiv_cli.commands.list import (
    list_library,
    mark_as_read,
    mark_as_unread,
    toggle_star
)
from arxiv_cli.utils.library import add_entry, get_entry


@pytest.fixture(autouse=True)
def temp_library(monkeypatch):
    """Использовать временный файл для библиотеки."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_file = Path(tmpdir) / 'library.json'
        monkeypatch.setattr('arxiv_cli.utils.library.LIBRARY_FILE', temp_file)
        yield temp_file


class TestListCommand:
    """Тесты для команды list."""
    
    def test_list_library_all(self):
        """Тест вывода всей библиотеки."""
        entry1 = {
            'id': '1111.1111',
            'title': 'AI Paper',
            'authors': ['Author 1'],
            'categories': ['cs.AI'],
            'published': '2020-01-01',
            'updated': '2020-01-01',
            'abstract': 'Test',
            'primary_category': 'cs.AI',
            'pdf_url': 'https://example.com',
            'abs_url': 'https://example.com'
        }
        
        entry2 = {
            'id': '2222.2222',
            'title': 'NLP Paper',
            'authors': ['Author 2'],
            'categories': ['cs.CL'],
            'published': '2020-02-01',
            'updated': '2020-02-01',
            'abstract': 'Test',
            'primary_category': 'cs.CL',
            'pdf_url': 'https://example.com',
            'abs_url': 'https://example.com'
        }
        
        add_entry(entry1, tags=['ai'])
        add_entry(entry2, tags=['nlp'], status='read')
        
        results = list_library()
        
        assert len(results) == 2
    
    def test_list_library_status_filter(self):
        """Тест фильтра по статусу."""
        entry1 = {
            'id': '1111.1111',
            'title': 'Paper 1',
            'authors': ['Author'],
            'categories': ['cs.AI'],
            'published': '2020-01-01',
            'updated': '2020-01-01',
            'abstract': 'Test',
            'primary_category': 'cs.AI',
            'pdf_url': 'https://example.com',
            'abs_url': 'https://example.com'
        }
        
        entry2 = {
            'id': '2222.2222',
            'title': 'Paper 2',
            'authors': ['Author'],
            'categories': ['cs.AI'],
            'published': '2020-01-01',
            'updated': '2020-01-01',
            'abstract': 'Test',
            'primary_category': 'cs.AI',
            'pdf_url': 'https://example.com',
            'abs_url': 'https://example.com'
        }
        
        add_entry(entry1, status='unread')
        add_entry(entry2, status='read')
        
        unread = list_library(status='unread')
        assert len(unread) == 1
        assert unread[0]['id'] == '1111.1111'
    
    def test_list_library_starred_filter(self):
        """Тест фильтра starred."""
        entry = {
            'id': '3333.3333',
            'title': 'Paper',
            'authors': ['Author'],
            'categories': ['cs.AI'],
            'published': '2020-01-01',
            'updated': '2020-01-01',
            'abstract': 'Test',
            'primary_category': 'cs.AI',
            'pdf_url': 'https://example.com',
            'abs_url': 'https://example.com'
        }
        
        add_entry(entry)
        toggle_star('3333.3333')
        
        starred = list_library(status='starred')
        assert len(starred) == 1
    
    def test_mark_as_read(self):
        """Тест отметки как прочитанная."""
        entry = {
            'id': '4444.4444',
            'title': 'Paper',
            'authors': ['Author'],
            'categories': ['cs.AI'],
            'published': '2020-01-01',
            'updated': '2020-01-01',
            'abstract': 'Test',
            'primary_category': 'cs.AI',
            'pdf_url': 'https://example.com',
            'abs_url': 'https://example.com'
        }
        
        add_entry(entry, status='unread')
        
        mark_as_read('4444.4444')
        
        result = get_entry('4444.4444')
        assert result['status'] == 'read'
        assert 'read_at' in result
    
    def test_mark_as_unread(self):
        """Тест отметки как непрочитанная."""
        entry = {
            'id': '5555.5555',
            'title': 'Paper',
            'authors': ['Author'],
            'categories': ['cs.AI'],
            'published': '2020-01-01',
            'updated': '2020-01-01',
            'abstract': 'Test',
            'primary_category': 'cs.AI',
            'pdf_url': 'https://example.com',
            'abs_url': 'https://example.com'
        }
        
        add_entry(entry, status='read')
        
        mark_as_unread('5555.5555')
        
        result = get_entry('5555.5555')
        assert result['status'] == 'unread'

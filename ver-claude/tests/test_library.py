"""
Тесты для расширенной функциональности библиотеки
"""

import pytest
import tempfile
from pathlib import Path
from arxiv_cli.utils.library import (
    add_entry,
    get_entries,
    update_status,
    toggle_starred,
    get_entry,
    remove_entry,
    LIBRARY_FILE
)


@pytest.fixture(autouse=True)
def temp_library(monkeypatch):
    """Использовать временный файл для библиотеки."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_file = Path(tmpdir) / 'library.json'
        monkeypatch.setattr('arxiv_cli.utils.library.LIBRARY_FILE', temp_file)
        yield temp_file


class TestLibraryExtended:
    """Тесты для расширенной функциональности библиотеки."""
    
    def test_add_entry_with_status(self):
        """Тест добавления статьи со статусом."""
        entry = {
            'id': '1234.5678',
            'title': 'Test Paper',
            'authors': ['Test Author'],
            'categories': ['cs.AI'],
            'published': '2020-01-01',
            'updated': '2020-01-01',
            'abstract': 'Test abstract',
            'primary_category': 'cs.AI',
            'pdf_url': 'https://example.com',
            'abs_url': 'https://example.com'
        }
        
        add_entry(entry, tags=['test'], status='read')
        
        result = get_entry('1234.5678')
        assert result is not None
        assert result['status'] == 'read'
        assert result['starred'] == False
        assert 'test' in result['tags']
        assert 'added_at' in result
    
    def test_get_entries_with_filters(self):
        """Тест фильтрации записей."""
        # Добавляем несколько статей
        entry1 = {
            'id': '1111.1111',
            'title': 'AI Paper',
            'authors': ['Author 1'],
            'categories': ['cs.AI'],
            'published': '2020-01-01',
            'updated': '2020-01-01',
            'abstract': 'Machine learning research',
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
            'abstract': 'Natural language processing',
            'primary_category': 'cs.CL',
            'pdf_url': 'https://example.com',
            'abs_url': 'https://example.com'
        }
        
        add_entry(entry1, tags=['ml'], status='unread')
        add_entry(entry2, tags=['nlp'], status='read')
        
        # Фильтр по статусу
        unread = get_entries(status='unread')
        assert len(unread) == 1
        assert unread[0]['id'] == '1111.1111'
        
        # Фильтр по категории
        ai_papers = get_entries(category='cs.AI')
        assert len(ai_papers) == 1
        
        # Фильтр по тегу
        nlp_papers = get_entries(tags=['nlp'])
        assert len(nlp_papers) == 1
        
        # Поиск по тексту
        ml_papers = get_entries(search_query='machine learning')
        assert len(ml_papers) == 1
    
    def test_update_status(self):
        """Тест обновления статуса."""
        entry = {
            'id': '3333.3333',
            'title': 'Test',
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
        
        update_status('3333.3333', 'read')
        
        result = get_entry('3333.3333')
        assert result['status'] == 'read'
        assert 'read_at' in result
    
    def test_toggle_starred(self):
        """Тест переключения starred."""
        entry = {
            'id': '4444.4444',
            'title': 'Test',
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
        
        # Первое переключение
        result = toggle_starred('4444.4444')
        assert result == True
        
        entry_data = get_entry('4444.4444')
        assert entry_data['starred'] == True
        
        # Второе переключение
        result = toggle_starred('4444.4444')
        assert result == False
    
    def test_remove_entry(self):
        """Тест удаления записи."""
        entry = {
            'id': '5555.5555',
            'title': 'Test',
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
        
        # Проверяем что статья есть
        assert get_entry('5555.5555') is not None
        
        # Удаляем
        result = remove_entry('5555.5555')
        assert result == True
        
        # Проверяем что статьи нет
        assert get_entry('5555.5555') is None
        
        # Повторное удаление
        result = remove_entry('5555.5555')
        assert result == False
    
    def test_sorting(self):
        """Тест сортировки."""
        entry1 = {
            'id': 'a.1111',
            'title': 'Alpha',
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
            'id': 'b.2222',
            'title': 'Beta',
            'authors': ['Author'],
            'categories': ['cs.AI'],
            'published': '2021-01-01',
            'updated': '2021-01-01',
            'abstract': 'Test',
            'primary_category': 'cs.AI',
            'pdf_url': 'https://example.com',
            'abs_url': 'https://example.com'
        }
        
        add_entry(entry1)
        add_entry(entry2)
        
        # Сортировка по названию
        results = get_entries(sort_by='title', sort_order='asc')
        assert results[0]['title'] == 'Alpha'
        
        # Сортировка по дате
        results = get_entries(sort_by='published', sort_order='desc')
        assert results[0]['published'] == '2021-01-01'

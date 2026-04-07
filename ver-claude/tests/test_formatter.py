"""
Тесты для форматтеров вывода
"""

import pytest
import json
from arxiv_cli.utils.formatter import (
    format_search_result,
    format_search_table,
    format_bibtex,
    format_csl
)


class TestFormatter:
    """Тесты для форматтеров."""
    
    @pytest.fixture
    def sample_entry(self):
        """Пример статьи для тестов."""
        return {
            'id': '1706.03762',
            'title': 'Attention Is All You Need',
            'authors': ['Ashish Vaswani', 'Noam Shazeer', 'Niki Parmar'],
            'abstract': 'The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.',
            'categories': ['cs.CL', 'cs.AI', 'cs.LG'],
            'primary_category': 'cs.CL',
            'published': '2017-06-12T17:40:30Z',
            'updated': '2017-06-12T17:40:30Z',
            'pdf_url': 'https://arxiv.org/pdf/1706.03762',
            'abs_url': 'https://arxiv.org/abs/1706.03762',
            'comment': '',
            'journal_ref': '',
            'doi': ''
        }
    
    def test_format_search_result_text(self, sample_entry):
        """Тест текстового форматирования результата."""
        result = format_search_result(sample_entry, format='text')
        
        assert 'ID: 1706.03762' in result
        assert 'Attention Is All You Need' in result
        assert 'Vaswani' in result
        assert 'cs.CL' in result
        assert '2017-06-12' in result
    
    def test_format_search_result_compact(self, sample_entry):
        """Тест компактного форматирования."""
        result = format_search_result(sample_entry, format='text', compact=True)
        
        # Компактный формат не должен содержать аннотацию
        assert 'Аннотация' not in result
        assert 'PDF:' not in result
        
        # Но основные поля должны быть
        assert '1706.03762' in result
        assert 'Attention Is All You Need' in result
    
    def test_format_search_result_json(self, sample_entry):
        """Тест JSON-форматирования."""
        result = format_search_result(sample_entry, format='json')
        
        # Проверяем, что это валидный JSON
        data = json.loads(result)
        assert data['id'] == '1706.03762'
        assert data['title'] == 'Attention Is All You Need'
    
    def test_format_search_table(self, sample_entry):
        """Тест табличного форматирования."""
        entries = [sample_entry]
        result = format_search_table(entries)
        
        assert '№' in result
        assert 'ID' in result
        assert 'Дата' in result
        assert 'Категория' in result
        assert 'Название' in result
        assert '1706.03762' in result
        assert '2017-06-12' in result
    
    def test_format_bibtex(self, sample_entry):
        """Тест форматирования BibTeX."""
        result = format_bibtex(sample_entry)
        
        assert '@article{' in result
        assert 'title = {Attention Is All You Need}' in result
        assert 'author = {Ashish Vaswani and Noam Shazeer and Niki Parmar}' in result
        assert 'year = {2017}' in result
        assert 'eprint = {1706.03762}' in result
        assert 'archivePrefix = {arXiv}' in result
        assert 'primaryClass = {cs.CL}' in result
    
    def test_format_csl(self, sample_entry):
        """Тест форматирования CSL JSON."""
        result = format_csl(sample_entry)
        
        assert result['id'] == '1706.03762'
        assert result['type'] == 'article-journal'
        assert result['title'] == 'Attention Is All You Need'
        
        # Проверяем авторов
        assert len(result['author']) == 3
        assert result['author'][0]['family'] == 'Vaswani'
        assert result['author'][0]['given'] == 'Ashish'
        
        # Проверяем дату
        assert result['issued']['date-parts'][0] == [2017, 6, 12]
    
    def test_format_bibtex_with_doi(self):
        """Тест BibTeX с DOI."""
        entry = {
            'id': '1234.5678',
            'title': 'Test Paper',
            'authors': ['Test Author'],
            'published': '2020-01-01',
            'primary_category': 'cs.AI',
            'abs_url': 'https://arxiv.org/abs/1234.5678',
            'doi': '10.1234/test.5678'
        }
        
        result = format_bibtex(entry)
        assert 'doi = {10.1234/test.5678}' in result
    
    def test_format_search_table_long_title(self):
        """Тест таблицы с длинным названием."""
        entry = {
            'id': '1234.5678',
            'title': 'A' * 100,  # Очень длинное название
            'authors': ['Test'],
            'published': '2020-01-01',
            'primary_category': 'cs.AI',
            'categories': ['cs.AI']
        }
        
        result = format_search_table([entry])
        
        # Название должно быть обрезано
        assert '...' in result
        assert len(result.split('\n')[2]) < 150  # Строка не должна быть слишком длинной
    
    def test_format_library_entry(self, sample_entry):
        """Тест форматирования записи библиотеки."""
        from arxiv_cli.utils.formatter import format_library_entry
        
        # Добавляем поля библиотеки
        sample_entry['status'] = 'read'
        sample_entry['starred'] = True
        sample_entry['added_at'] = '2026-04-07T12:00:00'
        sample_entry['tags'] = ['test', 'paper']
        
        result = format_library_entry(sample_entry, compact=False)
        
        assert '✓' in result  # read status
        assert '★' in result  # starred
        assert 'test' in result
        assert 'paper' in result
        assert sample_entry['title'] in result
    
    def test_format_library_entry_compact(self, sample_entry):
        """Тест компактного форматирования библиотеки."""
        from arxiv_cli.utils.formatter import format_library_entry
        
        sample_entry['status'] = 'unread'
        sample_entry['starred'] = False
        sample_entry['added_at'] = '2026-04-07T12:00:00'
        
        result = format_library_entry(sample_entry, compact=True)
        
        assert '○' in result  # unread
        assert '☆' in result  # not starred
        # Аннотация не должна быть в компактном формате
        assert len(result) < len(format_library_entry(sample_entry, compact=False))
    
    def test_format_library_table(self, sample_entry):
        """Тест табличного формата библиотеки."""
        from arxiv_cli.utils.formatter import format_library_table
        
        sample_entry['status'] = 'read'
        sample_entry['starred'] = False
        sample_entry['added_at'] = '2026-04-07T12:00:00'
        sample_entry['tags'] = ['nlp', 'transformers']
        
        result = format_library_table([sample_entry])
        
        assert 'St' in result
        assert 'ID' in result
        assert '✓' in result
        assert 'nlp' in result or 'transformers' in result
    
    def test_format_digest_text(self):
        """Тест текстового формата дайджеста."""
        from arxiv_cli.utils.formatter import format_digest
        
        digest_data = {
            'period': 'week',
            'date_from': '2026-03-31',
            'date_to': '2026-04-07',
            'total': 2,
            'statistics': {
                'total': 2,
                'by_category': {'cs.AI': 2}
            },
            'grouped': {
                'cs.AI': [
                    {
                        'id': '1111.1111',
                        'title': 'Test Paper',
                        'authors': ['Author 1', 'Author 2'],
                        'abstract': 'Test abstract',
                        'published': '2026-04-01',
                        'primary_category': 'cs.AI',
                        'categories': ['cs.AI']
                    }
                ]
            },
            'entries': []
        }
        
        result = format_digest(digest_data, format='text')
        
        assert 'Дайджест новых публикаций' in result
        assert '2026-03-31' in result
        assert '2026-04-07' in result
        assert 'Всего статей: 2' in result
        assert 'cs.AI' in result
        assert 'Test Paper' in result
    
    def test_format_digest_markdown(self):
        """Тест markdown формата дайджеста."""
        from arxiv_cli.utils.formatter import format_digest
        
        digest_data = {
            'period': 'day',
            'date_from': '2026-04-06',
            'date_to': '2026-04-07',
            'total': 1,
            'statistics': {
                'total': 1,
                'by_category': {'cs.CL': 1}
            },
            'grouped': {
                'cs.CL': [
                    {
                        'id': '2222.2222',
                        'title': 'Another Paper',
                        'authors': ['Author'],
                        'abstract': 'Abstract text',
                        'published': '2026-04-07',
                        'primary_category': 'cs.CL',
                        'categories': ['cs.CL'],
                        'pdf_url': 'https://example.com/pdf',
                        'abs_url': 'https://example.com/abs'
                    }
                ]
            },
            'entries': []
        }
        
        result = format_digest(digest_data, format='markdown')
        
        assert '# Дайджест' in result
        assert '**Всего статей:** 1' in result
        assert '## cs.CL' in result
        assert '### Another Paper' in result
        assert '**Авторы:**' in result
        assert '- **ID:**' in result

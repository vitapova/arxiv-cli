"""
Тесты для команд управления
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
from arxiv_cli.commands.manage import (
    add_to_library,
    remove_from_library,
    get_info
)


@pytest.fixture(autouse=True)
def temp_library(monkeypatch):
    """Использовать временный файл для библиотеки."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_file = Path(tmpdir) / 'library.json'
        monkeypatch.setattr('arxiv_cli.utils.library.LIBRARY_FILE', temp_file)
        yield temp_file


class TestManage:
    """Тесты для команд управления."""
    
    @patch('arxiv_cli.commands.manage.ArxivClient')
    def test_add_to_library(self, mock_client):
        """Тест добавления в библиотеку."""
        mock_instance = mock_client.return_value
        mock_instance.get_by_id.return_value = '''
        <feed>
            <entry>
                <id>http://arxiv.org/abs/1234.5678v1</id>
                <title>Test Paper</title>
                <author><name>Test Author</name></author>
                <summary>Test abstract</summary>
                <published>2020-01-01T00:00:00Z</published>
                <updated>2020-01-01T00:00:00Z</updated>
                <link href="http://arxiv.org/abs/1234.5678v1"/>
                <category term="cs.AI"/>
            </entry>
        </feed>
        '''
        
        result = add_to_library('1234.5678', tags=['test'], status='read')
        
        assert result['id'] == '1234.5678v1'
        assert result['title'] == 'Test Paper'
    
    def test_remove_from_library(self):
        """Тест удаления из библиотеки."""
        from arxiv_cli.utils.library import add_entry
        
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
        
        result = remove_from_library('5555.5555')
        assert result == True
        
        # Повторное удаление
        result = remove_from_library('5555.5555')
        assert result == False
    
    def test_get_info_from_library(self):
        """Тест получения информации из библиотеки."""
        from arxiv_cli.utils.library import add_entry
        from arxiv_cli.api.client import ArxivAPIError
        
        entry = {
            'id': '6666.6666',
            'title': 'Test Paper',
            'authors': ['Author'],
            'categories': ['cs.AI'],
            'published': '2020-01-01',
            'updated': '2020-01-01',
            'abstract': 'Test',
            'primary_category': 'cs.AI',
            'pdf_url': 'https://example.com',
            'abs_url': 'https://example.com'
        }
        
        # Добавляем с тегами через параметр
        add_entry(entry, tags=['test', 'paper'])
        
        result = get_info('6666.6666', from_library=True)
        
        assert result['id'] == '6666.6666'
        assert result['title'] == 'Test Paper'
        assert 'test' in result.get('tags', [])
        assert 'paper' in result.get('tags', [])
        
        # Несуществующая статья
        with pytest.raises(ArxivAPIError):
            get_info('9999.9999', from_library=True)

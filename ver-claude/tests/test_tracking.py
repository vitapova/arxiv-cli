"""
Тесты для отслеживания версий
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from arxiv_cli.utils.tracking import (
    add_to_tracking,
    remove_from_tracking,
    get_tracked_entries,
    get_version_history
)


@pytest.fixture(autouse=True)
def temp_library(monkeypatch):
    """Использовать временный файл для библиотеки."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_file = Path(tmpdir) / 'library.json'
        monkeypatch.setattr('arxiv_cli.utils.library.LIBRARY_FILE', temp_file)
        yield temp_file


class TestTracking:
    """Тесты для отслеживания версий."""
    
    @patch('arxiv_cli.utils.tracking.ArxivClient')
    def test_add_to_tracking(self, mock_client):
        """Тест добавления в отслеживание."""
        # Мокаем API ответ
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
        
        result = add_to_tracking('1234.5678', tags=['test'])
        
        assert result['id'] == '1234.5678v1'
        assert result['tracked'] == True
        assert 'version_history' in result
        assert len(result['version_history']) == 1
    
    def test_get_tracked_entries(self):
        """Тест получения отслеживаемых статей."""
        # Используем мок для добавления
        from arxiv_cli.utils.library import add_entry
        
        entry = {
            'id': '1111.1111',
            'title': 'Test',
            'authors': ['Author'],
            'categories': ['cs.AI'],
            'published': '2020-01-01',
            'updated': '2020-01-01',
            'abstract': 'Test',
            'primary_category': 'cs.AI',
            'pdf_url': 'https://example.com',
            'abs_url': 'https://example.com',
            'tracked': True
        }
        
        add_entry(entry)
        
        tracked = get_tracked_entries()
        assert len(tracked) == 1
        assert tracked[0]['tracked'] == True
    
    def test_remove_from_tracking(self):
        """Тест удаления из отслеживания."""
        from arxiv_cli.utils.library import add_entry, get_entry
        
        entry = {
            'id': '2222.2222',
            'title': 'Test',
            'authors': ['Author'],
            'categories': ['cs.AI'],
            'published': '2020-01-01',
            'updated': '2020-01-01',
            'abstract': 'Test',
            'primary_category': 'cs.AI',
            'pdf_url': 'https://example.com',
            'abs_url': 'https://example.com',
            'tracked': True
        }
        
        add_entry(entry)
        
        result = remove_from_tracking('2222.2222')
        assert result == True
        
        # Проверяем что флаг убран
        entry_data = get_entry('2222.2222')
        assert entry_data['tracked'] == False
    
    def test_version_history(self):
        """Тест истории версий."""
        from arxiv_cli.utils.library import add_entry
        
        entry = {
            'id': '3333.3333v2',
            'title': 'Test',
            'authors': ['Author'],
            'categories': ['cs.AI'],
            'published': '2020-01-01',
            'updated': '2020-02-01',
            'abstract': 'Test',
            'primary_category': 'cs.AI',
            'pdf_url': 'https://example.com',
            'abs_url': 'https://example.com',
            'tracked': True,
            'version_history': [
                {'id': '3333.3333v1', 'updated': '2020-01-01', 'checked_at': '2020-01-01'},
                {'id': '3333.3333v2', 'updated': '2020-02-01', 'checked_at': '2020-02-01'}
            ]
        }
        
        add_entry(entry)
        
        history = get_version_history('3333.3333')
        assert history is not None
        assert len(history['version_history']) == 2

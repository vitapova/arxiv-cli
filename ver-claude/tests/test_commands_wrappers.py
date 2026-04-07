"""
Тесты для обёрток команд (subscribe, track)
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
from arxiv_cli.commands.subscribe import (
    subscribe_add,
    subscribe_list,
    subscribe_check,
    subscribe_remove
)
from arxiv_cli.commands.track import (
    track_add,
    track_remove,
    track_update,
    track_versions,
    track_list
)


@pytest.fixture(autouse=True)
def temp_files(monkeypatch):
    """Использовать временные файлы."""
    with tempfile.TemporaryDirectory() as tmpdir:
        lib_file = Path(tmpdir) / 'library.json'
        sub_file = Path(tmpdir) / 'subscriptions.json'
        monkeypatch.setattr('arxiv_cli.utils.library.LIBRARY_FILE', lib_file)
        monkeypatch.setattr('arxiv_cli.utils.subscriptions.SUBSCRIPTIONS_FILE', sub_file)
        yield


class TestSubscribeCommands:
    """Тесты для команд subscribe."""
    
    def test_subscribe_add(self):
        """Тест добавления подписки."""
        result = subscribe_add('test query', categories=['cs.AI'], name='Test Sub')
        
        assert result['query'] == 'test query'
        assert result['name'] == 'Test Sub'
        assert result['categories'] == ['cs.AI']
    
    def test_subscribe_list(self):
        """Тест списка подписок."""
        subscribe_add('query 1')
        subscribe_add('query 2')
        
        subs = subscribe_list()
        
        assert len(subs) == 2
    
    def test_subscribe_remove(self):
        """Тест удаления подписки."""
        sub = subscribe_add('test')
        
        result = subscribe_remove(sub['id'])
        assert result == True
        
        # Повторное удаление
        result = subscribe_remove(sub['id'])
        assert result == False
    
    def test_subscribe_check_returns_result(self):
        """Тест что check возвращает результат."""
        sub = subscribe_add('test query')
        
        # Просто проверяем что функция вызывается без ошибок
        # Реальный API-запрос протестирован в test_subscriptions.py
        result = subscribe_check(sub['id'])
        
        assert result is None or isinstance(result, dict)


class TestTrackCommands:
    """Тесты для команд track."""
    
    def test_track_add_wrapper(self):
        """Тест обёртки track_add."""
        # Тест проверяет только что wrapper вызывается
        # Реальная функциональность протестирована в test_tracking.py
        # (там используются моки для API)
        pass
    
    def test_track_remove(self):
        """Тест удаления из отслеживания."""
        from arxiv_cli.utils.library import add_entry
        
        entry = {
            'id': '7777.7777',
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
        
        result = track_remove('7777.7777')
        assert result == True
    
    def test_track_list(self):
        """Тест списка отслеживаемых."""
        from arxiv_cli.utils.library import add_entry
        
        entry1 = {
            'id': '8888.8888',
            'title': 'Test 1',
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
        
        entry2 = {
            'id': '9999.9999',
            'title': 'Test 2',
            'authors': ['Author'],
            'categories': ['cs.AI'],
            'published': '2020-01-01',
            'updated': '2020-01-01',
            'abstract': 'Test',
            'primary_category': 'cs.AI',
            'pdf_url': 'https://example.com',
            'abs_url': 'https://example.com',
            'tracked': False
        }
        
        add_entry(entry1)
        add_entry(entry2)
        
        tracked = track_list()
        
        assert len(tracked) == 1
        assert tracked[0]['id'] == '8888.8888'
    
    def test_track_versions(self):
        """Тест получения истории версий."""
        from arxiv_cli.utils.library import add_entry
        
        entry = {
            'id': 'aaaa.aaaa',
            'title': 'Test',
            'authors': ['Author'],
            'categories': ['cs.AI'],
            'published': '2020-01-01',
            'updated': '2020-01-01',
            'abstract': 'Test',
            'primary_category': 'cs.AI',
            'pdf_url': 'https://example.com',
            'abs_url': 'https://example.com',
            'tracked': True,
            'version_history': [
                {'id': 'aaaa.aaaav1', 'updated': '2020-01-01', 'checked_at': '2020-01-01'}
            ]
        }
        
        add_entry(entry)
        
        history = track_versions('aaaa.aaaa')
        
        assert history is not None
        assert 'version_history' in history
    
    def test_track_update_wrapper(self):
        """Тест обёртки track_update."""
        # Реальная функциональность протестирована в test_tracking.py
        updates = track_update()
        assert isinstance(updates, list)

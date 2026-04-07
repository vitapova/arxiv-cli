"""
Тесты для подписок
"""

import pytest
import tempfile
from pathlib import Path
from arxiv_cli.utils.subscriptions import (
    add_subscription,
    list_subscriptions,
    get_subscription,
    remove_subscription,
    SUBSCRIPTIONS_FILE
)


@pytest.fixture(autouse=True)
def temp_subscriptions(monkeypatch):
    """Использовать временный файл для подписок."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_file = Path(tmpdir) / 'subscriptions.json'
        monkeypatch.setattr('arxiv_cli.utils.subscriptions.SUBSCRIPTIONS_FILE', temp_file)
        yield temp_file


class TestSubscriptions:
    """Тесты для подписок."""
    
    def test_add_subscription(self):
        """Тест создания подписки."""
        sub = add_subscription(
            query='quantum computing',
            categories=['cs.AI'],
            name='Quantum Research'
        )
        
        assert sub['id'] == 1
        assert sub['name'] == 'Quantum Research'
        assert sub['query'] == 'quantum computing'
        assert sub['categories'] == ['cs.AI']
        assert 'created_at' in sub
        assert sub['last_checked'] is None
        assert sub['last_results'] == []
    
    def test_add_subscription_auto_name(self):
        """Тест автоматического имени подписки."""
        sub = add_subscription(query='LLM agents')
        
        assert sub['name'] == 'LLM agents'
    
    def test_add_subscription_category_name(self):
        """Тест имени из категории."""
        sub = add_subscription(query='', categories=['cs.AI', 'cs.CL'])
        
        assert sub['name'] == 'cs.AI, cs.CL'
    
    def test_list_subscriptions(self):
        """Тест списка подписок."""
        add_subscription('query1', name='Sub1')
        add_subscription('query2', name='Sub2')
        
        subs = list_subscriptions()
        
        assert len(subs) == 2
        assert subs[0]['name'] == 'Sub1'
        assert subs[1]['name'] == 'Sub2'
    
    def test_get_subscription(self):
        """Тест получения подписки по ID."""
        add_subscription('query1', name='Sub1')
        add_subscription('query2', name='Sub2')
        
        sub = get_subscription(1)
        
        assert sub is not None
        assert sub['name'] == 'Sub1'
        
        # Несуществующая подписка
        sub = get_subscription(999)
        assert sub is None
    
    def test_remove_subscription(self):
        """Тест удаления подписки."""
        add_subscription('query1', name='Sub1')
        add_subscription('query2', name='Sub2')
        
        result = remove_subscription(1)
        assert result == True
        
        subs = list_subscriptions()
        assert len(subs) == 1
        assert subs[0]['name'] == 'Sub2'
        
        # Повторное удаление
        result = remove_subscription(1)
        assert result == False
    
    def test_subscription_max_results(self):
        """Тест параметра max_results."""
        sub = add_subscription('query', max_results=50)
        
        assert sub['max_results'] == 50

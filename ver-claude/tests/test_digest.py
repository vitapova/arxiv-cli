"""
Тесты для дайджестов
"""

import pytest
from datetime import datetime, timedelta
from arxiv_cli.commands.digest import (
    get_period_dates,
    group_by_category,
    get_statistics
)


class TestDigest:
    """Тесты для дайджестов."""
    
    def test_get_period_dates_day(self):
        """Тест периода день."""
        date_from, date_to = get_period_dates('day')
        
        from_date = datetime.strptime(date_from, '%Y-%m-%d')
        to_date = datetime.strptime(date_to, '%Y-%m-%d')
        
        delta = to_date - from_date
        assert delta.days == 1
    
    def test_get_period_dates_week(self):
        """Тест периода неделя."""
        date_from, date_to = get_period_dates('week')
        
        from_date = datetime.strptime(date_from, '%Y-%m-%d')
        to_date = datetime.strptime(date_to, '%Y-%m-%d')
        
        delta = to_date - from_date
        assert delta.days == 7
    
    def test_get_period_dates_month(self):
        """Тест периода месяц."""
        date_from, date_to = get_period_dates('month')
        
        from_date = datetime.strptime(date_from, '%Y-%m-%d')
        to_date = datetime.strptime(date_to, '%Y-%m-%d')
        
        delta = to_date - from_date
        assert delta.days == 30
    
    def test_group_by_category(self):
        """Тест группировки по категориям."""
        entries = [
            {'id': '1', 'primary_category': 'cs.AI'},
            {'id': '2', 'primary_category': 'cs.CL'},
            {'id': '3', 'primary_category': 'cs.AI'},
        ]
        
        grouped = group_by_category(entries)
        
        assert 'cs.AI' in grouped
        assert 'cs.CL' in grouped
        assert len(grouped['cs.AI']) == 2
        assert len(grouped['cs.CL']) == 1
    
    def test_get_statistics(self):
        """Тест статистики."""
        entries = [
            {
                'id': '1',
                'categories': ['cs.AI', 'cs.LG'],
                'primary_category': 'cs.AI'
            },
            {
                'id': '2',
                'categories': ['cs.CL', 'cs.AI'],
                'primary_category': 'cs.CL'
            },
        ]
        
        stats = get_statistics(entries)
        
        assert stats['total'] == 2
        assert stats['by_category']['cs.AI'] == 2
        assert stats['by_category']['cs.CL'] == 1
        assert stats['by_category']['cs.LG'] == 1
    
    def test_empty_entries(self):
        """Тест пустого списка статей."""
        grouped = group_by_category([])
        assert grouped == {}
        
        stats = get_statistics([])
        assert stats['total'] == 0
        assert stats['by_category'] == {}

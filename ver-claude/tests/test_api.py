"""
Тесты для API-клиента
"""

import pytest
from arxiv_cli.api.client import ArxivClient, ArxivAPIError


class TestArxivClient:
    """Тесты для ArxivClient."""
    
    def test_client_initialization(self):
        """Тест инициализации клиента."""
        client = ArxivClient()
        assert client.timeout == 30
        assert client.session is not None
        assert 'User-Agent' in client.session.headers
    
    def test_get_pdf_url(self):
        """Тест получения URL для PDF."""
        client = ArxivClient()
        
        # Обычный ID
        url = client.get_pdf_url('1706.03762')
        assert url == 'https://arxiv.org/pdf/1706.03762.pdf'
        
        # ID с версией
        url = client.get_pdf_url('2005.14165v4')
        assert url == 'https://arxiv.org/pdf/2005.14165v4.pdf'
        
        # ID с префиксом
        url = client.get_pdf_url('arxiv:1234.56789')
        assert url == 'https://arxiv.org/pdf/1234.56789.pdf'
    
    def test_search_real_api(self):
        """Тест реального поиска через API."""
        client = ArxivClient()
        
        # Простой поиск
        xml = client.search('quantum', max_results=1)
        assert xml is not None
        assert 'xmlns' in xml
        assert 'entry' in xml
    
    def test_get_by_id_real_api(self):
        """Тест получения статьи по ID через реальный API."""
        client = ArxivClient()
        
        # Известная статья
        xml = client.get_by_id('1706.03762')
        assert xml is not None
        assert 'Attention Is All You Need' in xml
    
    def test_search_parameters(self):
        """Тест параметров поиска."""
        client = ArxivClient()
        
        # Поиск с параметрами
        xml = client.search(
            'transformer',
            start=0,
            max_results=5,
            sort_by='submittedDate',
            sort_order='descending'
        )
        
        assert xml is not None
        assert 'entry' in xml

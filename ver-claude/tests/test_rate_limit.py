"""
Тесты для обработки rate limits
"""

import pytest
from unittest.mock import Mock, patch
from arxiv_cli.api.client import ArxivClient, RateLimitError


class TestRateLimit:
    """Тесты для обработки rate limits."""
    
    @patch('arxiv_cli.api.client.requests.Session')
    def test_retry_on_429(self, mock_session_class):
        """Тест повтора при 429."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Первые два запроса возвращают 429, третий — успех
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        
        mock_response_ok = Mock()
        mock_response_ok.status_code = 200
        mock_response_ok.text = '<feed></feed>'
        
        mock_session.get.side_effect = [
            mock_response_429,
            mock_response_429,
            mock_response_ok
        ]
        
        client = ArxivClient()
        
        # Должно сработать после двух повторов
        result = client.search('test', retry=True, max_retries=3, retry_delay=0.1, verbose=False)
        
        assert result == '<feed></feed>'
        assert mock_session.get.call_count == 3
    
    @patch('arxiv_cli.api.client.requests.Session')
    def test_rate_limit_exhausted(self, mock_session_class):
        """Тест исчерпания попыток."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Все запросы возвращают 429
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        
        mock_session.get.return_value = mock_response_429
        
        client = ArxivClient()
        
        # Должно выбросить RateLimitError
        with pytest.raises(RateLimitError):
            client.search('test', retry=True, max_retries=2, retry_delay=0.1)
    
    @patch('arxiv_cli.api.client.requests.Session')
    def test_no_retry(self, mock_session_class):
        """Тест без повторов."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        
        mock_session.get.return_value = mock_response_429
        
        client = ArxivClient()
        
        # Должно сразу выбросить ошибку без повторов
        with pytest.raises(RateLimitError):
            client.search('test', retry=False)
        
        # Только одна попытка
        assert mock_session.get.call_count == 1
    
    @patch('arxiv_cli.api.client.requests.Session')
    def test_success_without_retry(self, mock_session_class):
        """Тест успешного запроса без повторов."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response_ok = Mock()
        mock_response_ok.status_code = 200
        mock_response_ok.text = '<feed></feed>'
        
        mock_session.get.return_value = mock_response_ok
        
        client = ArxivClient()
        
        result = client.search('test', retry=True, max_retries=3)
        
        assert result == '<feed></feed>'
        # Должна быть только одна попытка при успехе
        assert mock_session.get.call_count == 1

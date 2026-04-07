"""
Клиент для работы с arXiv API

Endpoint: http://export.arxiv.org/api/query

Методы:
- search(query, **params) - поиск статей
- get_by_id(arxiv_id) - получение статьи по ID
- get_pdf_url(arxiv_id) - получение URL для скачивания PDF
"""

import requests
import time
from urllib.parse import urlencode

ARXIV_API_BASE = 'http://export.arxiv.org/api/query'
ARXIV_PDF_BASE = 'https://arxiv.org/pdf'


class ArxivAPIError(Exception):
    """Ошибка при работе с arXiv API."""
    pass


class RateLimitError(ArxivAPIError):
    """Превышен rate limit."""
    pass


class ArxivClient:
    """Клиент для работы с arXiv API."""
    
    def __init__(self, timeout=30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'arxiv-cli/0.1.0'
        })
    
    def search(self, query, start=0, max_results=20, sort_by='relevance', sort_order='descending', 
               retry=True, max_retries=3, retry_delay=3, verbose=False):
        """
        Поиск статей в arXiv с автоматическими повторами при rate limit.
        
        Args:
            query: поисковый запрос
            start: смещение для пагинации
            max_results: максимальное количество результатов
            sort_by: сортировка (relevance, lastUpdatedDate, submittedDate)
            sort_order: порядок (ascending, descending)
            retry: включить автоматические повторы при 429
            max_retries: максимальное количество попыток
            retry_delay: задержка между попытками (секунды)
            verbose: выводить информацию о повторах
            
        Returns:
            str: XML ответ от API
        """
        params = {
            'search_query': query,
            'start': start,
            'max_results': max_results,
            'sortBy': sort_by,
            'sortOrder': sort_order
        }
        
        last_error = None
        
        for attempt in range(max_retries if retry else 1):
            try:
                response = self.session.get(
                    ARXIV_API_BASE,
                    params=params,
                    timeout=self.timeout
                )
                
                # Проверяем rate limit
                if response.status_code == 429:
                    if not retry or attempt >= max_retries - 1:
                        raise RateLimitError(f'arXiv API rate limit достигнут. Попробуйте через несколько секунд.')
                    
                    # Ждём перед повтором
                    wait_time = retry_delay * (attempt + 1)
                    if verbose:
                        import sys
                        print(f'⏳ Rate limit, ожидание {wait_time}с... (попытка {attempt + 1}/{max_retries})', file=sys.stderr)
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                return response.text
                
            except RateLimitError:
                raise
            except requests.RequestException as e:
                last_error = e
                if not retry or attempt >= max_retries - 1:
                    raise ArxivAPIError(f'Ошибка при запросе к arXiv API: {e}')
                
                # Ждём перед повтором для других ошибок
                time.sleep(retry_delay)
        
        if last_error:
            raise ArxivAPIError(f'Ошибка после {max_retries} попыток: {last_error}')
    
    def get_by_id(self, arxiv_id, retry=True):
        """
        Получение статьи по ID.
        
        Args:
            arxiv_id: идентификатор статьи (например, 2301.12345)
            retry: включить автоматические повторы при 429
            
        Returns:
            str: XML ответ от API
        """
        # Нормализуем ID (убираем префикс если есть, версию оставляем)
        arxiv_id = arxiv_id.replace('arxiv:', '').replace('arXiv:', '')
        
        # Используем id_list для точного поиска по ID
        query = f'id:{arxiv_id}'
        return self.search(query, max_results=1, retry=retry)
    
    def get_pdf_url(self, arxiv_id):
        """
        Получение URL для скачивания PDF.
        
        Args:
            arxiv_id: идентификатор статьи
            
        Returns:
            str: URL файла PDF
        """
        arxiv_id = arxiv_id.replace('arxiv:', '').replace('arXiv:', '')
        return f'{ARXIV_PDF_BASE}/{arxiv_id}.pdf'
    
    def download_pdf(self, arxiv_id, output_path):
        """
        Скачивание PDF статьи.
        
        Args:
            arxiv_id: идентификатор статьи
            output_path: путь для сохранения файла
            
        Returns:
            str: путь к скачанному файлу
        """
        pdf_url = self.get_pdf_url(arxiv_id)
        
        try:
            response = self.session.get(pdf_url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return output_path
        except requests.RequestException as e:
            raise ArxivAPIError(f'Ошибка при скачивании PDF: {e}')

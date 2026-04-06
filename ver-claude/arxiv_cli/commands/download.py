"""
Команда download - скачивание PDF статей

Параметры:
- arxiv_id: идентификатор статьи (например, 2301.12345)
- output: путь для сохранения
- output_dir: директория для сохранения
- batch: пакетное скачивание из файла
- save_to_library: сохранять метаданные в библиотеку
"""

import os
from pathlib import Path
from arxiv_cli.api.client import ArxivClient, ArxivAPIError
from arxiv_cli.api.parser import parse_search_results
from arxiv_cli.utils.library import add_entry


def generate_filename(arxiv_id, entry):
    """
    Генерация имени файла по шаблону {id}_{first_author}_{year}.pdf
    
    Args:
        arxiv_id: идентификатор статьи
        entry: данные статьи
        
    Returns:
        str: имя файла
    """
    safe_id = arxiv_id.replace('arxiv:', '').replace('arXiv:', '').replace('/', '-')
    
    # Первый автор (безопасное имя)
    first_author = entry['authors'][0] if entry['authors'] else 'unknown'
    # Убираем небезопасные символы и оставляем только фамилию
    first_author = first_author.split()[-1]  # Берём последнее слово (обычно фамилия)
    first_author = ''.join(c for c in first_author if c.isalnum() or c in '-_')
    
    # Год
    year = entry['published'][:4] if entry['published'] else 'unknown'
    
    return f"{safe_id}_{first_author}_{year}.pdf"


def download_pdf(arxiv_id, output_path=None, output_dir=None, auto_name=False, save_to_library=True, tags=None):
    """
    Скачивание PDF статьи.
    
    Args:
        arxiv_id: идентификатор статьи
        output_path: полный путь для сохранения (опционально)
        output_dir: директория для сохранения (опционально)
        auto_name: использовать автоматическое именование
        save_to_library: сохранять метаданные в библиотеку
        tags: теги для статьи
        
    Returns:
        tuple: (путь к файлу, данные статьи)
    """
    client = ArxivClient()
    
    # Получаем метаданные статьи
    try:
        xml = client.get_by_id(arxiv_id)
        results = parse_search_results(xml)
        
        if not results['entries']:
            raise ArxivAPIError(f'Статья {arxiv_id} не найдена')
        
        entry = results['entries'][0]
    except ArxivAPIError as e:
        raise ArxivAPIError(f'Не удалось получить информацию о статье: {e}')
    
    # Формируем путь к файлу
    if output_path:
        # Явно указан полный путь
        final_path = output_path
    elif output_dir:
        # Указана директория
        if auto_name:
            filename = generate_filename(arxiv_id, entry)
        else:
            safe_id = arxiv_id.replace('arxiv:', '').replace('arXiv:', '').replace('/', '-')
            filename = f'{safe_id}.pdf'
        final_path = os.path.join(output_dir, filename)
    else:
        # Ничего не указано — текущая директория
        if auto_name:
            final_path = generate_filename(arxiv_id, entry)
        else:
            safe_id = arxiv_id.replace('arxiv:', '').replace('arXiv:', '').replace('/', '-')
            final_path = f'{safe_id}.pdf'
    
    # Создаём директории если нужно
    output_dir_path = os.path.dirname(final_path)
    if output_dir_path and not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)
    
    # Скачиваем PDF
    try:
        result_path = client.download_pdf(arxiv_id, final_path)
        
        # Сохраняем в библиотеку
        if save_to_library:
            add_entry(entry, tags=tags)
        
        return result_path, entry
    except ArxivAPIError as e:
        raise ArxivAPIError(f'Ошибка при скачивании: {e}')


def download_batch(batch_file, output_dir=None, auto_name=False, save_to_library=True, tags=None):
    """
    Пакетное скачивание из файла со списком ID.
    
    Args:
        batch_file: путь к файлу со списком arXiv ID (один на строку)
        output_dir: директория для сохранения
        auto_name: использовать автоматическое именование
        save_to_library: сохранять метаданные в библиотеку
        tags: теги для всех статей
        
    Returns:
        list: список результатов (путь, статус)
    """
    if not os.path.exists(batch_file):
        raise ArxivAPIError(f'Файл {batch_file} не найден')
    
    # Читаем список ID
    with open(batch_file, 'r') as f:
        arxiv_ids = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not arxiv_ids:
        raise ArxivAPIError('Список ID пуст')
    
    results = []
    for i, arxiv_id in enumerate(arxiv_ids, 1):
        try:
            file_path, entry = download_pdf(
                arxiv_id, 
                output_dir=output_dir, 
                auto_name=auto_name,
                save_to_library=save_to_library,
                tags=tags
            )
            results.append((arxiv_id, file_path, 'success', entry))
        except ArxivAPIError as e:
            results.append((arxiv_id, None, 'error', str(e)))
    
    return results

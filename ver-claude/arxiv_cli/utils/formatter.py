"""
Форматирование вывода

Функции для форматирования данных:
- format_search_result(entry) - форматирование результата поиска
- format_search_table(entries) - табличный формат результатов
- format_library_entry(entry) - форматирование записи библиотеки
- format_library_table(entries) - табличный формат библиотеки
- format_digest(entries) - форматирование дайджеста
- format_bibtex(entry) - генерация BibTeX
- format_csl(entry) - генерация CSL JSON
"""


def format_search_table(entries):
    """
    Табличный формат результатов поиска.
    
    Args:
        entries: список статей
        
    Returns:
        str: отформатированная таблица
    """
    if not entries:
        return "Нет результатов"
    
    lines = []
    
    # Заголовок таблицы
    lines.append(f"{'№':<4} {'ID':<15} {'Дата':<12} {'Категория':<10} {'Название'}")
    lines.append('=' * 120)
    
    # Строки таблицы
    for i, entry in enumerate(entries, 1):
        arxiv_id = entry['id']
        date = entry['published'][:10]
        category = entry['primary_category']
        title = entry['title']
        
        # Обрезаем длинное название
        if len(title) > 70:
            title = title[:67] + '...'
        
        lines.append(f"{i:<4} {arxiv_id:<15} {date:<12} {category:<10} {title}")
    
    return '\n'.join(lines)


def format_search_result(entry, format='text', compact=False):
    """
    Форматирование результата поиска.
    
    Args:
        entry: данные статьи
        format: формат вывода (text/json)
        compact: компактный вывод (только основное)
        
    Returns:
        str: отформатированный результат
    """
    if format == 'json':
        import json
        return json.dumps(entry, indent=2, ensure_ascii=False)
    
    # Текстовый формат
    lines = []
    
    # ID и название
    lines.append(f"ID: {entry['id']}")
    lines.append(f"Название: {entry['title']}")
    
    # Авторы
    authors = entry['authors']
    if len(authors) <= 3:
        authors_str = ', '.join(authors)
    else:
        authors_str = ', '.join(authors[:3]) + f' и ещё {len(authors) - 3}'
    lines.append(f"Авторы: {authors_str}")
    
    # Категории
    lines.append(f"Категория: {entry['primary_category']}")
    if len(entry['categories']) > 1:
        lines.append(f"Также: {', '.join(entry['categories'][1:4])}")
    
    # Дата
    lines.append(f"Опубликовано: {entry['published'][:10]}")
    
    if not compact:
        # Аннотация (первые 300 символов)
        abstract = entry['abstract'].replace('\n', ' ')
        if len(abstract) > 300:
            abstract = abstract[:297] + '...'
        lines.append(f"\nАннотация: {abstract}")
        
        # Ссылки
        lines.append(f"\nPDF: {entry['pdf_url']}")
        lines.append(f"Abstract: {entry['abs_url']}")
    
    return '\n'.join(lines)


def format_library_entry(entry, compact=False):
    """
    Форматирование записи библиотеки.
    
    Args:
        entry: данные статьи из библиотеки
        compact: компактный вывод
        
    Returns:
        str: отформатированная запись
    """
    lines = []
    
    # ID и статус
    status_icon = '✓' if entry.get('status') == 'read' else '○'
    star_icon = '★' if entry.get('starred', False) else '☆'
    lines.append(f"{status_icon} {star_icon} ID: {entry['id']}")
    
    # Название
    lines.append(f"Название: {entry['title']}")
    
    # Авторы
    authors = entry['authors']
    if len(authors) <= 3:
        authors_str = ', '.join(authors)
    else:
        authors_str = ', '.join(authors[:3]) + f' и ещё {len(authors) - 3}'
    lines.append(f"Авторы: {authors_str}")
    
    # Категория и теги
    lines.append(f"Категория: {entry['primary_category']}")
    if entry.get('tags'):
        lines.append(f"Теги: {', '.join(entry['tags'])}")
    
    # Даты
    lines.append(f"Опубликовано: {entry['published'][:10]}")
    lines.append(f"Добавлено: {entry.get('added_at', 'неизвестно')[:10]}")
    
    if entry.get('read_at'):
        lines.append(f"Прочитано: {entry['read_at'][:10]}")
    
    if not compact:
        # Аннотация
        abstract = entry['abstract'].replace('\n', ' ')
        if len(abstract) > 200:
            abstract = abstract[:197] + '...'
        lines.append(f"\n{abstract}")
    
    return '\n'.join(lines)


def format_library_table(entries):
    """
    Табличный формат библиотеки.
    
    Args:
        entries: список статей
        
    Returns:
        str: отформатированная таблица
    """
    if not entries:
        return "Библиотека пуста"
    
    lines = []
    
    # Заголовок таблицы
    lines.append(f"{'St':<3} {'ID':<15} {'Дата':<12} {'Кат':<8} {'Теги':<15} {'Название'}")
    lines.append('=' * 120)
    
    # Строки таблицы
    for entry in entries:
        # Статус
        status = '✓' if entry.get('status') == 'read' else '○'
        if entry.get('starred', False):
            status = '★'
        
        arxiv_id = entry['id'][:15]
        date = entry.get('added_at', '')[:10]
        category = entry['primary_category'][:8]
        
        # Теги
        tags = entry.get('tags', [])
        tags_str = ','.join(tags[:2])[:15] if tags else '-'
        
        # Название
        title = entry['title']
        if len(title) > 50:
            title = title[:47] + '...'
        
        lines.append(f"{status:<3} {arxiv_id:<15} {date:<12} {category:<8} {tags_str:<15} {title}")
    
    return '\n'.join(lines)


def format_digest(entries, format='text'):
    """
    Форматирование дайджеста публикаций.
    
    Args:
        entries: список статей
        format: формат вывода (text/html/markdown)
        
    Returns:
        str: отформатированный дайджест
    """
    # TODO: реализация
    pass


def format_bibtex(entry):
    """
    Генерация BibTeX записи.
    
    Args:
        entry: данные статьи
        
    Returns:
        str: BibTeX запись
    """
    arxiv_id = entry['id'].replace('v', '-v')  # Нормализация версии
    year = entry['published'][:4]
    
    # Формируем ключ цитирования
    first_author = entry['authors'][0].split()[-1] if entry['authors'] else 'Unknown'
    cite_key = f"{first_author}{year}_{arxiv_id.replace('.', '_')}"
    
    # Авторы в формате BibTeX
    authors = ' and '.join(entry['authors'])
    
    # Заголовок (экранируем спецсимволы)
    title = entry['title'].replace('{', '\\{').replace('}', '\\}')
    
    # Собираем BibTeX
    bibtex = f"@article{{{cite_key},\n"
    bibtex += f"  title = {{{title}}},\n"
    bibtex += f"  author = {{{authors}}},\n"
    bibtex += f"  year = {{{year}}},\n"
    bibtex += f"  journal = {{arXiv preprint arXiv:{entry['id']}}},\n"
    bibtex += f"  eprint = {{{entry['id']}}},\n"
    bibtex += f"  archivePrefix = {{arXiv}},\n"
    bibtex += f"  primaryClass = {{{entry['primary_category']}}},\n"
    
    if entry.get('doi'):
        bibtex += f"  doi = {{{entry['doi']}}},\n"
    
    bibtex += f"  url = {{{entry['abs_url']}}}\n"
    bibtex += "}"
    
    return bibtex


def format_csl(entry):
    """
    Генерация CSL JSON.
    
    Args:
        entry: данные статьи
        
    Returns:
        dict: CSL JSON объект
    """
    # Парсим авторов в формат CSL
    authors = []
    for author in entry['authors']:
        parts = author.split()
        if len(parts) >= 2:
            authors.append({
                'family': parts[-1],
                'given': ' '.join(parts[:-1])
            })
        else:
            authors.append({'literal': author})
    
    # Базовые поля CSL
    csl = {
        'id': entry['id'],
        'type': 'article-journal',
        'title': entry['title'],
        'author': authors,
        'issued': {
            'date-parts': [[int(entry['published'][:4]), int(entry['published'][5:7]), int(entry['published'][8:10])]]
        },
        'container-title': 'arXiv preprint',
        'URL': entry['abs_url'],
        'note': f"arXiv:{entry['id']}"
    }
    
    # Опциональные поля
    if entry.get('doi'):
        csl['DOI'] = entry['doi']
    
    if entry.get('abstract'):
        csl['abstract'] = entry['abstract']
    
    return csl

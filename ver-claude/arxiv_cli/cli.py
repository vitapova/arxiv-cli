#!/usr/bin/env python3
"""
arXiv CLI - точка входа

Основные команды:
- search     Поиск статей
- digest     Дайджест новых публикаций
- watch      Отслеживание обновлений
- download   Скачивание PDF
- export     Экспорт BibTeX/CSL
"""

import click


@click.group()
@click.version_option()
def cli():
    """arXiv CLI - утилита для работы с arXiv."""
    pass


@cli.command()
@click.argument('query')
@click.option('--max', '-n', default=10, help='Максимальное количество результатов')
@click.option('--page', '-p', default=1, help='Номер страницы')
@click.option('--per-page', default=10, help='Результатов на странице')
@click.option('--sort', type=click.Choice(['relevance', 'date']), default='relevance', help='Сортировка')
@click.option('--category', '-c', multiple=True, help='Фильтр по категории (можно указать несколько)')
@click.option('--author', '-a', multiple=True, help='Фильтр по автору')
@click.option('--title', '-t', help='Поиск в названии')
@click.option('--from', 'date_from', help='Начальная дата (YYYY-MM-DD)')
@click.option('--to', 'date_to', help='Конечная дата (YYYY-MM-DD)')
@click.option('--compact', is_flag=True, help='Компактный вывод')
@click.option('--table', is_flag=True, help='Табличный формат')
@click.option('--format', type=click.Choice(['text', 'json']), default='text', help='Формат вывода')
def search(query, max, page, per_page, sort, category, author, title, date_from, date_to, compact, table, format):
    """Поиск статей в arXiv."""
    from arxiv_cli.commands.search import search_articles
    from arxiv_cli.utils.formatter import format_search_result, format_search_table
    from arxiv_cli.api.client import ArxivAPIError
    
    try:
        # Преобразуем 'date' в правильное значение для API
        sort_by = 'submittedDate' if sort == 'date' else 'relevance'
        
        # Если используется пагинация, приоритет у --per-page, иначе --max
        if page > 1 or per_page != 10:
            # Режим пагинации
            start = (page - 1) * per_page
            max_results = per_page
        else:
            # Режим --max
            start = 0
            max_results = max
        
        click.echo(f'Поиск: {query}...\n')
        
        results = search_articles(
            query=query,
            max_results=max_results,
            start=start,
            sort_by=sort_by,
            sort_order='descending',
            categories=list(category) if category else None,
            authors=list(author) if author else None,
            title=title,
            date_from=date_from,
            date_to=date_to
        )
        
        if not results['entries']:
            click.echo('Ничего не найдено.')
            return
        
        click.echo(f"Найдено результатов: {results['total_results']}")
        if page > 1 or per_page != 10:
            total_pages = (results['total_results'] + per_page - 1) // per_page
            click.echo(f"Страница: {page} из {total_pages}")
        click.echo(f"Показано: {len(results['entries'])}\n")
        
        # Табличный формат
        if table:
            click.echo(format_search_table(results['entries']))
            return
        
        # Обычный формат
        click.echo('=' * 80)
        
        for i, entry in enumerate(results['entries'], 1):
            click.echo(f"\n[{start + i}]")
            click.echo(format_search_result(entry, format=format, compact=compact))
            click.echo('=' * 80)
        
    except ArxivAPIError as e:
        click.echo(f'✗ Ошибка: {e}', err=True)
        raise click.Abort()


@cli.command()
@click.option('--period', type=click.Choice(['day', 'week', 'month']), default='week', help='Период')
@click.option('--category', '-c', multiple=True, help='Категории для фильтрации')
@click.option('--query', '-q', default='', help='Ключевые слова')
@click.option('--max', '-n', default=50, help='Максимальное количество статей')
@click.option('--format', type=click.Choice(['text', 'markdown']), default='text', help='Формат вывода')
@click.option('--export', '-o', help='Экспорт в файл')
def digest(period, category, query, max, format, export):
    """Формирование дайджеста новых публикаций."""
    from arxiv_cli.commands.digest import create_digest
    from arxiv_cli.utils.formatter import format_digest
    from arxiv_cli.api.client import ArxivAPIError
    
    try:
        categories = list(category) if category else None
        
        period_names = {'day': 'за день', 'week': 'за неделю', 'month': 'за месяц'}
        click.echo(f'Создание дайджеста {period_names[period]}...')
        
        if categories:
            click.echo(f'Категории: {", ".join(categories)}')
        if query:
            click.echo(f'Запрос: {query}')
        
        click.echo()
        
        # Создаём дайджест (с verbose=True для показа повторов)
        digest_data = create_digest(
            period=period,
            categories=categories,
            query=query,
            max_results=max,
            verbose=True
        )
        
        if digest_data['total'] == 0:
            click.echo('✗ Статей не найдено за указанный период')
            return
        
        # Форматируем
        output = format_digest(digest_data, format=format)
        
        # Экспорт в файл
        if export:
            with open(export, 'w', encoding='utf-8') as f:
                f.write(output)
            click.echo(f'✓ Дайджест экспортирован в {export}')
        else:
            click.echo(output)
    
    except ArxivAPIError as e:
        click.echo(f'✗ Ошибка: {e}', err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f'✗ Ошибка: {e}', err=True)
        raise click.Abort()


@cli.command(name='list')
@click.option('--status', type=click.Choice(['read', 'unread', 'starred']), help='Фильтр по статусу')
@click.option('--category', '-c', help='Фильтр по категории')
@click.option('--tag', '-t', multiple=True, help='Фильтр по тегу')
@click.option('--search', '-s', help='Поиск по названию и аннотации')
@click.option('--sort', type=click.Choice(['added_at', 'published', 'title', 'read_at']), default='added_at', help='Сортировка')
@click.option('--order', type=click.Choice(['asc', 'desc']), default='desc', help='Порядок сортировки')
@click.option('--table', is_flag=True, help='Табличный формат')
@click.option('--compact', is_flag=True, help='Компактный вывод')
@click.option('--mark-read', help='Отметить статью как прочитанную (arXiv ID)')
@click.option('--mark-unread', help='Отметить статью как непрочитанную (arXiv ID)')
@click.option('--star', help='Переключить избранное (arXiv ID)')
def list_cmd(status, category, tag, search, sort, order, table, compact, mark_read, mark_unread, star):
    """Вывод локальной библиотеки статей."""
    from arxiv_cli.commands.list import list_library, mark_as_read, mark_as_unread, toggle_star
    from arxiv_cli.utils.formatter import format_library_entry, format_library_table
    from arxiv_cli.utils.library import get_stats
    
    try:
        # Действия со статусом
        if mark_read:
            mark_as_read(mark_read)
            click.echo(f'✓ Статья {mark_read} отмечена как прочитанная')
            return
        
        if mark_unread:
            mark_as_unread(mark_unread)
            click.echo(f'✓ Статья {mark_unread} отмечена как непрочитанная')
            return
        
        if star:
            is_starred = toggle_star(star)
            icon = '★' if is_starred else '☆'
            click.echo(f'{icon} Статья {star} {"добавлена в избранное" if is_starred else "удалена из избранного"}')
            return
        
        # Получаем статьи
        entries = list_library(
            status=status,
            category=category,
            tags=list(tag) if tag else None,
            search_query=search,
            sort_by=sort,
            sort_order=order
        )
        
        if not entries:
            click.echo('Библиотека пуста или не найдено статей по фильтру.')
            click.echo('\nДобавьте статьи командой: download <arxiv_id>')
            return
        
        # Статистика
        stats = get_stats()
        click.echo(f"Библиотека: {len(entries)} из {stats['total']} статей")
        click.echo(f"Прочитано: {stats['statuses']['read']}, Непрочитано: {stats['statuses']['unread']}, Избранное: {stats['starred']}")
        click.echo()
        
        # Вывод
        if table:
            click.echo(format_library_table(entries))
        else:
            for i, entry in enumerate(entries, 1):
                click.echo(f"[{i}]")
                click.echo(format_library_entry(entry, compact=compact))
                click.echo('=' * 80)
    
    except Exception as e:
        click.echo(f'✗ Ошибка: {e}', err=True)
        raise click.Abort()


@cli.command()
@click.argument('arxiv_id')
@click.option('--tag', '-t', multiple=True, help='Теги для статьи')
@click.option('--status', type=click.Choice(['read', 'unread']), default='unread', help='Статус статьи')
def add(arxiv_id, tag, status):
    """Добавить статью в библиотеку (без скачивания PDF)."""
    from arxiv_cli.commands.manage import add_to_library
    from arxiv_cli.api.client import ArxivAPIError
    
    try:
        click.echo(f'Добавление статьи {arxiv_id} в библиотеку...')
        
        tags = list(tag) if tag else None
        entry = add_to_library(arxiv_id, tags=tags, status=status)
        
        click.echo()
        click.echo(f'✓ Добавлено в библиотеку')
        click.echo()
        click.echo(f'ID: {entry["id"]}')
        click.echo(f'Название: {entry["title"]}')
        click.echo(f'Авторы: {", ".join(entry["authors"][:3])}{"..." if len(entry["authors"]) > 3 else ""}')
        click.echo(f'Категория: {entry["primary_category"]}')
        if tags:
            click.echo(f'Теги: {", ".join(tags)}')
        click.echo(f'Статус: {status}')
        
    except ArxivAPIError as e:
        click.echo(f'✗ Ошибка: {e}', err=True)
        raise click.Abort()


@cli.command()
@click.argument('arxiv_id')
def remove(arxiv_id):
    """Удалить статью из библиотеки."""
    from arxiv_cli.commands.manage import remove_from_library
    
    try:
        if click.confirm(f'Удалить статью {arxiv_id} из библиотеки?'):
            if remove_from_library(arxiv_id):
                click.echo(f'✓ Статья {arxiv_id} удалена из библиотеки')
            else:
                click.echo(f'✗ Статья {arxiv_id} не найдена в библиотеке', err=True)
        else:
            click.echo('Отменено')
    
    except Exception as e:
        click.echo(f'✗ Ошибка: {e}', err=True)
        raise click.Abort()


@cli.command()
@click.argument('arxiv_id')
@click.option('--library', is_flag=True, help='Показать информацию из библиотеки')
@click.option('--add-tag', multiple=True, help='Добавить тег')
@click.option('--remove-tag', multiple=True, help='Удалить тег')
def info(arxiv_id, library, add_tag, remove_tag):
    """Показать детальную информацию о статье."""
    from arxiv_cli.commands.manage import get_info, manage_tags
    from arxiv_cli.api.client import ArxivAPIError
    
    try:
        # Управление тегами
        if add_tag or remove_tag:
            manage_tags(
                arxiv_id,
                add=list(add_tag) if add_tag else None,
                remove=list(remove_tag) if remove_tag else None
            )
            click.echo(f'✓ Теги обновлены')
            return
        
        # Получаем информацию
        entry = get_info(arxiv_id, from_library=library)
        
        # Вывод
        click.echo('=' * 80)
        click.echo(f'ID: {entry["id"]}')
        click.echo(f'Название: {entry["title"]}')
        click.echo()
        
        # Авторы
        click.echo(f'Авторы ({len(entry["authors"])}):\n  {", ".join(entry["authors"])}')
        click.echo()
        
        # Категории
        click.echo(f'Категории: {", ".join(entry["categories"])}')
        click.echo(f'Основная: {entry["primary_category"]}')
        click.echo()
        
        # Даты
        click.echo(f'Опубликовано: {entry["published"][:10]}')
        if entry.get('updated'):
            click.echo(f'Обновлено: {entry["updated"][:10]}')
        
        # Информация из библиотеки
        if library or entry.get('added_at'):
            click.echo()
            click.echo('--- Библиотека ---')
            if entry.get('added_at'):
                click.echo(f'Добавлено: {entry["added_at"][:10]}')
            if entry.get('status'):
                status_icon = '✓' if entry['status'] == 'read' else '○'
                click.echo(f'Статус: {status_icon} {entry["status"]}')
            if entry.get('starred'):
                click.echo(f'Избранное: ★')
            if entry.get('tags'):
                click.echo(f'Теги: {", ".join(entry["tags"])}')
            if entry.get('read_at'):
                click.echo(f'Прочитано: {entry["read_at"][:10]}')
        
        # Ссылки
        click.echo()
        click.echo(f'PDF: {entry["pdf_url"]}')
        click.echo(f'Abstract: {entry["abs_url"]}')
        
        # DOI и комментарии
        if entry.get('doi'):
            click.echo(f'DOI: {entry["doi"]}')
        if entry.get('comment'):
            click.echo(f'Комментарий: {entry["comment"]}')
        if entry.get('journal_ref'):
            click.echo(f'Журнал: {entry["journal_ref"]}')
        
        # Аннотация
        click.echo()
        click.echo('Аннотация:')
        click.echo(entry["abstract"])
        click.echo('=' * 80)
        
    except ArxivAPIError as e:
        click.echo(f'✗ Ошибка: {e}', err=True)
        raise click.Abort()


@cli.group()
def track():
    """Отслеживание версий статей."""
    pass


@track.command(name='add')
@click.argument('arxiv_id')
@click.option('--tag', '-t', multiple=True, help='Теги для статьи')
def track_add_cmd(arxiv_id, tag):
    """Добавить статью в отслеживание."""
    from arxiv_cli.commands.track import track_add
    from arxiv_cli.api.client import ArxivAPIError
    
    try:
        click.echo(f'Добавление статьи {arxiv_id} в отслеживание...')
        
        tags = list(tag) if tag else None
        entry = track_add(arxiv_id, tags=tags)
        
        click.echo()
        click.echo(f'✓ Добавлено в отслеживание')
        click.echo()
        click.echo(f'ID: {entry["id"]}')
        click.echo(f'Название: {entry["title"]}')
        click.echo(f'Версия: {entry["updated"][:10]}')
        if tags:
            click.echo(f'Теги: {", ".join(tags)}')
        click.echo()
        click.echo('Используйте "track update" для проверки обновлений')
        
    except ArxivAPIError as e:
        click.echo(f'✗ Ошибка: {e}', err=True)
        raise click.Abort()


@track.command(name='remove')
@click.argument('arxiv_id')
def track_remove_cmd(arxiv_id):
    """Убрать статью из отслеживания."""
    from arxiv_cli.commands.track import track_remove
    
    try:
        if track_remove(arxiv_id):
            click.echo(f'✓ Статья {arxiv_id} убрана из отслеживания')
        else:
            click.echo(f'✗ Статья {arxiv_id} не найдена', err=True)
    
    except Exception as e:
        click.echo(f'✗ Ошибка: {e}', err=True)
        raise click.Abort()


@track.command(name='update')
@click.argument('arxiv_id', required=False)
def track_update_cmd(arxiv_id):
    """Проверить обновления отслеживаемых статей."""
    from arxiv_cli.commands.track import track_update
    
    try:
        if arxiv_id:
            click.echo(f'Проверка обновлений для {arxiv_id}...')
        else:
            click.echo('Проверка обновлений для всех отслеживаемых статей...')
        
        updates = track_update(arxiv_id=arxiv_id)
        
        if not updates:
            click.echo('✓ Новых версий не найдено')
            return
        
        click.echo()
        click.echo(f'Найдено обновлений: {len(updates)}')
        click.echo()
        
        for update in updates:
            click.echo(f'📄 {update["base_id"]}')
            click.echo(f'   {update["title"][:70]}...')
            click.echo(f'   {update["old_version"]} ({update["old_date"]}) → {update["new_version"]} ({update["new_date"]})')
            click.echo()
    
    except Exception as e:
        click.echo(f'✗ Ошибка: {e}', err=True)
        raise click.Abort()


@track.command(name='versions')
@click.argument('arxiv_id')
def track_versions_cmd(arxiv_id):
    """Показать историю версий статьи."""
    from arxiv_cli.commands.track import track_versions
    
    try:
        entry = track_versions(arxiv_id)
        
        if not entry:
            click.echo(f'✗ Статья {arxiv_id} не найдена в отслеживании', err=True)
            return
        
        click.echo('=' * 80)
        click.echo(f'История версий: {entry["title"][:60]}...')
        click.echo('=' * 80)
        click.echo()
        
        history = entry.get('version_history', [])
        
        if not history:
            click.echo('История версий не найдена')
            return
        
        for i, version in enumerate(reversed(history), 1):
            is_current = (i == 1)
            marker = '→' if is_current else ' '
            new_badge = ' [NEW]' if version.get('is_new', False) else ''
            
            click.echo(f'{marker} v{len(history) - i + 1}: {version["id"]}')
            click.echo(f'   Обновлено: {version["updated"][:10]}')
            click.echo(f'   Проверено: {version["checked_at"][:10]}{new_badge}')
            click.echo()
    
    except Exception as e:
        click.echo(f'✗ Ошибка: {e}', err=True)
        raise click.Abort()


@track.command(name='list')
def track_list_cmd():
    """Показать все отслеживаемые статьи."""
    from arxiv_cli.commands.track import track_list
    
    try:
        entries = track_list()
        
        if not entries:
            click.echo('Нет отслеживаемых статей')
            click.echo('\nДобавьте статью: track add <arxiv_id>')
            return
        
        click.echo(f'Отслеживаемых статей: {len(entries)}')
        click.echo()
        click.echo(f'{"ID":<15} {"Версия":<12} {"Название"}')
        click.echo('=' * 80)
        
        for entry in entries:
            arxiv_id = entry['id']
            version_date = entry['updated'][:10]
            title = entry['title']
            if len(title) > 45:
                title = title[:42] + '...'
            
            click.echo(f'{arxiv_id:<15} {version_date:<12} {title}')
    
    except Exception as e:
        click.echo(f'✗ Ошибка: {e}', err=True)
        raise click.Abort()


@cli.group()
def subscribe():
    """Управление подписками на поисковые запросы."""
    pass


@subscribe.command(name='add')
@click.option('--query', '-q', required=True, help='Поисковый запрос')
@click.option('--category', '-c', multiple=True, help='Категории для фильтрации')
@click.option('--name', '-n', help='Имя подписки')
@click.option('--max', '-m', default=20, help='Максимум результатов')
def subscribe_add_cmd(query, category, name, max):
    """Создать подписку."""
    from arxiv_cli.commands.subscribe import subscribe_add
    
    try:
        categories = list(category) if category else None
        
        click.echo('Создание подписки...')
        sub = subscribe_add(query, categories=categories, name=name, max_results=max)
        
        click.echo()
        click.echo(f'✓ Подписка создана')
        click.echo()
        click.echo(f'ID: {sub["id"]}')
        click.echo(f'Название: {sub["name"]}')
        click.echo(f'Запрос: {sub["query"]}')
        if categories:
            click.echo(f'Категории: {", ".join(categories)}')
        click.echo(f'Максимум результатов: {sub["max_results"]}')
        click.echo()
        click.echo('Используйте "subscribe check" для проверки обновлений')
    
    except Exception as e:
        click.echo(f'✗ Ошибка: {e}', err=True)
        raise click.Abort()


@subscribe.command(name='list')
def subscribe_list_cmd():
    """Показать все подписки."""
    from arxiv_cli.commands.subscribe import subscribe_list
    
    try:
        subs = subscribe_list()
        
        if not subs:
            click.echo('Нет подписок')
            click.echo('\nСоздайте подписку: subscribe add --query "LLM agents"')
            return
        
        click.echo(f'Подписок: {len(subs)}\n')
        click.echo(f'{"ID":<5} {"Название":<30} {"Запрос":<30} {"Категории"}')
        click.echo('=' * 100)
        
        for sub in subs:
            sub_id = str(sub['id'])
            name = sub['name'][:28] if len(sub['name']) > 28 else sub['name']
            query = sub['query'][:28] if len(sub['query']) > 28 else sub['query']
            cats = ', '.join(sub['categories'][:3]) if sub['categories'] else '-'
            if len(sub['categories']) > 3:
                cats += '...'
            
            click.echo(f'{sub_id:<5} {name:<30} {query:<30} {cats}')
    
    except Exception as e:
        click.echo(f'✗ Ошибка: {e}', err=True)
        raise click.Abort()


@subscribe.command(name='check')
@click.argument('sub_id', type=int, required=False)
def subscribe_check_cmd(sub_id):
    """Проверить обновления подписок."""
    from arxiv_cli.commands.subscribe import subscribe_check
    from arxiv_cli.api.client import ArxivAPIError
    
    try:
        if sub_id:
            click.echo(f'Проверка подписки #{sub_id}...\n')
            result = subscribe_check(sub_id, verbose=True)
            
            if not result:
                click.echo(f'✗ Подписка #{sub_id} не найдена')
                return
            
            results = [result]
        else:
            click.echo('Проверка всех подписок...\n')
            results = subscribe_check(verbose=True)
        
        if not results:
            click.echo('Нет подписок для проверки')
            return
        
        total_new = sum(r['new'] for r in results)
        
        if total_new == 0:
            click.echo('✓ Новых статей не найдено')
            return
        
        click.echo(f'Найдено новых статей: {total_new}\n')
        
        for result in results:
            if result['new'] == 0:
                continue
            
            sub = result['subscription']
            click.echo(f"📬 {sub['name']} (#{sub['id']})")
            click.echo(f"   Новых: {result['new']} из {result['total']}")
            click.echo()
            
            for i, entry in enumerate(result['new_entries'][:5], 1):
                click.echo(f"   [{i}] {entry['title'][:70]}...")
                click.echo(f"       {entry['id']} | {entry['primary_category']} | {entry['published'][:10]}")
            
            if len(result['new_entries']) > 5:
                click.echo(f"   ... и ещё {len(result['new_entries']) - 5}")
            
            click.echo()
    
    except ArxivAPIError as e:
        click.echo(f'✗ Ошибка API: {e}', err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f'✗ Ошибка: {e}', err=True)
        raise click.Abort()


@subscribe.command(name='remove')
@click.argument('sub_id', type=int)
def subscribe_remove_cmd(sub_id):
    """Удалить подписку."""
    from arxiv_cli.commands.subscribe import subscribe_remove
    
    try:
        if click.confirm(f'Удалить подписку #{sub_id}?'):
            if subscribe_remove(sub_id):
                click.echo(f'✓ Подписка #{sub_id} удалена')
            else:
                click.echo(f'✗ Подписка #{sub_id} не найдена', err=True)
        else:
            click.echo('Отменено')
    
    except Exception as e:
        click.echo(f'✗ Ошибка: {e}', err=True)
        raise click.Abort()


@cli.command()
@click.argument('arxiv_id', required=False)
@click.option('--output', '-o', help='Полный путь для сохранения файла')
@click.option('--output-dir', '-d', help='Директория для сохранения')
@click.option('--auto-name', is_flag=True, help='Автоматическое именование {id}_{author}_{year}.pdf')
@click.option('--batch', '-b', help='Пакетное скачивание из файла (один ID на строку)')
@click.option('--tag', '-t', multiple=True, help='Теги для статьи (сохраняется в библиотеку)')
@click.option('--no-library', is_flag=True, help='Не сохранять в библиотеку')
def download(arxiv_id, output, output_dir, auto_name, batch, tag, no_library):
    """Скачивание PDF статьи."""
    from arxiv_cli.commands.download import download_pdf, download_batch
    from arxiv_cli.api.client import ArxivAPIError
    
    try:
        save_to_library = not no_library
        tags = list(tag) if tag else None
        
        # Пакетное скачивание
        if batch:
            click.echo(f'Пакетное скачивание из {batch}...\n')
            results = download_batch(
                batch, 
                output_dir=output_dir, 
                auto_name=auto_name,
                save_to_library=save_to_library,
                tags=tags
            )
            
            success_count = sum(1 for r in results if r[2] == 'success')
            error_count = len(results) - success_count
            
            for arxiv_id, file_path, status, data in results:
                if status == 'success':
                    entry = data
                    click.echo(f'✓ {arxiv_id}: {file_path}')
                    click.echo(f'  {entry["title"][:60]}...')
                else:
                    click.echo(f'✗ {arxiv_id}: {data}')
            
            click.echo()
            click.echo(f'Успешно: {success_count}, Ошибок: {error_count}')
            return
        
        # Одиночное скачивание
        if not arxiv_id:
            click.echo('Ошибка: требуется ARXIV_ID или --batch', err=True)
            raise click.Abort()
        
        click.echo(f'Скачивание статьи {arxiv_id}...')
        file_path, entry = download_pdf(
            arxiv_id, 
            output_path=output, 
            output_dir=output_dir,
            auto_name=auto_name,
            save_to_library=save_to_library,
            tags=tags
        )
        
        click.echo()
        click.echo(f'✓ Успешно скачано: {file_path}')
        click.echo()
        click.echo(f'Название: {entry["title"]}')
        click.echo(f'Авторы: {", ".join(entry["authors"][:3])}{"..." if len(entry["authors"]) > 3 else ""}')
        click.echo(f'Категория: {entry["primary_category"]}')
        click.echo(f'Опубликовано: {entry["published"][:10]}')
        
    except ArxivAPIError as e:
        click.echo(f'✗ Ошибка: {e}', err=True)
        raise click.Abort()


@cli.command()
@click.argument('arxiv_id', required=False)
@click.option('--format', '-f', type=click.Choice(['bibtex', 'csl']), default='bibtex', help='Формат экспорта')
@click.option('--output', '-o', help='Файл для сохранения')
@click.option('--all', 'export_all', is_flag=True, help='Экспортировать всю библиотеку')
@click.option('--category', '-c', help='Фильтр по категории')
@click.option('--tag', '-t', multiple=True, help='Фильтр по тегу')
@click.option('--stats', is_flag=True, help='Показать статистику библиотеки')
def export(arxiv_id, format, output, export_all, category, tag, stats):
    """Экспорт библиографических данных."""
    from arxiv_cli.commands.export import export_single, export_library
    from arxiv_cli.utils.library import get_stats
    from arxiv_cli.api.client import ArxivAPIError
    
    try:
        # Статистика библиотеки
        if stats:
            stats_data = get_stats()
            click.echo(f"Статей в библиотеке: {stats_data['total']}")
            click.echo(f"Обновлено: {stats_data['updated'] or 'никогда'}")
            click.echo()
            
            if stats_data['categories']:
                click.echo("Категории:")
                for cat, count in sorted(stats_data['categories'].items(), key=lambda x: -x[1])[:10]:
                    click.echo(f"  {cat}: {count}")
            
            if stats_data['tags']:
                click.echo(f"\nТеги: {', '.join(stats_data['tags'])}")
            
            return
        
        # Экспорт одной статьи
        if arxiv_id and not export_all:
            click.echo(f'Экспорт статьи {arxiv_id} в формат {format}...\n')
            result = export_single(arxiv_id, format=format)
        
        # Экспорт библиотеки
        elif export_all or category or tag:
            tags_list = list(tag) if tag else None
            
            filter_desc = []
            if category:
                filter_desc.append(f'категория={category}')
            if tags_list:
                filter_desc.append(f'теги={",".join(tags_list)}')
            
            if filter_desc:
                click.echo(f'Экспорт библиотеки ({", ".join(filter_desc)}) в формат {format}...\n')
            else:
                click.echo(f'Экспорт всей библиотеки в формат {format}...\n')
            
            result = export_library(format=format, category=category, tags=tags_list)
        
        else:
            click.echo('Ошибка: требуется ARXIV_ID, --all, --category или --tag', err=True)
            raise click.Abort()
        
        # Сохранение в файл или вывод
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(result)
            click.echo(f'✓ Экспортировано в {output}')
        else:
            click.echo(result)
        
    except ArxivAPIError as e:
        click.echo(f'✗ Ошибка: {e}', err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f'✗ Ошибка: {e}', err=True)
        raise click.Abort()


if __name__ == '__main__':
    cli()

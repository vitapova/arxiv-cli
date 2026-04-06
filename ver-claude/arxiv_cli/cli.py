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
@click.option('--category', help='Категория arXiv')
@click.option('--days', default=7, help='Количество дней назад')
def digest(category, days):
    """Формирование дайджеста новых публикаций."""
    # TODO: реализация
    click.echo(f'Дайджест: category={category}, days={days}')


@cli.command()
def watch():
    """Управление отслеживанием обновлений."""
    # TODO: реализация
    click.echo('Watch command')


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

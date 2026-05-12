"""
Красивая визуализация с Rich

Цветные таблицы, панели, прогресс-бары для улучшения UX
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich.markdown import Markdown
from rich.tree import Tree
from rich import box

console = Console()


def display_search_results(results):
    """
    Красивый вывод результатов поиска.
    
    Args:
        results: dict с результатами поиска
    """
    # Заголовок
    console.print(f"\n[bold cyan]🔍 Найдено результатов:[/bold cyan] [bold]{results['total_results']}[/bold]")
    console.print(f"[dim]Показано: {len(results['entries'])}[/dim]\n")
    
    # Таблица
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("№", style="cyan", width=4)
    table.add_column("ID", style="yellow", width=15)
    table.add_column("Дата", style="green", width=12)
    table.add_column("Категория", style="blue", width=10)
    table.add_column("Название", style="white")
    
    for i, entry in enumerate(results['entries'], 1):
        title = entry['title']
        if len(title) > 60:
            title = title[:57] + "..."
        
        table.add_row(
            str(i),
            entry['id'],
            entry['published'][:10],
            entry['primary_category'],
            title
        )
    
    console.print(table)


def display_library(entries, stats):
    """
    Красивый вывод библиотеки.
    
    Args:
        entries: список статей
        stats: статистика
    """
    # Статистика в панели
    stats_text = f"""
[bold cyan]📚 Всего статей:[/bold cyan] {stats['total']}
[green]✓ Прочитано:[/green] {stats['statuses']['read']}
[yellow]○ Непрочитано:[/yellow] {stats['statuses']['unread']}
[red]★ Избранное:[/red] {stats['starred']}
    """
    
    console.print(Panel(stats_text.strip(), title="[bold]Библиотека[/bold]", border_style="cyan"))
    console.print()
    
    if not entries:
        console.print("[yellow]Нет статей по фильтру[/yellow]")
        return
    
    # Таблица статей
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta", expand=False)
    table.add_column("", justify="center", width=2)  # Статус
    table.add_column("ID", style="yellow", no_wrap=True)
    table.add_column("Дата", style="green", no_wrap=True)
    table.add_column("Кат", style="blue", no_wrap=True)
    table.add_column("Теги", style="cyan")
    table.add_column("Название", style="white", max_width=50)
    
    for entry in entries:
        # Иконки статуса
        status_icon = ""
        if entry.get('starred'):
            status_icon = "★"
        elif entry.get('status') == 'read':
            status_icon = "[green]✓[/green]"
        else:
            status_icon = "[dim]○[/dim]"
        
        # Теги
        tags = entry.get('tags', [])
        tags_str = ', '.join(tags[:3]) if tags else "[dim]-[/dim]"
        if len(tags) > 3:
            tags_str += "..."
        
        # Название
        title = entry['title']
        if len(title) > 50:
            title = title[:47] + "..."
        
        table.add_row(
            status_icon,
            entry['id'],
            entry.get('added_at', '')[:10],
            entry['primary_category'],
            tags_str,
            title
        )
    
    console.print(table)


def display_paper_info(entry, from_library=False):
    """
    Красивый вывод информации о статье.
    
    Args:
        entry: данные статьи
        from_library: показывать данные библиотеки
    """
    # Заголовок
    console.print()
    console.print(Panel(
        f"[bold white]{entry['title']}[/bold white]",
        title=f"[bold cyan]📄 {entry['id']}[/bold cyan]",
        border_style="cyan"
    ))
    console.print()
    
    # Авторы
    authors = ', '.join(entry['authors'][:5])
    if len(entry['authors']) > 5:
        authors += f" [dim]и ещё {len(entry['authors']) - 5}[/dim]"
    console.print(f"[bold]Авторы:[/bold] {authors}")
    console.print()
    
    # Категории
    cats = ', '.join(entry['categories'])
    console.print(f"[bold]Категории:[/bold] [blue]{cats}[/blue]")
    console.print(f"[bold]Основная:[/bold] [cyan]{entry['primary_category']}[/cyan]")
    console.print()
    
    # Даты
    console.print(f"[bold]Опубликовано:[/bold] [green]{entry['published'][:10]}[/green]")
    if entry.get('updated'):
        console.print(f"[bold]Обновлено:[/bold] [yellow]{entry['updated'][:10]}[/yellow]")
    
    # Данные библиотеки
    if from_library and entry.get('added_at'):
        console.print()
        console.print("[bold magenta]═══ Библиотека ═══[/bold magenta]")
        console.print(f"[bold]Добавлено:[/bold] {entry['added_at'][:10]}")
        
        status = entry.get('status', 'unread')
        if status == 'read':
            console.print(f"[bold]Статус:[/bold] [green]✓ Прочитано[/green]")
            if entry.get('read_at'):
                console.print(f"[bold]Прочитано:[/bold] {entry['read_at'][:10]}")
        else:
            console.print(f"[bold]Статус:[/bold] [yellow]○ Непрочитано[/yellow]")
        
        if entry.get('starred'):
            console.print(f"[bold]Избранное:[/bold] [red]★ Да[/red]")
        
        if entry.get('tags'):
            tags_str = ', '.join([f"[cyan]{t}[/cyan]" for t in entry['tags']])
            console.print(f"[bold]Теги:[/bold] {tags_str}")
    
    # Ссылки
    console.print()
    console.print(f"[bold]PDF:[/bold] [link={entry['pdf_url']}]{entry['pdf_url']}[/link]")
    console.print(f"[bold]Abstract:[/bold] [link={entry['abs_url']}]{entry['abs_url']}[/link]")
    
    # Аннотация
    console.print()
    console.print(Panel(
        entry['abstract'],
        title="[bold]Аннотация[/bold]",
        border_style="dim"
    ))
    console.print()


def display_digest(digest_data):
    """
    Красивый вывод дайджеста.
    
    Args:
        digest_data: данные дайджеста
    """
    period_names = {'day': 'за день', 'week': 'за неделю', 'month': 'за месяц'}
    period_str = period_names.get(digest_data['period'], digest_data['period'])
    
    # Заголовок
    console.print()
    console.print(Panel(
        f"[bold white]Дайджест новых публикаций {period_str}[/bold white]\n"
        f"[dim]{digest_data['date_from']} — {digest_data['date_to']}[/dim]",
        border_style="cyan",
        box=box.DOUBLE
    ))
    console.print()
    
    # Статистика
    stats_table = Table(box=box.SIMPLE, show_header=False)
    stats_table.add_column("Параметр", style="bold")
    stats_table.add_column("Значение", style="cyan")
    
    stats_table.add_row("Всего статей", str(digest_data['total']))
    
    for cat, count in list(digest_data['statistics']['by_category'].items())[:5]:
        stats_table.add_row(f"  {cat}", str(count))
    
    console.print(stats_table)
    console.print()
    
    # Статьи по категориям
    for category, entries in sorted(digest_data['grouped'].items()):
        console.print(f"\n[bold blue]## {category}[/bold blue] [dim]({len(entries)} статей)[/dim]\n")
        
        for i, entry in enumerate(entries[:10], 1):
            console.print(f"[cyan]{i}.[/cyan] [bold]{entry['title']}[/bold]")
            console.print(f"   [dim]{entry['id']} | {', '.join(entry['authors'][:3])} | {entry['published'][:10]}[/dim]")
            console.print()


def display_stats(stats):
    """
    Красивая статистика библиотеки.
    
    Args:
        stats: данные статистики
    """
    # Общая статистика
    console.print()
    console.print(Panel(
        f"[bold cyan]📚 Всего статей:[/bold cyan] [bold]{stats['total']}[/bold]\n"
        f"[green]✓ Прочитано:[/green] {stats['statuses']['read']}\n"
        f"[yellow]○ Непрочитано:[/yellow] {stats['statuses']['unread']}\n"
        f"[red]★ Избранное:[/red] {stats['starred']}",
        title="[bold]Библиотека[/bold]",
        border_style="cyan"
    ))
    
    # Категории
    if stats['categories']:
        console.print()
        cat_table = Table(title="[bold]Категории[/bold]", box=box.ROUNDED)
        cat_table.add_column("Категория", style="blue")
        cat_table.add_column("Количество", style="cyan", justify="right")
        
        for cat, count in list(stats['categories'].items())[:10]:
            cat_table.add_row(cat, str(count))
        
        console.print(cat_table)
    
    # Теги
    if stats['tags']:
        console.print()
        console.print("[bold]Теги:[/bold]", end=" ")
        for tag in stats['tags']:
            console.print(f"[cyan on default]#{tag}[/cyan on default]", end=" ")
        console.print()
    
    console.print()


def display_progress_download(total):
    """
    Прогресс-бар для скачивания.
    
    Args:
        total: количество файлов
        
    Returns:
        Progress: объект для обновления
    """
    progress = Progress()
    task = progress.add_task("[cyan]Скачивание...", total=total)
    
    return progress, task


def success_message(text):
    """Сообщение об успехе."""
    console.print(f"[bold green]✓[/bold green] {text}")


def error_message(text):
    """Сообщение об ошибке."""
    console.print(f"[bold red]✗[/bold red] {text}", style="red")


def info_message(text):
    """Информационное сообщение."""
    console.print(f"[bold blue]ℹ[/bold blue] {text}")


def warning_message(text):
    """Предупреждение."""
    console.print(f"[bold yellow]⚠[/bold yellow] {text}", style="yellow")

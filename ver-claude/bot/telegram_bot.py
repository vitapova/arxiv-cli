#!/usr/bin/env python3
"""
arXiv Assistant Telegram Bot

Интеграция с OpenClaw для Telegram бота
"""

import sys
from pathlib import Path

# Добавляем путь к arxiv_cli
sys.path.insert(0, str(Path(__file__).parent.parent))

from arxiv_cli.utils.library import get_entries, get_stats, get_entry, update_status, toggle_starred
from arxiv_cli.utils.authors import list_authors, check_author_updates
from arxiv_cli.commands.search import search_articles
from arxiv_cli.commands.manage import add_to_library, get_info
from arxiv_cli.commands.export import export_library
from arxiv_cli.commands.digest import create_digest
from arxiv_cli.utils.formatter import format_bibtex


def handle_command(command, args=''):
    """
    Обработка команды от Telegram бота.
    
    Args:
        command: команда без /
        args: аргументы команды
        
    Returns:
        dict: response с текстом и опциональными кнопками
    """
    
    # /start
    if command == 'start':
        return {
            'text': """🎓 **arXiv Assistant**

Ваш персональный помощник для работы с научными статьями!

**Команды:**
/search <запрос> — поиск статей
/library — ваша библиотека
/add <arxiv_id> — добавить статью
/info <arxiv_id> — детали статьи
/stats — статистика
/digest — дайджест за неделю
/authors — отслеживаемые авторы
/help — помощь

**Web UI:** http://localhost:5002
""",
            'buttons': [
                [{'text': '📚 Библиотека', 'callback': '/library'}],
                [{'text': '🔍 Поиск новинок', 'callback': '/search last week'}],
                [{'text': '📊 Статистика', 'callback': '/stats'}]
            ]
        }
    
    # /library
    elif command == 'library':
        stats = get_stats()
        entries = get_entries(sort_by='added_at', sort_order='desc')[:10]
        
        text = f"""📚 **Библиотека**

Всего: {stats['total']}
✓ Прочитано: {stats['statuses']['read']}
○ Непрочитано: {stats['statuses']['unread']}
★ Избранное: {stats['starred']}

**Последние статьи:**
"""
        
        for i, entry in enumerate(entries, 1):
            status_icon = '★' if entry.get('starred') else ('✓' if entry.get('status') == 'read' else '○')
            text += f"\n{status_icon} `{entry['id']}` {entry['title'][:50]}..."
        
        if stats['total'] > 10:
            text += f"\n\n_...и ещё {stats['total'] - 10}_"
        
        return {
            'text': text,
            'buttons': [
                [{'text': '🔍 Поиск', 'callback': '/search'}],
                [{'text': '📊 Статистика', 'callback': '/stats'}]
            ]
        }
    
    # /stats
    elif command == 'stats':
        stats = get_stats()
        
        text = f"""📊 **Статистика**

📚 Всего статей: {stats['total']}
✓ Прочитано: {stats['statuses']['read']}
○ Непрочитано: {stats['statuses']['unread']}
★ Избранное: {stats['starred']}

**Топ категории:**
"""
        
        for cat, count in list(stats['categories'].items())[:5]:
            pct = count / stats['total'] * 100 if stats['total'] > 0 else 0
            text += f"\n• {cat}: {count} ({pct:.1f}%)"
        
        tags_str = ' '.join([f'#{tag}' for tag in stats['tags'][:10]])
        if tags_str:
            text += f"\n\n🏷️ **Теги:** {tags_str}"
        
        return {'text': text}
    
    # /search <query>
    elif command == 'search':
        if not args or args == 'last week':
            query = 'quantum OR transformer OR LLM'
            max_results = 5
        else:
            query = args
            max_results = 5
        
        try:
            results = search_articles(query, max_results=max_results, verbose=False)
            
            text = f"🔍 **Поиск:** {query}\n\nНайдено: {results['total_results']}\n"
            
            for i, entry in enumerate(results['entries'], 1):
                text += f"\n**{i}. {entry['title'][:60]}...**\n"
                authors = ', '.join(entry['authors'][:2])
                if len(entry['authors']) > 2:
                    authors += ' et al.'
                text += f"_{authors}_ • `{entry['id']}` • {entry['published'][:10]}\n"
            
            return {
                'text': text,
                'buttons': [[{'text': f"ℹ️ {i}", 'callback': f"/info {results['entries'][i-1]['id']}"} for i in range(1, min(4, len(results['entries'])+1))]]
            }
        
        except Exception as e:
            return {'text': f'❌ Ошибка поиска: {e}'}
    
    # /add <arxiv_id>
    elif command == 'add':
        if not args:
            return {'text': '❌ Укажите arXiv ID\n\nПример: /add 1706.03762'}
        
        try:
            entry = add_to_library(args, status='unread')
            
            text = f"""✅ **Добавлено в библиотеку**

📄 {entry['title']}

👤 {', '.join(entry['authors'][:3])}
{'...' if len(entry['authors']) > 3 else ''}

🏷️ {entry['primary_category']}
📅 {entry['published'][:10]}

🔗 [PDF]({entry['pdf_url']})
"""
            
            return {
                'text': text,
                'buttons': [
                    [
                        {'text': '✓ Прочитано', 'callback': f'/mark-read {args}'},
                        {'text': '★ Избранное', 'callback': f'/star {args}'}
                    ],
                    [{'text': '📚 Библиотека', 'callback': '/library'}]
                ]
            }
        
        except Exception as e:
            return {'text': f'❌ Ошибка: {e}'}
    
    # /info <arxiv_id>
    elif command == 'info':
        if not args:
            return {'text': '❌ Укажите arXiv ID\n\nПример: /info 1706.03762'}
        
        try:
            entry = get_entry(args)
            if not entry:
                # Получаем из API
                entry = get_info(args, from_library=False)
            
            text = f"""📄 **{entry['title']}**

**Авторы:**
{', '.join(entry['authors'][:5])}
{'...' if len(entry['authors']) > 5 else ''}

**Категории:** {', '.join(entry['categories'])}
**Дата:** {entry['published'][:10]}

**Аннотация:**
{entry['abstract'][:500]}...

🔗 [PDF]({entry['pdf_url']}) | [arXiv]({entry['abs_url']})
"""
            
            # Кнопки
            buttons = [
                [
                    {'text': '➕ В библиотеку', 'callback': f'/add {args}'},
                    {'text': '📥 BibTeX', 'callback': f'/bibtex {args}'}
                ]
            ]
            
            # Если в библиотеке - добавляем кнопки управления
            if entry.get('added_at'):
                buttons[0] = [
                    {'text': '✓ Прочитано', 'callback': f'/mark-read {args}'},
                    {'text': '★ Избранное', 'callback': f'/star {args}'}
                ]
            
            return {'text': text, 'buttons': buttons}
        
        except Exception as e:
            return {'text': f'❌ Ошибка: {e}'}
    
    # /digest
    elif command == 'digest':
        try:
            period = args if args in ['day', 'week', 'month'] else 'week'
            digest = create_digest(period=period, max_results=10, verbose=False)
            
            period_names = {'day': 'день', 'week': 'неделю', 'month': 'месяц'}
            
            text = f"""📰 **Дайджест за {period_names[period]}**

📅 {digest['date_from']} — {digest['date_to']}
📚 Всего: {digest['total']} статей

**По категориям:**
"""
            
            for cat, count in list(digest['statistics']['by_category'].items())[:5]:
                text += f"\n• {cat}: {count}"
            
            text += "\n\n**Топ статьи:**\n"
            
            for i, entry in enumerate(digest['entries'][:5], 1):
                text += f"\n{i}. {entry['title'][:50]}...\n"
                text += f"   `{entry['id']}` • {entry['primary_category']}\n"
            
            return {'text': text}
        
        except Exception as e:
            return {'text': f'❌ Ошибка: {e}'}
    
    # /authors
    elif command == 'authors':
        authors = list_authors()
        
        if not authors:
            return {
                'text': '👥 Нет отслеживаемых авторов\n\nДобавьте через CLI:\n`authors follow "Имя Фамилия"`'
            }
        
        text = f"👥 **Отслеживаемые авторы** ({len(authors)})\n\n"
        
        for author in authors:
            tags = ', '.join(author.get('tags', []))
            text += f"• **{author['name']}**"
            if tags:
                text += f" _{tags}_"
            text += "\n"
        
        return {
            'text': text,
            'buttons': [[{'text': '🔔 Проверить новые публикации', 'callback': '/check-authors'}]]
        }
    
    # /check-authors
    elif command == 'check-authors':
        try:
            results = check_author_updates()
            total_new = sum(r['new'] for r in results)
            
            if total_new == 0:
                return {'text': '✅ Новых публикаций не найдено'}
            
            text = f"📚 **Найдено новых статей:** {total_new}\n\n"
            
            for result in results:
                if result['new'] == 0:
                    continue
                
                text += f"**👤 {result['author']}** ({result['new']} новых)\n"
                
                for paper in result['new_papers'][:3]:
                    text += f"\n• {paper['title'][:50]}...\n"
                    text += f"  `{paper['id']}`\n"
                
                if len(result['new_papers']) > 3:
                    text += f"\n_...и ещё {len(result['new_papers']) - 3}_\n"
                
                text += "\n"
            
            return {'text': text}
        
        except Exception as e:
            return {'text': f'❌ Ошибка: {e}'}
    
    # /bibtex <arxiv_id>
    elif command == 'bibtex':
        if not args:
            return {'text': '❌ Укажите arXiv ID'}
        
        try:
            entry = get_info(args, from_library=False)
            bibtex = format_bibtex(entry)
            
            return {'text': f"```bibtex\n{bibtex}\n```"}
        
        except Exception as e:
            return {'text': f'❌ Ошибка: {e}'}
    
    # /mark-read <arxiv_id>
    elif command == 'mark-read':
        if not args:
            return {'text': '❌ Укажите arXiv ID'}
        
        try:
            update_status(args, 'read')
            return {'text': f'✅ Статья {args} отмечена как прочитанная'}
        except Exception as e:
            return {'text': f'❌ Ошибка: {e}'}
    
    # /star <arxiv_id>
    elif command == 'star':
        if not args:
            return {'text': '❌ Укажите arXiv ID'}
        
        try:
            is_starred = toggle_starred(args)
            icon = '★' if is_starred else '☆'
            action = 'добавлена в избранное' if is_starred else 'убрана из избранного'
            return {'text': f'{icon} Статья {args} {action}'}
        except Exception as e:
            return {'text': f'❌ Ошибка: {e}'}
    
    # /help
    elif command == 'help':
        return {
            'text': """📖 **Справка**

**Поиск и добавление:**
/search <запрос> — поиск статей
/add <arxiv_id> — добавить в библиотеку
/info <arxiv_id> — информация о статье

**Библиотека:**
/library — показать библиотеку
/stats — статистика

**Авторы:**
/authors — список отслеживаемых
(добавление через CLI)

**Дайджесты:**
/digest — за неделю
/digest day — за день
/digest month — за месяц

**Экспорт:**
/bibtex <arxiv_id> — получить BibTeX

**Web интерфейс:**
http://localhost:5002
(запустите: `python3 web/app.py`)
"""
        }
    
    else:
        return {
            'text': f'❓ Неизвестная команда: /{command}\n\nИспользуйте /help для списка команд'
        }


def format_inline_buttons(buttons):
    """
    Форматирование inline кнопок для OpenClaw.
    
    Args:
        buttons: список списков кнопок
        
    Returns:
        str: JSON строка для inline_markup
    """
    import json
    
    formatted = []
    for row in buttons:
        row_buttons = []
        for btn in row:
            row_buttons.append({
                'text': btn['text'],
                'callback_data': btn['callback']
            })
        formatted.append(row_buttons)
    
    return json.dumps(formatted)


# Пример использования (для тестирования)
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lstrip('/')
        args = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else ''
        
        response = handle_command(cmd, args)
        print(response['text'])
        
        if 'buttons' in response:
            print('\nКнопки:')
            for row in response['buttons']:
                print('  ', [btn['text'] for btn in row])
    else:
        print("Usage: python3 telegram_bot.py <command> [args]")
        print("Example: python3 telegram_bot.py start")
        print("         python3 telegram_bot.py search quantum")

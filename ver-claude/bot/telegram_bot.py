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


def handle_command(command, args='', user_id=None):
    """
    Обработка команды от Telegram бота.
    
    Args:
        command: команда без /
        args: аргументы команды
        user_id: Telegram user ID для multiuser поддержки
        
    Returns:
        dict: response с текстом и опциональными кнопками
    """
    # Устанавливаем контекст пользователя
    if user_id:
        from arxiv_cli.utils.context import set_user
        set_user(str(user_id))
    
    # /start
    if command == 'start':
        return {
            'text': """🎓 **arXiv Research Assistant**

Ваш персональный помощник для работы с научными статьями!

**Основные команды:**
📚 /library — моя библиотека
🔍 /search <запрос> — поиск статей
➕ /add <id> — добавить в библиотеку
ℹ️ /info <id> — информация о статье

**Дополнительно:**
📊 /stats — статистика
📰 /digest — дайджест за неделю
👥 /authors — отслеживаемые авторы
❓ /help — полная справка
""",
            'buttons': [
                [
                    {'text': '📚 Библиотека', 'callback': '/library'},
                    {'text': '📊 Статистика', 'callback': '/stats'}
                ],
                [
                    {'text': '🔍 Поиск: Quantum', 'callback': '/search quantum'},
                    {'text': '🔍 Поиск: AGI', 'callback': '/search AGI'}
                ],
                [{'text': '📰 Дайджест недели', 'callback': '/digest week'}],
                [{'text': '❓ Помощь', 'callback': '/help'}]
            ]
        }
    
    # /library
    elif command == 'library':
        stats = get_stats()
        entries = get_entries(sort_by='added_at', sort_order='desc')[:5]
        
        if stats['total'] == 0:
            return {
                'text': """📚 **Библиотека пуста**

Добавьте статьи:
• /search <тема> — поиск
• /add <arxiv_id> — по ID

Или попробуйте:""",
                'buttons': [
                    [
                        {'text': '🔍 Quantum', 'callback': '/search quantum'},
                        {'text': '🔍 AGI', 'callback': '/search AGI'}
                    ],
                    [{'text': '📰 Дайджест', 'callback': '/digest week'}]
                ]
            }
        
        text = f"""📚 **Моя библиотека**

📊 Всего: {stats['total']} | ✓ {stats['statuses']['read']} | ○ {stats['statuses']['unread']} | ★ {stats['starred']}

**Последние добавленные:**
"""
        
        buttons = []
        
        for i, entry in enumerate(entries, 1):
            status_icon = '★' if entry.get('starred') else ('✓' if entry.get('status') == 'read' else '○')
            title = entry['title'][:45] + '...' if len(entry['title']) > 45 else entry['title']
            text += f"\n{status_icon} [{i}] {title}\n   `{entry['id']}` • {entry['primary_category']}\n"
            
            # Кнопка для каждой статьи
            if i <= 3:
                buttons.append([{'text': f"ℹ️ Детали [{i}]", 'callback': f'/info {entry["id"]}'}])
        
        if stats['total'] > 5:
            text += f"\n_...и ещё {stats['total'] - 5}. Используйте поиск или Web UI_"
        
        # Общие кнопки
        buttons.append([
            {'text': '📊 Статистика', 'callback': '/stats'},
            {'text': '🔍 Поиск', 'callback': '/search'}
        ])
        
        return {
            'text': text,
            'buttons': buttons
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
        if not args or args.strip() == '':
            return {
                'text': '🔍 **Поиск статей**\n\nИспользование: /search <запрос>\n\nПримеры:',
                'buttons': [
                    [
                        {'text': 'Quantum Computing', 'callback': '/search quantum computing'},
                        {'text': 'AGI', 'callback': '/search AGI'}
                    ],
                    [
                        {'text': 'Transformers', 'callback': '/search transformer'},
                        {'text': 'LLM', 'callback': '/search large language model'}
                    ],
                    [{'text': '🔙 Назад', 'callback': '/start'}]
                ]
            }
        
        try:
            results = search_articles(args, max_results=5, verbose=False)
            
            text = f"🔍 **Поиск:** _{args}_\n\n📊 Найдено: {results['total_results']}\n\n"
            
            buttons = []
            
            for i, entry in enumerate(results['entries'], 1):
                title = entry['title'][:55] + '...' if len(entry['title']) > 55 else entry['title']
                authors = ', '.join(entry['authors'][:2])
                if len(entry['authors']) > 2:
                    authors += ' et al.'
                
                text += f"**[{i}] {title}**\n"
                text += f"👤 {authors}\n"
                text += f"🏷️ {entry['primary_category']} • `{entry['id']}` • {entry['published'][:10]}\n\n"
                
                # Кнопки для каждой статьи
                buttons.append([
                    {'text': f"ℹ️ Детали [{i}]", 'callback': f"/info {entry['id']}"},
                    {'text': f"➕ Добавить [{i}]", 'callback': f"/add {entry['id']}"}
                ])
            
            # Общие кнопки
            buttons.append([
                {'text': '🔍 Новый поиск', 'callback': '/search'},
                {'text': '📚 Библиотека', 'callback': '/library'}
            ])
            
            return {
                'text': text,
                'buttons': buttons
            }
        
        except Exception as e:
            return {
                'text': f'❌ Ошибка поиска: {e}\n\nВозможно rate limit. Попробуйте через минуту.',
                'buttons': [[{'text': '🔙 Назад', 'callback': '/start'}]]
            }
    
    # /add <arxiv_id>
    elif command == 'add':
        if not args:
            return {
                'text': '❌ Укажите arXiv ID\n\nПример: /add 1706.03762',
                'buttons': [[{'text': '🔙 Назад', 'callback': '/search'}]]
            }
        
        try:
            # Проверяем, может уже в библиотеке
            existing = get_entry(args)
            if existing:
                return {
                    'text': f'ℹ️ Статья `{args}` уже в библиотеке!\n\n{existing["title"][:60]}...',
                    'buttons': [
                        [{'text': 'ℹ️ Посмотреть', 'callback': f'/info {args}'}],
                        [{'text': '📚 Библиотека', 'callback': '/library'}]
                    ]
                }
            
            entry = add_to_library(args, status='unread')
            
            authors = ', '.join(entry['authors'][:3])
            if len(entry['authors']) > 3:
                authors += ' et al.'
            
            text = f"""✅ **Добавлено в библиотеку**

📄 {entry['title'][:80]}...

👤 {authors}
🏷️ {entry['primary_category']}
📅 {entry['published'][:10]}
🆔 `{entry['id']}`

Что дальше?
"""
            
            return {
                'text': text,
                'buttons': [
                    [
                        {'text': '✓ Отметить прочитанным', 'callback': f'/mark-read {args}'},
                        {'text': '⭐ В избранное', 'callback': f'/star {args}'}
                    ],
                    [
                        {'text': 'ℹ️ Детали', 'callback': f'/info {args}'},
                        {'text': '📥 BibTeX', 'callback': f'/bibtex {args}'}
                    ],
                    [{'text': '📚 Библиотека', 'callback': '/library'}]
                ]
            }
        
        except Exception as e:
            return {
                'text': f'❌ Ошибка: {e}',
                'buttons': [[{'text': '🔙 Назад', 'callback': '/search'}]]
            }
    
    # /info <arxiv_id>
    elif command == 'info':
        if not args:
            return {
                'text': '❌ Укажите arXiv ID\n\nПример: /info 1706.03762',
                'buttons': [[{'text': '🔙 Назад', 'callback': '/library'}]]
            }
        
        try:
            entry = get_entry(args)
            in_library = entry is not None
            
            if not entry:
                # Получаем из API
                entry = get_info(args, from_library=False)
            
            # Авторы
            authors = ', '.join(entry['authors'][:3])
            authors_count = len(entry['authors'])
            if authors_count > 3:
                authors += f' и ещё {authors_count - 3}'
            
            # Формируем текст
            text = f"""📄 **{entry['title']}**

👤 {authors}
🏷️ {entry['primary_category']} • {', '.join(entry['categories'][:3])}
📅 {entry['published'][:10]}
🆔 `{entry['id']}`

**Аннотация:**
{entry['abstract'][:400]}...

🔗 [PDF]({entry['pdf_url']}) | [Abstract на arXiv]({entry['abs_url']})
"""
            
            # Данные библиотеки
            if in_library:
                lib_info = f"\n\n📚 **В библиотеке**\n"
                lib_info += f"• Добавлено: {entry.get('added_at', '')[:10]}\n"
                lib_info += f"• Статус: {'✓ Прочитано' if entry.get('status') == 'read' else '○ Непрочитано'}\n"
                if entry.get('starred'):
                    lib_info += "• ★ В избранном\n"
                if entry.get('tags'):
                    lib_info += f"• Теги: {', '.join(['#' + t for t in entry['tags'][:5]])}\n"
                text += lib_info
            
            # Кнопки
            buttons = []
            
            if in_library:
                # Уже в библиотеке — кнопки управления
                status_btn = '✓ Прочитано' if entry.get('status') == 'read' else '○ Отметить прочитанным'
                star_btn = '★ Избранное' if entry.get('starred') else '☆ В избранное'
                
                buttons.append([
                    {'text': status_btn, 'callback': f'/toggle-read {args}'},
                    {'text': star_btn, 'callback': f'/star {args}'}
                ])
                buttons.append([{'text': '📥 BibTeX', 'callback': f'/bibtex {args}'}])
            else:
                # Не в библиотеке — предложить добавить
                buttons.append([{'text': '➕ Добавить в библиотеку', 'callback': f'/add {args}'}])
                buttons.append([{'text': '📥 BibTeX', 'callback': f'/bibtex {args}'}])
            
            buttons.append([
                {'text': '🔍 Похожие', 'callback': f'/search {entry["primary_category"]}'},
                {'text': '📚 Библиотека', 'callback': '/library'}
            ])
            
            return {'text': text, 'buttons': buttons}
        
        except Exception as e:
            return {
                'text': f'❌ Ошибка: {e}',
                'buttons': [[{'text': '🔙 Назад', 'callback': '/start'}]]
            }
    
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
            return {
                'text': f'✅ Статья отмечена как прочитанная',
                'buttons': [
                    [
                        {'text': 'ℹ️ Детали', 'callback': f'/info {args}'},
                        {'text': '📚 Библиотека', 'callback': '/library'}
                    ]
                ]
            }
        except Exception as e:
            return {'text': f'❌ Ошибка: {e}'}
    
    # /toggle-read <arxiv_id>
    elif command == 'toggle-read':
        if not args:
            return {'text': '❌ Укажите arXiv ID'}
        
        try:
            entry = get_entry(args)
            if not entry:
                return {'text': f'❌ Статья {args} не найдена в библиотеке'}
            
            new_status = 'unread' if entry.get('status') == 'read' else 'read'
            update_status(args, new_status)
            
            icon = '✓' if new_status == 'read' else '○'
            action = 'прочитанной' if new_status == 'read' else 'непрочитанной'
            
            return {
                'text': f'{icon} Статья отмечена как {action}',
                'buttons': [[{'text': 'ℹ️ Детали', 'callback': f'/info {args}'}]]
            }
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
            
            return {
                'text': f'{icon} Статья {action}',
                'buttons': [
                    [
                        {'text': 'ℹ️ Детали', 'callback': f'/info {args}'},
                        {'text': '📚 Библиотека', 'callback': '/library'}
                    ]
                ]
            }
        except Exception as e:
            return {'text': f'❌ Ошибка: {e}'}
    
    # /help
    elif command == 'help':
        return {
            'text': """📖 **Полная справка**

**🔍 Поиск:**
/search quantum — поиск по теме
/search "author name" — по автору

**➕ Добавление:**
/add 1706.03762 — добавить статью
/info 1706.03762 — детали перед добавлением

**📚 Библиотека:**
/library — мои статьи (последние 5)
/stats — статистика и категории

**👥 Авторы:**
/authors — отслеживаемые исследователи
(добавление: CLI или попроси админа)

**📰 Дайджесты:**
/digest — за неделю
/digest day — за сутки
/digest month — за месяц

**📥 Экспорт:**
/bibtex 1706.03762 — получить BibTeX цитату

**💡 Подсказки:**
• Кликай на кнопки под сообщениями
• ID статьи — это число типа 1706.03762
• Найти ID: ищи статью в Google → URL содержит ID

**🖥️ Web интерфейс:**
Если запущен: http://localhost:5002
(больше возможностей: заметки, фильтры, графики)
""",
            'buttons': [
                [
                    {'text': '📚 Библиотека', 'callback': '/library'},
                    {'text': '🔍 Поиск', 'callback': '/search'}
                ],
                [{'text': '🏠 Главная', 'callback': '/start'}]
            ]
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

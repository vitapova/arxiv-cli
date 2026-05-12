# Multiuser Support

## Как работает

Каждый пользователь Telegram бота получает **свою библиотеку**.

### Структура хранения:

```
~/.arxiv-cli/
├── library.json           # Старая общая библиотека (для CLI)
├── subscriptions.json
├── authors.json
└── users/                 # Multiuser данные
    ├── 123456789/         # Telegram user_id
    │   ├── library.json
    │   ├── subscriptions.json
    │   └── authors.json
    ├── 987654321/
    │   ├── library.json
    │   └── ...
    └── ...
```

### Использование в коде:

```python
from arxiv_cli.utils.context import set_user, get_user

# Установить пользователя (в начале обработки команды)
set_user(telegram_user_id)

# Все функции library автоматически используют user_id из контекста
from arxiv_cli.utils.library import get_entries, add_entry

entries = get_entries()  # Автоматически для current user
```

### CLI vs Telegram Bot

**CLI (без user_id):**
- Использует `~/.arxiv-cli/library.json`
- Одна библиотека для локального пользователя

**Telegram Bot (с user_id):**
- Использует `~/.arxiv-cli/users/{user_id}/library.json`
- У каждого пользователя своя библиотека

### Миграция существующих данных

Если у тебя уже есть библиотека в `~/.arxiv-cli/library.json`:

```python
from arxiv_cli.utils.multiuser import migrate_to_multiuser

# Мигрировать в user_id='default'
migrate_to_multiuser('default')

# Или в свой Telegram ID
migrate_to_multiuser('123456789')
```

## Обратная совместимость

CLI продолжает работать со старой библиотекой:

```bash
# Работает как раньше (общая библиотека)
python3 -m arxiv_cli.cli list
```

Telegram бот создаёт отдельные библиотеки для каждого пользователя.

## Реализация в standalone_bot.py

В каждой команде передаём `user_id`:

```python
async def library_cmd(update: Update, context):
    user_id = update.effective_user.id  # Telegram user ID
    
    # Устанавливаем контекст
    set_user(str(user_id))
    
    # Функции автоматически используют user_id
    response = handle_command('library', user_id=user_id)
    
    await update.message.reply_text(response['text'])
```

## Статистика по пользователям

```python
from arxiv_cli.utils.multiuser import list_users, get_user_stats

# Все пользователи
users = list_users()

# Статистика конкретного
stats = get_user_stats('123456789')
# {'total_papers': 15, 'read': 5, ...}
```

## Следующие шаги

1. ✅ Контекст пользователя (context.py)
2. ✅ Multiuser utils (multiuser.py)
3. ✅ Обновлён load_library/save_library
4. 🚧 Обновить остальные функции library
5. 🚧 Протестировать с разными user_id
6. ✅ Интеграция в Telegram bot

## Текущий статус

**Реализовано:**
- ✅ Базовая инфраструктура multiuser
- ✅ Context для user_id
- ✅ Функции get_library_path/save_library с user_id
- ✅ Standalone bot передаёт user_id

**TODO:**
- Обновить все функции library.py (add_entry, get_entries, etc.)
- Обновить subscriptions.py
- Обновить authors.py
- Протестировать с 2+ пользователями

**Обратная совместимость:** CLI работает как раньше (без user_id).

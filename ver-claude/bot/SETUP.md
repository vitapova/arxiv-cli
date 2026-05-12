# Telegram Bot Setup

## Способ 1: Через OpenClaw (рекомендуется)

### Настройка

Добавь в OpenClaw config (`~/.openclaw/config.yaml`):

```yaml
telegram:
  enabled: true
  botToken: "YOUR_BOT_TOKEN"
```

### Создание бота

1. Открой Telegram → найди **@BotFather**
2. Отправь `/newbot`
3. Введи имя: **arXiv Assistant**
4. Введи username: **arxiv_yourname_bot**
5. Скопируй token
6. Добавь в config

### Обработчик команд

Создай файл `~/.openclaw/workspace/arxiv-bot-handler.py`:

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/vitapotapova/.openclaw/workspace/arxiv-cli/ver-claude')

from bot.telegram_bot import handle_command

# Получаем команду от OpenClaw
message = sys.argv[1] if len(sys.argv) > 1 else ''

# Парсим команду
if message.startswith('/'):
    parts = message.split(maxsplit=1)
    cmd = parts[0][1:]  # Убираем /
    args = parts[1] if len(parts) > 1 else ''
else:
    # Обычное сообщение - интерпретируем как поиск
    cmd = 'search'
    args = message

# Обрабатываем
response = handle_command(cmd, args)

# Выводим результат (OpenClaw подхватит)
print(response['text'])

# Inline buttons (если есть)
if 'buttons' in response:
    import json
    print('\n__BUTTONS__')
    print(json.dumps(response['buttons']))
```

### Настройка OpenClaw для inline buttons

В AGENTS.md или config добавь обработку callback queries.

---

## Способ 2: Standalone бот (без OpenClaw)

```bash
pip install python-telegram-bot

python3 bot/standalone_bot.py
```

(Файл standalone_bot.py нужно создать отдельно)

---

## Использование

### Базовые команды

```
/start — начало работы
/library — показать библиотеку
/search quantum — поиск статей
/add 1706.03762 — добавить статью
/info 1706.03762 — детали
/stats — статистика
/digest — дайджест за неделю
/authors — отслеживаемые авторы
```

### Inline кнопки

После `/search` или `/info` появляются кнопки:
- ➕ В библиотеку
- ✓ Прочитано  
- ★ Избранное
- 📥 BibTeX

Клик на кнопку выполняет действие.

---

## Scheduled дайджесты (через OpenClaw cron)

Добавь cron job:

```bash
# Дайджест каждый день в 9:00
openclaw cron add \
  --schedule "0 9 * * *" \
  --command "/digest day" \
  --target telegram
```

---

## Тестирование (локально)

```bash
# Тест команд
cd /Users/vitapotapova/.openclaw/workspace/arxiv-cli/ver-claude

python3 bot/telegram_bot.py start
python3 bot/telegram_bot.py library
python3 bot/telegram_bot.py stats
python3 bot/telegram_bot.py authors
```

---

## Следующие шаги

1. Создай бота через BotFather
2. Добавь token в OpenClaw config
3. Настрой обработчик команд
4. Протестируй основные команды
5. Настрой scheduled дайджесты

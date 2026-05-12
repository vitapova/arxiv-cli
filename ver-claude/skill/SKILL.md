# arXiv Assistant Skill

OpenClaw skill для работы с arXiv статьями.

## Установка

```bash
# Клонировать репозиторий
git clone https://github.com/vitapova/arxiv-cli
cd arxiv-cli/ver-claude

# Установить зависимости
pip install -e .

# Добавить skill в OpenClaw
ln -s "$(pwd)/skill" ~/.openclaw/skills/arxiv-assistant
```

## Использование

### Через чат с OpenClaw:

```
Найди статьи про quantum computing

Добавь статью 1706.03762 в библиотеку

Покажи мою библиотеку статей

Экспортируй библиотеку в BibTeX

Создай дайджест новых статей за неделю по теме AGI
```

### Автоматические дайджесты:

OpenClaw может настроить scheduled задачи:

```
Настрой автоматический дайджест каждый день в 9:00 по категории cs.AI
```

## Команды

Skill предоставляет следующие инструменты для OpenClaw agent:

- `arxiv_search(query, max_results)` — поиск статей
- `arxiv_add(arxiv_id, tags)` — добавление в библиотеку
- `arxiv_library(filters)` — просмотр библиотеки
- `arxiv_info(arxiv_id)` — информация о статье
- `arxiv_export(format)` — экспорт библиографии
- `arxiv_digest(period, category)` — дайджест
- `arxiv_download(arxiv_id)` — скачивание PDF
- `arxiv_authors_check()` — проверка новых работ авторов

## Примеры

**Поиск и добавление:**
```
User: Найди последние статьи про transformers
Agent: [использует arxiv_search] Найдено 5 статей...
User: Добавь первую в библиотеку
Agent: [использует arxiv_add] Статья добавлена
```

**Дайджест:**
```
User: Что нового в AGI за неделю?
Agent: [использует arxiv_digest] Формирую дайджест...
      Найдено 15 новых статей по AGI...
```

**Scheduled задачи:**
```
User: Каждое утро в 9:00 присылай дайджест по cs.AI
Agent: [создаёт cron job с arxiv_digest]
       Настроил! Буду присылать каждый день.
```

## Для других исследователей

### Вариант A: Публичный Telegram бот
Ты можешь запустить **один публичный бот** который будет работать для ВСЕХ.

**Плюсы:**
- ✅ Исследователи просто пишут боту (как @ChatGPT_bot)
- ✅ Не нужно ничего устанавливать
- ✅ Каждый получает свою библиотеку

**Минусы:**
- ❌ Тебе нужно держать сервер запущенным
- ❌ Нагрузка на твой API

### Вариант B: Установка локально
Каждый исследователь:
1. Устанавливает CLI
2. Запускает своего бота (свой token)
3. Получает полный контроль

**Инструкция для них:**
```bash
# 1. Установить
git clone https://github.com/vitapova/arxiv-cli
cd arxiv-cli/ver-claude
pip install -e .
pip install python-telegram-bot

# 2. Создать своего бота через @BotFather

# 3. Запустить
export TELEGRAM_BOT_TOKEN='your_token'
python3 bot/standalone_bot.py
```

### Вариант C: OpenClaw Skill (для продвинутых)
Те у кого есть OpenClaw устанавливают как skill.

---

## 🎯 Рекомендация:

**Создай ПУБЛИЧНЫЙ бот** — это самый простой путь для пользователей!

1. Создаём бота через @BotFather
2. Запускаем `standalone_bot.py` на сервере (или твоём Mac)
3. Делаем бота публичным
4. Исследователи просто пишут боту — всё!

**Хочешь создам публичного бота прямо сейчас?**

Или сначала протестируем локально твоего личного бота?

---

## 📦 OpenClaw Skill — ДА, можно!

Я создам skill структуру. Другие пользователи OpenClaw смогут установить:

```bash
# В OpenClaw
install skill arxiv-assistant from https://github.com/vitapova/arxiv-cli
```

**Делаем skill структуру?**
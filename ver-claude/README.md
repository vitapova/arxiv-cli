# arXiv Research Assistant

[![Tests](https://img.shields.io/badge/tests-117%20passed-success)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-75%25-brightgreen)](tests/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue)](../LICENSE)

Консольная утилита + Web UI + Telegram бот для работы с научными статьями на arXiv.

**Особенности:**
- 🎨 Красивый терминал (Rich library) и Web интерфейс
- 📱 Telegram бот с inline кнопками
- 👥 Multiuser поддержка
- 📚 Управление библиотекой с тегами и статусами
- 🔔 Отслеживание авторов и версий статей
- 📊 Дайджесты и статистика
- 🤖 LLM-ready (опциональная интеграция)

---

## 🚀 Быстрый старт

### 1. Установка

```bash
git clone https://github.com/vitapova/arxiv-cli
cd arxiv-cli/ver-claude
pip install -e .
```

### 2. Использование

**CLI (терминал):**
```bash
python3 -m arxiv_cli.cli search "quantum computing" --max 5
python3 -m arxiv_cli.cli library
python3 -m arxiv_cli.cli add 1706.03762 --tag transformers
```

**Web UI (localhost):**
```bash
pip install fastapi uvicorn jinja2
python3 web/app.py
# Открой http://localhost:5002
```

**Telegram Bot:**
```bash
pip install python-telegram-bot
export TELEGRAM_BOT_TOKEN='your_token'
python3 bot/standalone_bot.py
```

---

## 📖 Основные команды

### Поиск и добавление

```bash
# Поиск статей
arxiv search "transformer" --max 10 --table

# Поиск с фильтрами
arxiv search "quantum" --category cs.AI --from 2024-01-01 --max 20

# Добавить в библиотеку (без скачивания PDF)
arxiv add 1706.03762 --tag transformers --tag nlp

# Скачать PDF
arxiv download 1706.03762 --auto-name

# Пакетное скачивание
echo -e "1706.03762\n2005.14165" > ids.txt
arxiv download --batch ids.txt --output-dir papers --auto-name
```

### Библиотека

```bash
# Показать библиотеку (красивая таблица)
arxiv list

# Простой текст
arxiv list --plain

# Фильтры
arxiv list --status read
arxiv list --tag gpt
arxiv list --search "attention"

# Сортировка
arxiv list --sort published --order desc

# Управление
arxiv list --mark-read 1706.03762
arxiv list --star 2005.14165
```

### Информация и заметки

```bash
# Детали статьи
arxiv info 1706.03762 --library

# Добавить заметку
arxiv note add 1706.03762 "Важная работа по attention"

# Список заметок
arxiv note list

# Поиск по заметкам
arxiv note search "AGI"
```

### Экспорт

```bash
# BibTeX
arxiv export --all --format bibtex -o papers.bib

# CSL JSON
arxiv export --all --format csl -o papers.json

# С фильтрами
arxiv export --tag gpt --format bibtex

# Статистика
arxiv export --stats
```

### Дайджесты

```bash
# За неделю
arxiv digest --period week --query "AGI" --max 20

# Markdown экспорт
arxiv digest --period month --category cs.AI --format markdown -o digest.md
```

### Отслеживание

```bash
# Версии статей
arxiv track add 1706.03762
arxiv track list
arxiv track update

# Авторы
arxiv authors follow "Ilya Sutskever" --tag AGI
arxiv authors list
arxiv authors check

# Подписки
arxiv subscribe add --query "quantum AGI" --category cs.AI
arxiv subscribe check
```

---

## 🌐 Web Interface

**Запуск:**
```bash
python3 web/app.py
```

**Открой:** http://localhost:5002

**Возможности:**
- 📚 Таблица библиотеки с фильтрами
- 📄 Детальные карточки статей
- 📝 Добавление заметок
- 👥 Просмотр отслеживаемых авторов  
- 📊 Графики статистики
- 🎨 Красивый дизайн

---

## 📱 Telegram Bot

### Для пользователей (простой способ)

Пиши боту `@ваш_бот` (когда запущен):

```
/start — начало
/library — библиотека
/search quantum — поиск
/add 1706.03762 — добавить
/info 1706.03762 — детали
/digest — дайджест недели
/stats — статистика
```

### Для хоста бота (ты)

**1. Создай бота через @BotFather**

**2. Запусти:**
```bash
export TELEGRAM_BOT_TOKEN='ваш_токен'
python3 bot/standalone_bot.py
```

**Документация:** [bot/SETUP.md](bot/SETUP.md)

---

## 💾 Где хранятся данные

```
~/.arxiv-cli/
├── library.json              # Твоя личная библиотека (CLI)
├── subscriptions.json
├── authors.json
└── users/                    # Библиотеки пользователей Telegram
    ├── 123456789/            # User 1
    │   ├── library.json
    │   ├── subscriptions.json
    │   └── authors.json
    └── 987654321/            # User 2
        └── ...
```

**Важно:** Данные на диске, не теряются при перезапуске.

---

## 🤖 LLM Integration (опционально)

Добавь AI-анализ дайджестов:

```bash
export OPENAI_API_KEY='sk-...'

# LLM выбирает топ-5 важных статей
arxiv digest --period week --ai-rank

# Narrative дайджест
arxiv digest --period week --ai-narrative
```

**Документация:** [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 📚 Документация

- **[TUTORIAL.md](TUTORIAL.md)** — подробное руководство для начинающих
- **[ARCHITECTURE.md](ARCHITECTURE.md)** — архитектура системы
- **[AGI_FEATURES.md](AGI_FEATURES.md)** — фичи для AGI исследователей
- **[DISTRIBUTION.md](DISTRIBUTION.md)** — варианты распространения
- **[bot/SETUP.md](bot/SETUP.md)** — настройка Telegram бота
- **[web/README.md](web/README.md)** — Web UI документация

---

## 🧪 Тестирование

```bash
# Установка dev зависимостей
pip install -r requirements.txt

# Запуск тестов
pytest tests/ -v

# С покрытием
pytest tests/ --cov=arxiv_cli --cov-report=term

# Быстрые тесты (без API)
pytest tests/ -k "not real"
```

**Покрытие:** 75% (117 тестов) ✅

---

## 🎯 Для AGI исследователей

**Специальные возможности:**
- 👥 Отслеживание ключевых авторов (Sutskever, Bengio, etc.)
- 📝 Reading notes с полнотекстовым поиском
- 🔗 Связи между работами (планируется)
- 🤖 LLM summaries (опционально)
- 📊 Trend analysis (планируется)

**Подробнее:** [AGI_FEATURES.md](AGI_FEATURES.md)

---

## 📦 Установка для других исследователей

### Вариант A: Через твой Telegram бот
**Самый простой** — просто пишут боту, ничего не устанавливают.

### Вариант B: Локальная установка
```bash
git clone https://github.com/vitapova/arxiv-cli
cd arxiv-cli/ver-claude
pip install -e .
```

### Вариант C: OpenClaw Skill (если есть OpenClaw)
```bash
openclaw skill install arxiv-assistant from https://github.com/vitapova/arxiv-cli
```

**Подробнее:** [DISTRIBUTION.md](DISTRIBUTION.md)

---

## 🛠️ Технологии

- **CLI:** Click, Rich
- **API:** arXiv Export API, feedparser
- **Storage:** JSON files
- **Web UI:** FastAPI, Jinja2, HTMX
- **Telegram:** python-telegram-bot
- **LLM:** OpenAI/Claude (опционально)
- **Tests:** pytest, 75% coverage

---

## 📄 Лицензия

MIT License — см. [LICENSE](../LICENSE)

---

## 🤝 Contribution

Pull requests welcome! См. [ARCHITECTURE.md](ARCHITECTURE.md) для понимания структуры.

---

## 📞 Контакты

- **GitHub:** https://github.com/vitapova/arxiv-cli
- **Issues:** https://github.com/vitapova/arxiv-cli/issues
- **Автор:** Vita Potapova

---

## ⚡ Краткая шпаргалка

```bash
# Поиск → добавить → прочитать → экспорт
arxiv search "AGI" --max 5
arxiv add 2301.12345 --tag AGI --tag important  
arxiv note add 2301.12345 "Прорывная работа!"
arxiv list --tag important
arxiv export --tag important --format bibtex -o important.bib

# Отслеживание авторов
arxiv authors follow "Ilya Sutskever"
arxiv authors check

# Дайджесты
arxiv digest --period week --category cs.AI

# Web UI
python3 web/app.py  # → http://localhost:5002

# Telegram Bot
export TELEGRAM_BOT_TOKEN='...'
python3 bot/standalone_bot.py
```

---

**Нужна помощь?** См. [TUTORIAL.md](TUTORIAL.md) для пошаговой инструкции!

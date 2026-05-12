# arXiv CLI

[![Tests](https://img.shields.io/badge/tests-117%20passed-success)](ver-claude/tests/)
[![Coverage](https://img.shields.io/badge/coverage-75%25-brightgreen)](ver-claude/tests/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Консольная утилита для работы с базой научных препринтов arXiv, сгенерированная с помощью LLM.

## Версии реализации

Проект содержит две версии CLI, реализованные разными моделями:

### 📁 [ver-claude](ver-claude/) — Claude Sonnet 4.5 ⭐ FEATURED

**Полный стек для исследователей:**
- ✅ CLI (11 команд) с Rich визуализацией
- ✅ Web UI (http://localhost:5002)
- ✅ Telegram Bot (multiuser)
- ✅ 117 тестов, покрытие 75%
- ✅ Rate limit auto-retry
- ✅ Отслеживание авторов и версий
- ✅ Reading notes с поиском
- ✅ LLM-ready (опциональная интеграция)

**Для AGI исследователей:**
- 👥 Track ключевых авторов (Sutskever, Bengio, etc.)
- 📝 Заметки к статьям
- 📊 Дайджесты с группировкой
- 🤖 AI-анализ (coming soon)

### 📁 [ver-gpt](ver-gpt/) — GPT-5.2

- ✅ Альтернативная реализация
- ✅ Современный tooling (pyproject.toml, ruff)
- ✅ Сравнительный анализ подходов

**Сравнение:** [COMPARISON.md](COMPARISON.md)

## Основные возможности

**Работа со статьями:**
- 🔍 Поиск по авторам, категориям, ключевым словам, датам
- 📥 Скачивание PDF (автоименование, пакетное)
- 📚 Библиотека с тегами, статусами (read/unread/starred)
- 📝 Reading notes с полнотекстовым поиском
- 📊 Экспорт в BibTeX/CSL для LaTeX/Zotero

**Отслеживание:**
- 👥 Новые публикации от ключевых авторов
- 🔄 Версии статей (v1, v2, v3...)
- 📌 Подписки на темы с детекцией новых статей

**Дайджесты:**
- 📰 По периодам (день/неделя/месяц)
- 🏷️ Группировка по категориям
- 📊 Статистика публикаций
- 📝 Экспорт в Markdown

**Интерфейсы:**
- 💻 CLI с цветными таблицами (Rich)
- 🌐 Web UI на localhost
- 📱 Telegram bot с inline кнопками

## API

Используется внешний REST API arXiv:
- **Endpoint:** `http://export.arxiv.org/api/query`
- **Формат:** Atom XML
- **Документация:** https://arxiv.org/help/api/

## Установка и использование

См. документацию в каждой версии:
- [ver-claude/README.md](ver-claude/README.md)
- [ver-gpt/README.md](ver-gpt/README.md)

## Структура репозитория

```
arxiv-cli/
├── LICENSE              # MIT License
├── .gitignore           # Git exclusions
├── README.md            # Этот файл
├── ver-claude/          # Версия Claude
│   ├── arxiv_cli/       # Исходный код
│   ├── tests/           # 117 тестов
│   ├── README.md        # Документация
│   └── setup.py
└── ver-gpt/             # Версия GPT
    ├── arxiv_cli/       # Исходный код
    ├── tests/           # Тесты
    ├── README.md        # Документация
    └── REPORT.md        # Сравнительный анализ
```

## Сравнение версий

См. детальный анализ в [ver-gpt/REPORT.md](ver-gpt/REPORT.md)

## Лицензия

MIT License — см. [LICENSE](LICENSE)

## Автор

Генерация кода:
- **ver-claude:** Claude Sonnet 4.5 (Anthropic)
- **ver-gpt:** GPT-5.2 (OpenAI)

Проект: Vita Potapova

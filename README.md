# arXiv CLI

[![Tests](https://img.shields.io/badge/tests-117%20passed-success)](ver-claude/tests/)
[![Coverage](https://img.shields.io/badge/coverage-75%25-brightgreen)](ver-claude/tests/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Консольная утилита для работы с базой научных препринтов arXiv, сгенерированная с помощью LLM.

## Версии реализации

Проект содержит две версии CLI, реализованные разными моделями:

### 📁 [ver-claude](ver-claude/) — Claude Sonnet 4.5
- ✅ Полная реализация всех команд
- ✅ 117 тестов, покрытие 75%
- ✅ Rate limit handling
- ✅ Библиотека статей с тегами
- ✅ Отслеживание версий
- ✅ Подписки с детекцией новых статей

### 📁 [ver-gpt](ver-gpt/) — GPT-5.2
- ✅ Альтернативная реализация
- ✅ Сравнительный анализ подходов

## Возможности

- 🔍 Поиск статей по авторам, категориям, ключевым словам
- 📅 Фильтрация по датам публикации
- 📋 Формирование дайджестов новых публикаций
- 🔔 Отслеживание обновлений и версий статей
- 📥 Скачивание PDF (одиночное и пакетное)
- 📚 Экспорт библиографических данных (BibTeX/CSL)
- 📌 Подписки на поисковые запросы
- 🏷️ Управление библиотекой с тегами и статусами

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

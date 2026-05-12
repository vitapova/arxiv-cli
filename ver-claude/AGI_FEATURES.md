# Функциональность для AGI исследователей

## 🎯 Сценарии использования

### 1. Отслеживание ключевых авторов
**Проблема:** Следить за публикациями конкретных исследователей (Ilya Sutskever, Demis Hassabis, etc.)

**Решение:**
```bash
# Новая команда: authors
arxiv authors follow "Ilya Sutskever"
arxiv authors list
arxiv authors check  # Новые статьи от отслеживаемых авторов
```

**Реализация:**
- Хранилище `~/.arxiv-cli/authors.json`
- Поиск `au:"Author Name"` + фильтр по датам
- Уведомления о новых публикациях

---

### 2. Автоматические дайджесты по расписанию
**Проблема:** Нужен регулярный обзор новых статей

**Решение:**
```bash
# Настройка автоматического дайджеста
arxiv schedule add --query "AGI" --category cs.AI --period daily --time 09:00
arxiv schedule list
```

**Реализация через OpenClaw cron:**
- Задание cron для ежедневного дайджеста
- Отправка в Telegram
- Экспорт в Markdown для архива

---

### 3. Reading notes и аннотации
**Проблема:** Нужно сохранять заметки о прочитанных статьях

**Решение:**
```bash
arxiv note add 1706.03762 "Важная работа по attention. Использовать для проекта X"
arxiv note list
arxiv note search "проект X"
```

**Реализация:**
- Поле `notes` в библиотеке
- Markdown формат для структурированных заметок
- Полнотекстовый поиск по заметкам

---

### 4. Связи между статьями (References)
**Проблема:** Понять взаимосвязь работ

**Решение:**
```bash
arxiv graph show 1706.03762  # Показать связи
arxiv graph related --limit 10  # Похожие статьи
```

**Реализация:**
- Извлечение references из PDF (pdfplumber)
- Поиск по цитированиям
- Граф зависимостей

---

### 5. LLM-генерация summaries
**Проблема:** Быстро понять суть статьи

**Решение:**
```bash
arxiv summarize 1706.03762 --length short
arxiv summarize 1706.03762 --questions "Какая основная идея? Применимо ли к AGI?"
```

**Реализация:**
- Интеграция OpenAI/Claude API
- Извлечение текста из PDF
- Промпт-шаблоны для разных типов суммаризации

---

### 6. Collections и reading lists
**Проблема:** Организация статей по проектам/темам

**Решение:**
```bash
arxiv collection create "AGI Safety Papers"
arxiv collection add 1706.03762 --to "AGI Safety Papers"
arxiv collection show "AGI Safety Papers"
arxiv collection export "AGI Safety Papers" --format bibtex
```

**Реализация:**
- Коллекции как группы тегов
- Экспорт коллекций
- Sharing коллекций (JSON export/import)

---

### 7. Alerts для важных авторов/тем
**Проблема:** Не пропустить прорывные работы

**Решение:**
```bash
arxiv alert add --author "Ilya Sutskever" --notify telegram
arxiv alert add --keywords "AGI" "recursive self-improvement" --priority high
```

**Реализация:**
- Интеграция с Telegram/Email
- Приоритеты уведомлений
- Умная фильтрация (ML for relevance scoring)

---

### 8. Citation tracking
**Проблема:** Отслеживать цитирования своих работ

**Решение:**
```bash
arxiv citations watch "your paper id"
arxiv citations count  # Количество цитирований
```

**Реализация:**
- Semantic Scholar API / Google Scholar scraping
- История цитирований

---

### 9. Экспорт в Knowledge Management
**Проблема:** Интеграция с Notion/Obsidian/Roam

**Решение:**
```bash
arxiv export --format notion --to "Research Database"
arxiv export --format obsidian -o vault/Papers/
```

**Реализация:**
- Notion API
- Obsidian markdown format
- Automatic backlinks

---

### 10. Collaborative библиотеки
**Проблема:** Поделиться подборкой с коллегами

**Решение:**
```bash
arxiv share export "AGI Papers" --public
# Генерирует ссылку: https://arxiv-cli.app/shared/abc123

arxiv share import https://arxiv-cli.app/shared/abc123
```

**Реализация:**
- Backend для хранения shared collections
- Import/export через JSON

---

## 🤖 Telegram Bot функциональность

### Основные команды:

```
/search transformer - Поиск статей
/library - Показать библиотеку
/info 1706.03762 - Информация о статье
/add 1706.03762 #transformers - Добавить в библиотеку
/export bibtex - Экспорт в BibTeX
/digest week - Дайджест за неделю
/stats - Статистика

/subscribe add "quantum AGI" - Создать подписку
/subscribe check - Проверить обновления

/authors follow "Ilya Sutskever" - Отслеживать автора
/authors check - Новые статьи от авторов
```

### Интерактивные возможности:

**Inline кнопки:**
```
📄 Paper Title
Vaswani et al., 2017

[📥 Скачать] [➕ В библиотеку] [⭐ Избранное]
[📝 Заметка] [🔗 Связанные] [📊 Summary]
```

**Автоматические уведомления:**
- Новые статьи от отслеживаемых авторов
- Обновления подписок (1 раз в день)
- Новые версии tracked статей

**Отправка файлов:**
- PDF прямо в чат
- Markdown дайджесты
- BibTeX файлы

---

## 🚀 Приоритеты для MVP

### Must-have (для версии 1.0):

1. ✅ **Отслеживание авторов** (`authors` команда)
   - Простая реализация через API фильтр
   - ~2 часа работы

2. ✅ **Reading notes** (`note` команда)
   - Поле в библиотеке
   - ~1 час

3. ✅ **Collections** (расширение тегов)
   - Можно через существующую систему тегов
   - ~1 час

4. ✅ **Telegram bot** (базовая версия)
   - Обёртка над CLI
   - OpenClaw message tool
   - ~3-4 часа

### Nice-to-have (версия 2.0):

5. ⏳ **LLM summaries**
   - Интеграция OpenAI/Claude
   - ~3 часа

6. ⏳ **Related papers** (через embeddings)
   - Semantic search
   - ~4 часа

7. ⏳ **Notion/Obsidian export**
   - API интеграция
   - ~2-3 часа

---

## 💡 Рекомендации

**Для запуска:**
1. Начни с `authors` команды (самое полезное для AGI сферы)
2. Добавь `notes` (простая, но нужная функция)
3. Сделай базовый Telegram bot
4. На основе фидбека — остальное

**Для Telegram бота:**
- Используй OpenClaw message tool (уже в твоей системе!)
- Inline buttons для UX
- Scheduled jobs для автодайджестов

Начать с чего? Предлагаю:
1. **`authors`** команда (20 минут)
2. **`notes`** команда (15 минут)  
3. **Telegram bot** базовая версия (1 час)

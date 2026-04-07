# arXiv CLI

Консольная утилита для работы с базой научных препринтов arXiv.

## Возможности

- 🔍 Поиск статей по авторам, категориям, ключевым словам
- 📅 Фильтрация по датам публикации
- 📋 Формирование дайджестов новых публикаций
- 🔔 Отслеживание обновлений по сохранённым запросам
- 📥 Скачивание PDF
- 📚 Экспорт библиографических данных (BibTeX/CSL)

## Установка

```bash
cd ver-claude
pip install -e .
```

## Особенности

### Автоматическая обработка rate limits

arXiv CLI автоматически справляется с ограничениями API (429 ответ):
- ✅ Автоматические повторы с экспоненциальной задержкой
- ✅ До 3 попыток с паузами 3, 6, 9 секунд
- ✅ Информация о повторах выводится в stderr (`⏳ Rate limit, ожидание 3с...`)
- ✅ Пользователю не нужно ждать вручную или перезапускать команду

При интенсивном использовании (digest, subscribe check) CLI автоматически подождёт и повторит запрос.

## Разработка и тестирование

```bash
# Установка dev-зависимостей
pip install -r requirements.txt

# Запуск тестов
pytest tests/ -v

# Запуск с покрытием
pytest tests/ --cov=arxiv_cli --cov-report=term-missing

# Быстрый запуск (без реальных API-запросов)
pytest tests/ -v -k "not real"
```

**Текущее покрытие тестами:** 32% (65 тестов)

Тестируются:
- ✅ API-клиент: 81% (retry logic, rate limits)
- ✅ Парсер XML: 100%
- ✅ Команды: search (84%), download (47%), export (57%), list (100%), manage (65%)
- ✅ Форматтеры: 37% (text, table, markdown, BibTeX, CSL)
- ✅ Библиотека: 65% (статусы, теги, starred, фильтрация, сортировка)
- ✅ Подписки: 68% (add, list, remove)
- ✅ Отслеживание: 48% (версии, обновления)
- ✅ Дайджесты: 76% (периоды, группировка, статистика)

**Набор тестов:**
- 5 тестов API + rate limits
- 4 теста парсера
- 13 тестов команд (search, download, export)
- 10 тестов библиотеки (статусы, фильтры, сортировка)
- 8 тестов форматтеров
- 8 тестов подписок
- 4 теста отслеживания
- 5 тестов дайджестов
- 8 тестов управления (add, remove, info)
- 4 теста rate limit handling

## Использование

**Текущий статус реализации:** ✅ ВСЕ КОМАНДЫ РЕАЛИЗОВАНЫ: `download`, `search`, `export`, `list`, `add`, `remove`, `info`, `track`, `digest`, `subscribe`

### Скачивание PDF статей

```bash
# Скачать статью (автоматическое имя файла)
python3 -m arxiv_cli.cli download 1706.03762

# Скачать с указанием имени
python3 -m arxiv_cli.cli download 2301.07041 -o my-paper.pdf

# Автоматическое именование: {id}_{author}_{year}.pdf
python3 -m arxiv_cli.cli download 1706.03762 --auto-name
# → 1706.03762_Vaswani_2017.pdf

# Скачать в определённую директорию
python3 -m arxiv_cli.cli download 2103.00020 -d ~/papers

# Скачать в директорию с автоименованием
python3 -m arxiv_cli.cli download 2005.14165 -d ~/papers --auto-name

# Пакетное скачивание из файла
python3 -m arxiv_cli.cli download --batch ids.txt --output-dir papers --auto-name
```

**Формат batch-файла** (`ids.txt`):
```
# Список arXiv ID (один на строку, # для комментариев)
1706.03762
2005.14165
2301.07041
```

**Параметры:**
- `-o, --output` — полный путь для сохранения файла
- `-d, --output-dir` — директория для сохранения
- `--auto-name` — именование `{id}_{author}_{year}.pdf`
- `-b, --batch` — пакетное скачивание из файла
- `-t, --tag` — теги для статьи (сохраняется в библиотеку)
- `--no-library` — не сохранять в библиотеку

**Библиотека статей:**
При скачивании метаданные автоматически сохраняются в `~/.arxiv-cli/library.json` для последующего экспорта.

**Примеры arXiv ID для тестирования:**
- `1706.03762` — Attention Is All You Need (Transformers)
- `2005.14165` — GPT-3
- `2301.07041` — Verifiable Fully Homomorphic Encryption
- `2103.00020` — Flamingo (DeepMind)
- `2212.08073` — Constitutional AI (Anthropic)

### Поиск статей

```bash
# Базовый поиск
python3 -m arxiv_cli.cli search "quantum computing"

# Поиск с ограничением количества результатов
python3 -m arxiv_cli.cli search "neural networks" --max 5

# Поиск с пагинацией
python3 -m arxiv_cli.cli search "GPT" --page 2 --per-page 20

# Поиск с фильтром по категории
python3 -m arxiv_cli.cli search "transformer" --category cs.CL

# Поиск по автору
python3 -m arxiv_cli.cli search "" --author "Vaswani"

# Поиск в названии
python3 -m arxiv_cli.cli search "" --title "attention"

# Фильтр по датам (YYYY-MM-DD)
python3 -m arxiv_cli.cli search "quantum" --from 2026-01-01 --to 2026-04-06

# Поиск за последний месяц
python3 -m arxiv_cli.cli search "LLM" --from 2026-03-01 --sort date

# Сортировка по дате (вместо релевантности)
python3 -m arxiv_cli.cli search "GPT" --sort date

# Табличный формат
python3 -m arxiv_cli.cli search "machine learning" --max 10 --table

# Компактный вывод (без аннотаций)
python3 -m arxiv_cli.cli search "machine learning" --max 10 --compact

# Вывод в JSON
python3 -m arxiv_cli.cli search "quantum" --max 1 --format json

# Комбинация фильтров
python3 -m arxiv_cli.cli search "deep learning" --category cs.LG --category cs.AI --from 2025-01-01 --max 5 --table

# Справка по команде
python3 -m arxiv_cli.cli search --help
```

**Параметры поиска:**
- `-n, --max` — количество результатов (по умолчанию 10)
- `-p, --page` — номер страницы (для пагинации)
- `--per-page` — результатов на странице (по умолчанию 10)
- `--sort` — сортировка: `relevance` (по умолчанию) или `date`
- `-c, --category` — фильтр по категории (можно указать несколько)
- `-a, --author` — фильтр по автору
- `-t, --title` — поиск в названии
- `--from` — начальная дата (YYYY-MM-DD)
- `--to` — конечная дата (YYYY-MM-DD)
- `--table` — табличный формат вывода
- `--compact` — компактный вывод (без аннотаций)
- `--format` — формат: `text` (по умолчанию) или `json`

### Экспорт библиографических данных

```bash
# Статистика библиотеки
python3 -m arxiv_cli.cli export --stats

# Экспорт одной статьи в BibTeX
python3 -m arxiv_cli.cli export 1706.03762 --format bibtex

# Экспорт одной статьи в CSL JSON
python3 -m arxiv_cli.cli export 2005.14165 --format csl

# Экспорт всей библиотеки в BibTeX
python3 -m arxiv_cli.cli export --all --format bibtex

# Экспорт всей библиотеки в файл
python3 -m arxiv_cli.cli export --all --format bibtex -o my_library.bib

# Экспорт с фильтром по категории
python3 -m arxiv_cli.cli export --all --category cs.CL --format bibtex

# Экспорт с фильтром по тегу
python3 -m arxiv_cli.cli export --tag llm --format csl

# Комбинация фильтров
python3 -m arxiv_cli.cli export --all --category cs.AI --tag transformers --format bibtex
```

**Параметры:**
- `-f, --format` — формат: `bibtex` (по умолчанию) или `csl`
- `-o, --output` — файл для сохранения (иначе вывод в консоль)
- `--all` — экспортировать всю библиотеку
- `-c, --category` — фильтр по категории
- `-t, --tag` — фильтр по тегу (можно указать несколько)
- `--stats` — показать статистику библиотеки

**Форматы экспорта:**
- **BibTeX** — для LaTeX, JabRef
- **CSL JSON** — для Zotero, Mendeley, Citation.js

### Быстрое управление библиотекой

```bash
# Добавить статью в библиотеку (без скачивания PDF)
python3 -m arxiv_cli.cli add 2103.00020 --tag multimodal --tag vision

# Добавить как прочитанную
python3 -m arxiv_cli.cli add 1706.03762 --status read

# Показать информацию о статье (из API)
python3 -m arxiv_cli.cli info 2212.08073

# Показать информацию из библиотеки
python3 -m arxiv_cli.cli info 1706.03762 --library

# Добавить теги к существующей статье
python3 -m arxiv_cli.cli info 2103.00020 --add-tag openai --add-tag clip

# Удалить теги
python3 -m arxiv_cli.cli info 2103.00020 --remove-tag multimodal

# Удалить статью из библиотеки
python3 -m arxiv_cli.cli remove 2005.14165
```

### Управление библиотекой статей

```bash
# Показать всю библиотеку
python3 -m arxiv_cli.cli list

# Табличный формат
python3 -m arxiv_cli.cli list --table

# Фильтр по статусу
python3 -m arxiv_cli.cli list --status read
python3 -m arxiv_cli.cli list --status unread
python3 -m arxiv_cli.cli list --status starred

# Фильтр по тегу
python3 -m arxiv_cli.cli list --tag llm --compact

# Поиск по названию и аннотации
python3 -m arxiv_cli.cli list --search "attention mechanism"

# Сортировка
python3 -m arxiv_cli.cli list --sort published --order asc
python3 -m arxiv_cli.cli list --sort title

# Отметить статью как прочитанную
python3 -m arxiv_cli.cli list --mark-read 1706.03762

# Отметить как непрочитанную
python3 -m arxiv_cli.cli list --mark-unread 1706.03762

# Добавить/убрать из избранного
python3 -m arxiv_cli.cli list --star 2005.14165

# Комбинация фильтров
python3 -m arxiv_cli.cli list --status unread --tag gpt --table
```

**Параметры:**
- `--status` — фильтр: `read`, `unread`, `starred`
- `-c, --category` — фильтр по категории
- `-t, --tag` — фильтр по тегу (можно несколько)
- `-s, --search` — поиск по названию и аннотации
- `--sort` — сортировка: `added_at` (по умолчанию), `published`, `title`, `read_at`
- `--order` — порядок: `desc` (по умолчанию), `asc`
- `--table` — табличный формат
- `--compact` — компактный вывод (без аннотаций)
- `--mark-read` — отметить как прочитанную
- `--mark-unread` — отметить как непрочитанную
- `--star` — переключить избранное

**Индикаторы статуса:**
- `○` — непрочитано
- `✓` — прочитано
- `★` — в избранном
- `☆` — не в избранном

### Отслеживание версий статей

```bash
# Добавить статью в отслеживание
python3 -m arxiv_cli.cli track add 1706.03762 --tag transformers

# Показать все отслеживаемые статьи
python3 -m arxiv_cli.cli track list

# Проверить обновления всех отслеживаемых статей
python3 -m arxiv_cli.cli track update

# Проверить обновления конкретной статьи
python3 -m arxiv_cli.cli track update 1706.03762

# Показать историю версий
python3 -m arxiv_cli.cli track versions 1706.03762

# Убрать из отслеживания
python3 -m arxiv_cli.cli track remove 1706.03762
```

**Возможности:**
- Автоматическое отслеживание новых версий препринтов
- История версий с датами обновления и проверки
- Массовая проверка обновлений (`track update`)
- Пометки новых версий в истории

**Как работает:**
1. `track add` — добавляет статью в отслеживание, сохраняет текущую версию
2. `track update` — проверяет arXiv API на наличие новых версий
3. При обновлении автоматически:
   - Обновляет метаданные (title, abstract, authors)
   - Сохраняет историю версий
   - Помечает новую версию маркером [NEW]
4. `track versions` — показывает всю историю с датами

### Дайджесты новых публикаций

```bash
# Дайджест за неделю
python3 -m arxiv_cli.cli digest --period week

# Дайджест за день с фильтром по категории
python3 -m arxiv_cli.cli digest --period day --category cs.AI --max 20

# Дайджест с ключевыми словами
python3 -m arxiv_cli.cli digest --period month --query "transformer" --max 10

# Экспорт в Markdown
python3 -m arxiv_cli.cli digest --period week --format markdown --export digest.md

# Комбинация фильтров
python3 -m arxiv_cli.cli digest --period week --category cs.CL --category cs.AI --query "attention" --max 15
```

**Возможности:**
- Периоды: `day`, `week` (по умолчанию), `month`
- Фильтрация по категориям и ключевым словам
- Группировка результатов по категориям
- Статистика (количество статей по категориям)
- Форматы: `text` (консоль) и `markdown` (файл)
- Экспорт в Markdown с полными аннотациями

**Параметры:**
- `--period` — период: `day`, `week`, `month`
- `-c, --category` — категории (можно несколько)
- `-q, --query` — ключевые слова
- `-n, --max` — максимум статей (по умолчанию 50)
- `--format` — формат: `text`, `markdown`
- `-o, --export` — экспорт в файл

### Подписки на поисковые запросы

```bash
# Создать подписку
python3 -m arxiv_cli.cli subscribe add --query "LLM agents" --category cs.AI

# С именем
python3 -m arxiv_cli.cli subscribe add --query "quantum computing" --name "Quantum Research"

# Несколько категорий
python3 -m arxiv_cli.cli subscribe add --query "transformer" --category cs.CL --category cs.AI

# Показать все подписки
python3 -m arxiv_cli.cli subscribe list

# Проверить обновления всех подписок
python3 -m arxiv_cli.cli subscribe check

# Проверить конкретную подписку
python3 -m arxiv_cli.cli subscribe check 1

# Удалить подписку
python3 -m arxiv_cli.cli subscribe remove 2
```

**Возможности:**
- Сохранённые поисковые запросы
- Автоматическая проверка новых статей
- Показывает только НОВЫЕ статьи (сравнение с прошлым запуском)
- Поддержка категорий и ключевых слов
- Отслеживание истории результатов

**Как работает:**
1. `subscribe add` — создаёт подписку с запросом
2. `subscribe check` — выполняет поиск и сравнивает с прошлыми результатами
3. Показывает только новые статьи (которых не было при прошлой проверке)
4. Сохраняет ID последних результатов для следующего сравнения

**Параметры:**
- `-q, --query` — поисковый запрос (обязательно)
- `-c, --category` — категории (можно несколько)
- `-n, --name` — имя подписки (опционально)
- `-m, --max` — максимум результатов (по умолчанию 20)

**Хранение:** `~/.arxiv-cli/subscriptions.json`

## Структура проекта

```
ver-claude/
├── arxiv_cli/
│   ├── commands/      # CLI-команды
│   ├── api/          # Работа с arXiv API
│   └── utils/        # Вспомогательные функции
├── tests/            # Тесты
└── README.md
```

## API arXiv

Endpoint: `GET http://export.arxiv.org/api/query`

Параметры:
- `search_query` — поисковый запрос
- `start` — смещение для пагинации
- `max_results` — максимальное количество результатов
- `sortBy` — сортировка (relevance, lastUpdatedDate, submittedDate)
- `sortOrder` — порядок (ascending, descending)

## Лицензия

MIT

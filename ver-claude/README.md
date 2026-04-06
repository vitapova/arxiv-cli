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

**Текущее покрытие тестами:** 44% (30 тестов)

Тестируются:
- ✅ API-клиент (запросы, парсинг URL)
- ✅ Парсер XML (структура, поля, реальные данные)
- ✅ Команды (search, download, export)
- ✅ Форматтеры (BibTeX, CSL, таблицы)
- ✅ Библиотека статей (добавление, фильтрация)

## Использование

**Текущий статус реализации:** ✅ `download`, `search`, `export` | 🚧 `digest`, `watch`

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

### Команды в разработке

```bash
# Дайджест за последнюю неделю (TODO)
python3 -m arxiv_cli.cli digest --category cs.AI --days 7

# Отслеживание обновлений (TODO)
python3 -m arxiv_cli.cli watch add "quantum computing" --name quantum
```

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

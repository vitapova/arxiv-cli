# arxiv-cli (ver-gpt)

Консольная утилита для работы с arXiv: поиск, дайджесты, отслеживание сохранённых запросов, скачивание PDF, экспорт BibTeX/CSL.

Статус: **в разработке**.

## Что уже есть

- `arxiv search` — поиск по arXiv через export API
  - поддерживает raw `search_query` **или** сборку запроса из флагов (`--author/--category/--title/--abstract/--all/--id`)
  - пагинация: `--page`, `--per-page` (и advanced `--start`, `--max-results`)
  - сортировка: `--sort relevance|date` (date = `submittedDate`)
  - фильтр по датам: `--from`, `--to` (по `published`, client-side)
  - форматы вывода: `--format table|compact|text`, плюс `--json`

- `arxiv download` — скачивание PDF по arXiv id
  - `--output-dir` для выбора папки
  - `--batch` для пакетного скачивания
  - именование: `{id}_{first_author}_{year}.pdf`

- `arxiv export` — экспорт библиографии из локальной библиотеки
  - `--format bibtex|csl`
  - фильтры: `--tag`, `--category`
  - экспорт всей библиотеки по умолчанию

- `arxiv track` — управление локальной библиотекой
  - `track add` — добавление статьи (fetch метаданных из arXiv), задаёт `added_at`, `status`, `tags`
  - `track remove` — удаление статьи
  - `track update` — обновление метаданных при появлении новых версий (и замена старой версии на новую)
  - `track versions` — история версий
  - `track status --set` — статус `read|unread|starred`
  - `track tag --add/--remove` — теги

## Команды

- `arxiv search` — поиск
- `arxiv download` — скачивание PDF
- `arxiv export` — экспорт библиографии
- `arxiv track` — управление локальной библиотекой
- `arxiv list` — просмотр и поиск по локальной библиотеке
- `arxiv subscribe` — подписки на сохранённые запросы
- `arxiv digest` — дайджест новых публикаций

## Источник данных

arXiv API:
- `GET http://export.arxiv.org/api/query`
- параметры: `search_query`, `start`, `max_results`, `sortBy`, `sortOrder`

## Установка для разработки

Из папки `ver-gpt/`:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

## Быстрый запуск без установки

Если не хочется ставить пакет, можно запускать из репозитория:

```bash
cd ver-gpt
./arxiv --help
./arxiv search --category cs.CL --all transformer --per-page 3 --sort date
```

Скрипт `./arxiv` автоматически использует `./.venv/bin/python`, если venv создан.

## Локальное хранилище

По умолчанию данные хранятся в user data dir ОС.
На macOS это обычно:

- `~/Library/Application Support/arxiv-cli/`
  - `library.json` — библиотека статей
  - `subscriptions.json` — подписки
  - `state/`
    - `tracking.json` — история версий для `track versions`
    - `subscriptions_state.json` — last-seen для `subscribe check`

## Примеры

### `search`

#### 1) Raw запрос (как в документации arXiv)

```bash
arxiv search "cat:cs.CL AND au:Smith" --per-page 5 --sort date
```

(Back-compat) Старый вариант тоже поддерживается:

```bash
arxiv search "cat:cs.CL AND all:transformer" --max-results 2 --sort-by submittedDate --format text
```

#### 2) Запрос из флагов (повторяемые `--author`, `--category`)

```bash
arxiv search --author "Yoshua Bengio" --category cs.LG --per-page 5 --sort date
```

#### 3) Категория + full-text терм + диапазон дат + компактный формат

```bash
arxiv search --category cs.CL --all transformer \
  --from 2026-04-01 --to 2026-04-05 \
  --page 1 --per-page 10 --sort date \
  --format compact
```

#### 4) Таблица (по умолчанию)

```bash
arxiv search --category cs.CL --all transformer --per-page 5 --sort date --format table
```

#### 5) JSON

```bash
arxiv search --category cs.CL --all transformer --per-page 2 --json
```

### `download`

#### 1) Download одного PDF по id

```bash
arxiv download 2604.03199v1 --output-dir ./papers
```

Именование файла: `{id}_{first_author}_{year}.pdf`

#### 2) Batch download из файла

```bash
arxiv download --batch docs/batch_ids.txt --output-dir ./papers
```

Формат batch-файла: 1 id на строку, `#` — комментарии.

Примечание: команда делает запрос метаданных к arXiv (для `first_author` и `year`), затем качает PDF.

### `list`

```bash
arxiv list --format table
arxiv list --status unread --tag transformers --format compact
arxiv list --from 2026-04-01 --to 2026-04-30 --sort added --order desc
arxiv list --q memorization
```

Примечание: `--from/--to` в `list` — это фильтр по **дате добавления** (`added_at`), а не по дате публикации.

### `subscribe`

```bash
arxiv subscribe add --query "LLM agents" --category cs.AI
arxiv subscribe list
arxiv subscribe check --max-results 25 --min-interval 3 --retries-429 2 --backoff 15
arxiv subscribe remove <id>
```

Примечание: `subscribe check` хранит состояние "уже видели" в `state/subscriptions_state.json`.

### `digest`

```bash
# Week digest for a category + keywords
arxiv digest --period week --category cs.CL --keywords transformer --max-results 100

# Export to Markdown file
arxiv digest --period day --category cs.AI --keywords agents --export digest.md
```

Примечание: период фильтруется по `published` client-side после получения результатов (ограничены `--max-results`).

### `export`

Команда экспортирует **сохранённую локальную библиотеку** из файла `library.json` в OS data dir.
Путь можно переопределить флагом `--library`.

Пример структуры библиотеки (для ручного заполнения/отладки) см. `docs/library.example.json`.

#### 1) Экспорт всей библиотеки в BibTeX

```bash
arxiv export --format bibtex
```

#### 2) Экспорт всей библиотеки в CSL-JSON

```bash
arxiv export --format csl
```

#### 3) Фильтрация по тегу / категории

```bash
arxiv export --format bibtex --tag multilingual
arxiv export --format csl --category cs.LG
```

#### 4) Экспорт в файл

```bash
arxiv export --format bibtex --out refs.bib
arxiv export --format csl --out refs.json
```

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

- `arxiv track add` — добавление статьи в локальную библиотеку (fetch метаданных из arXiv)
  - задаёт `added_at`, `status`, `tags`

## Команды

- `arxiv search` — поиск
- `arxiv download` — скачивание PDF
- `arxiv export` — экспорт библиографии
- `arxiv track` — управление локальной библиотекой
- `arxiv list` — просмотр и поиск по локальной библиотеке
- (в планах) `arxiv digest`, `arxiv subscribe`

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

## Локальное хранилище

По умолчанию данные хранятся в user data dir ОС.
На macOS это обычно:

- `~/Library/Application Support/arxiv-cli/`
  - `library.json` — библиотека статей
  - `subscriptions.json` — подписки (пока заглушка, будет)
  - `state/` — состояние (last seen и т.п.)

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

### `list`

```bash
arxiv list --format table
arxiv list --status unread --tag transformers --format compact
arxiv list --from 2026-04-01 --to 2026-04-30 --sort added --order desc
arxiv list --q memorization
```

### `export`

> Команда экспортирует **сохранённую локальную библиотеку** из JSON-файла
> `./.arxiv-cli-library.json` (пока это минимальный формат хранения; позже сделаем `save/add`).
>
> Пример структуры см. `docs/library.example.json`.

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

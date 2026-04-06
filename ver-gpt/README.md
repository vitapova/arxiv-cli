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

## Команды

- `arxiv search` — поиск
- `arxiv download` — скачивание PDF
- (в планах) `arxiv digest`, `arxiv watch`, `arxiv export`

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

## Примеры

### Download одного PDF по id

```bash
arxiv download 2604.03199v1 --output-dir ./papers
```

Именование файла: `{id}_{first_author}_{year}.pdf`

### Batch download из файла

```bash
arxiv download --batch docs/batch_ids.txt --output-dir ./papers
```

Формат batch-файла: 1 id на строку, `#` — комментарии.


### 1) Raw запрос (как в документации arXiv)

```bash
arxiv "cat:cs.CL AND au:Smith" --per-page 5 --sort date
```

### 2) Запрос из флагов (повторяемые `--author`, `--category`)

```bash
arxiv --author "Yoshua Bengio" --category cs.LG --per-page 5 --sort date
```

### 3) Категория + full-text терм + диапазон дат + компактный формат

```bash
arxiv --category cs.CL --all transformer \
  --from 2026-04-01 --to 2026-04-05 \
  --page 1 --per-page 10 --sort date \
  --format compact
```

### 4) Таблица (по умолчанию)

```bash
arxiv --category cs.CL --all transformer --per-page 5 --sort date --format table
```

### 5) JSON

```bash
arxiv --category cs.CL --all transformer --per-page 2 --json
```

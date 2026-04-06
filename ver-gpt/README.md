# arxiv-cli (ver-gpt)

Консольная утилита для работы с arXiv: поиск, дайджесты, отслеживание сохранённых запросов, скачивание PDF, экспорт BibTeX/CSL.

Статус: **в разработке**.

## Что уже есть

- `arxiv search` — поиск по arXiv через export API
  - поддерживает raw `search_query` **или** сборку запроса из флагов (`--author/--category/--title/--abstract/--all/--id`)
  - `--json` для машинного вывода
  - `--since YYYY-MM-DD` (фильтр по published, применяется клиент-сайд)

## Планируемые команды

- `arxiv digest` — дайджест новых публикаций
- `arxiv watch` — отслеживание сохранённых запросов
- `arxiv pdf` — скачать PDF
- `arxiv export` — экспорт BibTeX/CSL

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

### 1) Raw запрос (как в документации arXiv)

```bash
arxiv "cat:cs.CL AND au:Smith" --max-results 5 --sort-by submittedDate
```

### 2) Запрос из флагов (повторяемые `--author`, `--category`)

```bash
arxiv --author "Yoshua Bengio" --category cs.LG --max-results 5 --sort-by submittedDate
```

### 3) Категория + full-text терм + фильтр по дате

```bash
arxiv --category cs.CL --all transformer --since 2026-04-01 --max-results 10 --sort-by submittedDate
```

### 4) JSON

```bash
arxiv --category cs.CL --all transformer --max-results 2 --json
```

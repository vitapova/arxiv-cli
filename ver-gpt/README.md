# arxiv-cli (ver-gpt)

Консольная утилита для работы с arXiv: поиск, дайджесты, отслеживание сохранённых запросов, скачивание PDF, экспорт BibTeX/CSL.

Статус: **скелет проекта** (без реализации).

## Планируемые команды (черновик)

- `arxiv search` — поиск статей
- `arxiv digest` — дайджест новых публикаций
- `arxiv watch` — отслеживание сохранённых запросов
- `arxiv pdf` — скачать PDF
- `arxiv export` — экспорт BibTeX/CSL

## Источник данных

arXiv API:
- `GET http://export.arxiv.org/api/query`
- параметры: `search_query`, `start`, `max_results`, `sortBy`, `sortOrder`

## Dev

Требования и сборка будут добавлены после выбора стека (Go/TS/Python) и CLI-фреймворка.

# Architecture (draft)

## Goals

- Удобный поиск по arXiv
- Дайджесты новых публикаций
- Watch/save запросов и уведомления/отчёты
- PDF download
- Экспорт BibTeX/CSL

## Data source

- `GET http://export.arxiv.org/api/query`
- Atom feed response

## Modules (planned)

- `internal/arxiv`: строит запросы, вызывает API, парсит Atom, маппит на доменные структуры.
- `internal/storage`: хранит сохранённые запросы, состояние (lastSeen), кэш.
- `internal/digest`: собирает списки/дайджесты из результатов.
- `internal/export`: формирует BibTeX/CSL.
- `internal/cli`: команды и UX.

## CLI UX (planned)

- Чёткие флаги: `--author`, `--category`, `--query`, `--since`, `--sort`.
- Форматы вывода: text/json.

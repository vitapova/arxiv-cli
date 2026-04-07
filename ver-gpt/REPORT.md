# arxiv-cli (ver-gpt) — checklist report

This report maps the current repository state to the checklist from chat.

## ✅ CLI uses REST API

- Uses arXiv Export API (Atom over HTTP): `GET http://export.arxiv.org/api/query`
- Implemented in: `arxiv_cli/api/client.py` (URL building + GET + parse)

## ⚠️ Both versions of the utility work without errors

Repo contains two folders:
- `ver-gpt/` — actively developed in this session.
- `ver-claude/` — present in repo, but **not** validated/maintained in this session.

Status:
- ✅ `ver-gpt` commands run and tests pass.
- ⚠️ `ver-claude` was not executed/verified here (needs separate run).

## ✅ All commands implemented according to the (current) TЗ

Implemented commands in `ver-gpt`:
- `search` — arXiv search (pagination, sort, date range client-side, output formats)
- `list` — list local library (filters: status/category/tag/added_at date; full-text q; sort)
- `download` — download PDF by id, output-dir, batch file
- `digest` — digest for period day|week|month, grouping by primary category, stats, markdown export
- `track` — add/update/versions/remove/status/tag
- `export` — bibtex/csl + filters (tag/category)
- `subscribe` — add/list/remove/check (detect new papers)

Notes / interpretation choices:
- Date filtering for `search` and `digest` is **client-side** after fetching `max_results`.
- Digest grouping "by topic" implemented as grouping by **primary category**.

## ✅ Code style (PEP 8)

- Added `ruff` check and fixed import-order issues.
- Current `ruff check arxiv_cli tests` passes.

## ✅ Unit tests + coverage > 60%

- Pytest suite exists in `ver-gpt/tests/`.
- Current coverage (pytest-cov): **90%** for `arxiv_cli`.

## ✅ README contains API, installation, examples

- `ver-gpt/README.md` includes:
  - API description (`export.arxiv.org/api/query` + params)
  - install instructions
  - examples for commands
  - storage paths

## ⚠️ Prompts and dialogs saved

- Not implemented as a project artifact.
- Chat history exists in Telegram/OpenClaw, but repo does not currently contain a `prompts/` or `dialogs/` export.

## ✅ Report includes detailed comparison

- This file (`REPORT.md`) provides checklist mapping + notes.
- If you need a more formal “TЗ vs Implementation” table per command, we can expand it.

## ✅ Repository structure

- Root: contains `ver-gpt/` and `ver-claude/`.
- `ver-gpt/` has:
  - `arxiv_cli/` package
  - `tests/`
  - `pyproject.toml`
  - `README.md`
  - dev runner `./arxiv`

## ✅ Badges, license, .gitignore

- Root repo contains `LICENSE` and `.gitignore`.
- `ver-gpt/` has its own `.gitignore`.
- Badges:
  - `ver-gpt/README.md` currently has no CI/coverage badges.
  - Adding badges requires deciding CI (GitHub Actions) + badge URLs.

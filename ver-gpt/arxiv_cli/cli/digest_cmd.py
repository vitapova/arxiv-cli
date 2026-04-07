from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import typer

from arxiv_cli.api.client import ArxivClient, ArxivQuery
from arxiv_cli.digest.generator import build_digest, digest_to_markdown


def _period_range(period: str, today: date) -> tuple[date, date]:
    if period == "day":
        return today - timedelta(days=1), today
    if period == "week":
        return today - timedelta(days=7), today
    if period == "month":
        return today - timedelta(days=30), today
    raise typer.BadParameter("--period must be day|week|month")


def _build_search_query(keywords: Optional[str], categories: list[str]) -> str:
    parts: list[str] = []

    if keywords:
        q = keywords.replace('"', "").strip()
        if " " in q:
            q = f'"{q}"'
        parts.append(f"all:{q}")

    if categories:
        cats = " OR ".join(f"cat:{c}" for c in categories)
        parts.append(f"({cats})")

    if not parts:
        raise typer.BadParameter("Provide --keywords and/or --category")

    return " AND ".join(parts)


def add_digest_command(app: typer.Typer) -> None:
    @app.command("digest")
    def digest(
        period: str = typer.Option("week", "--period", help="day|week|month"),
        category: list[str] = typer.Option([], "--category", "--cat", help="Category filter (repeatable)"),
        keywords: Optional[str] = typer.Option(None, "--keywords", "-k", help="Keyword query (used as all:<keywords>)"),
        max_results: int = typer.Option(100, "--max-results", help="How many papers to fetch before filtering"),
        export: Optional[Path] = typer.Option(None, "--export", help="Export digest to Markdown file"),
    ) -> None:
        """Build digest of new papers for a period."""

        today = date.today()
        from_d, to_d = _period_range(period, today)
        search_q = _build_search_query(keywords, category)

        client = ArxivClient(timeout_s=60.0)
        q = ArxivQuery(
            search_query=search_q,
            start=0,
            max_results=max_results,
            sortBy="submittedDate",
            sortOrder="descending",
        )

        try:
            papers = client.search(q)
        except Exception as e:
            typer.echo(f"ERR\t{type(e).__name__}: {e}")
            raise typer.Exit(code=2)

        # Filter client-side by published date.
        filtered = []
        for p in papers:
            if not p.published:
                continue
            pd = p.published.date()
            if pd < from_d or pd > to_d:
                continue
            filtered.append(p)

        d = build_digest(filtered, period=period, from_date=from_d, to_date=to_d)
        md = digest_to_markdown(d, query_desc=search_q)

        # Always print to stdout; optionally also export.
        typer.echo(md, nl=False)
        if export:
            export.write_text(md, encoding="utf-8")
            typer.echo(f"\nExported\t{export}")

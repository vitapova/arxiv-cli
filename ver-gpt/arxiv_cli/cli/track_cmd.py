from __future__ import annotations

from typing import Optional

import typer

from arxiv_cli.api.metadata import fetch_paper_by_id
from arxiv_cli.api.utils import normalize_arxiv_id
from arxiv_cli.storage.library import Library
from arxiv_cli.storage.schema import ArticleRecord, now_iso


def add_track_commands(app: typer.Typer) -> None:
    track_app = typer.Typer(help="Track/save papers in the local library")

    @track_app.command("add")
    def add(
        arxiv_id: str = typer.Argument(..., help="arXiv id or URL"),
        tag: list[str] = typer.Option([], "--tag", help="Tag(s) to attach"),
        status: str = typer.Option("unread", "--status", help="unread|read|starred"),
    ) -> None:
        """Add a paper to the local library (fetches metadata from arXiv)."""
        if status not in {"unread", "read", "starred"}:
            raise typer.BadParameter("--status must be unread|read|starred")

        norm = normalize_arxiv_id(arxiv_id)
        paper = fetch_paper_by_id(norm)
        if paper is None:
            raise typer.Exit(code=2)

        rec = ArticleRecord(
            arxiv_id=paper.arxiv_id,
            title=paper.title,
            summary=paper.summary,
            authors=paper.authors,
            categories=paper.categories,
            published=paper.published.isoformat() if paper.published else None,
            updated=paper.updated.isoformat() if paper.updated else None,
            added_at=now_iso(),
            status=status,  # type: ignore[arg-type]
            tags=list(tag),
            links=paper.links,
        )

        Library().upsert(rec)
        typer.echo(f"Saved\t{rec.arxiv_id}")

    app.add_typer(track_app, name="track")

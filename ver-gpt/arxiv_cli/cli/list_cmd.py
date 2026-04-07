from __future__ import annotations

from datetime import date
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from arxiv_cli.storage.library import Library
from arxiv_cli.storage.schema import ArticleRecord


def _parse_date(s: str, flag: str) -> date:
    try:
        return date.fromisoformat(s)
    except ValueError as e:
        raise typer.BadParameter(f"{flag} must be YYYY-MM-DD") from e


def _added_date(rec: ArticleRecord) -> Optional[date]:
    if not rec.added_at:
        return None
    # Expect ISO like 2026-04-07T10:23:18+03:00
    try:
        return date.fromisoformat(rec.added_at[0:10])
    except ValueError:
        return None


def _matches_query(rec: ArticleRecord, q: str) -> bool:
    q = q.strip().lower()
    if not q:
        return True
    hay = (rec.title or "") + "\n" + (rec.summary or "")
    return q in hay.lower()


def _build_table(items: list[ArticleRecord]) -> Table:
    table = Table(title=f"Library ({len(items)})")
    table.add_column("id", no_wrap=True)
    table.add_column("status", no_wrap=True)
    table.add_column("added", no_wrap=True)
    table.add_column("published", no_wrap=True)
    table.add_column("cat", no_wrap=True)
    table.add_column("tags")
    table.add_column("title")

    for it in items:
        added = (it.added_at or "")[0:10] if it.added_at else ""
        pub = (it.published or "")[0:10] if it.published else ""
        cats = ",".join(it.categories[:2]) + ("…" if len(it.categories) > 2 else "")
        tags = ",".join(it.tags)
        table.add_row(it.arxiv_id, it.status, added, pub, cats, tags, it.title)

    return table


def add_list_command(app: typer.Typer) -> None:
    @app.command("list")
    def list_cmd(
        status: Optional[str] = typer.Option(None, "--status", help="read|unread|starred"),
        category: list[str] = typer.Option([], "--category", "--cat", help="Filter by category (repeatable)"),
        tag: list[str] = typer.Option([], "--tag", help="Filter by tag (repeatable)"),
        added_from: Optional[str] = typer.Option(None, "--from", help="Added date from (YYYY-MM-DD), inclusive"),
        added_to: Optional[str] = typer.Option(None, "--to", help="Added date to (YYYY-MM-DD), inclusive"),
        q: Optional[str] = typer.Option(None, "--q", help="Full-text query over title+summary"),
        sort: str = typer.Option("added", "--sort", help="added|published|updated|title"),
        order: str = typer.Option("desc", "--order", help="asc|desc"),
        format_: str = typer.Option("table", "--format", help="table|compact|json"),
    ) -> None:
        """List saved local library with filters."""

        if status is not None and status not in {"read", "unread", "starred"}:
            raise typer.BadParameter("--status must be read|unread|starred")
        if sort not in {"added", "published", "updated", "title"}:
            raise typer.BadParameter("--sort must be added|published|updated|title")
        if order not in {"asc", "desc"}:
            raise typer.BadParameter("--order must be asc|desc")
        if format_ not in {"table", "compact", "json"}:
            raise typer.BadParameter("--format must be table|compact|json")

        from_d = _parse_date(added_from, "--from") if added_from else None
        to_d = _parse_date(added_to, "--to") if added_to else None
        if from_d and to_d and from_d > to_d:
            raise typer.BadParameter("--from must be <= --to")

        items = Library().load()

        if status:
            items = [it for it in items if it.status == status]

        if category:
            cats = set(category)
            items = [it for it in items if cats.intersection(it.categories)]

        if tag:
            tags = set(tag)
            items = [it for it in items if tags.intersection(it.tags)]

        if from_d or to_d:
            filtered: list[ArticleRecord] = []
            for it in items:
                d = _added_date(it)
                if d is None:
                    continue
                if from_d and d < from_d:
                    continue
                if to_d and d > to_d:
                    continue
                filtered.append(it)
            items = filtered

        if q:
            items = [it for it in items if _matches_query(it, q)]

        reverse = order == "desc"

        def key_added(it: ArticleRecord) -> str:
            return it.added_at or ""

        def key_published(it: ArticleRecord) -> str:
            return it.published or ""

        def key_updated(it: ArticleRecord) -> str:
            return it.updated or ""

        def key_title(it: ArticleRecord) -> str:
            return (it.title or "").lower()

        key_map = {
            "added": key_added,
            "published": key_published,
            "updated": key_updated,
            "title": key_title,
        }

        items.sort(key=key_map[sort], reverse=reverse)

        if format_ == "json":
            import json

            typer.echo(json.dumps([Library()._to_dict(it) for it in items], ensure_ascii=False, indent=2) + "\n")
            return

        if format_ == "compact":
            for it in items:
                added = (it.added_at or "")[0:10] if it.added_at else ""
                pub = (it.published or "")[0:10] if it.published else ""
                cats = ",".join(it.categories)
                tags = ",".join(it.tags)
                typer.echo(f"{it.arxiv_id}\t{it.status}\t{added}\t{pub}\t{cats}\t{tags}\t{it.title}")
            return

        console = Console()
        console.print(_build_table(items))

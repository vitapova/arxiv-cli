from __future__ import annotations

from typing import Optional

import typer

from arxiv_cli.api.metadata import fetch_latest_by_base_id, fetch_paper_by_id
from arxiv_cli.api.utils import base_arxiv_id, normalize_arxiv_id, parse_version
from arxiv_cli.storage.library import Library
from arxiv_cli.storage.schema import ArticleRecord, now_iso
from arxiv_cli.storage.history import VersionEvent
from arxiv_cli.storage.tracking import TrackingStore


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

    @track_app.command("remove")
    def remove(
        arxiv_id: str = typer.Argument(..., help="arXiv id or URL"),
    ) -> None:
        """Remove a paper from the local library."""
        norm = normalize_arxiv_id(arxiv_id)
        lib = Library()
        items = lib.load()
        before = len(items)
        items = [it for it in items if it.arxiv_id != norm]
        if len(items) == before:
            typer.echo(f"Not found\t{norm}")
            raise typer.Exit(code=1)
        lib.save(items)
        typer.echo(f"Removed\t{norm}")

    @track_app.command("update")
    def update() -> None:
        """Update tracked library items by checking for newer arXiv versions."""
        lib = Library()
        items = lib.load()
        if not items:
            typer.echo("Library is empty")
            return

        store = TrackingStore()
        updated_count = 0

        for it in items:
            base_id = base_arxiv_id(it.arxiv_id)
            latest = fetch_latest_by_base_id(base_id)
            if latest is None:
                continue

            current_v = it.version or parse_version(it.arxiv_id) or 1
            latest_v = parse_version(latest.arxiv_id) or 1

            # Record history event if we haven't seen this version.
            store.append(
                VersionEvent(
                    arxiv_base_id=base_id,
                    seen_version=latest_v,
                    seen_at=now_iso(),
                    updated=latest.updated.isoformat() if latest.updated else None,
                )
            )

            if latest_v <= current_v:
                continue

            # Update record in library to the latest version + refreshed metadata
            new_rec = ArticleRecord(
                arxiv_id=latest.arxiv_id,
                title=latest.title,
                summary=latest.summary,
                authors=latest.authors,
                categories=latest.categories,
                published=latest.published.isoformat() if latest.published else it.published,
                updated=latest.updated.isoformat() if latest.updated else it.updated,
                added_at=it.added_at,
                status=it.status,
                tags=it.tags,
                links=latest.links,
                version=latest_v,
            )
            lib.upsert(new_rec)
            updated_count += 1
            typer.echo(f"Updated\t{base_id}\tv{current_v} -> v{latest_v}")

        typer.echo(f"\nUpdated items: {updated_count}")

    @track_app.command("versions")
    def versions(
        arxiv_id: str = typer.Argument(..., help="arXiv id or URL"),
    ) -> None:
        """Show version history for a tracked paper."""
        norm = normalize_arxiv_id(arxiv_id)
        base_id = base_arxiv_id(norm)
        events = TrackingStore().get(base_id)
        if not events:
            typer.echo(f"No version history\t{base_id}")
            raise typer.Exit(code=1)

        for e in events:
            upd = (e.updated or "")
            typer.echo(f"{base_id}\tv{e.seen_version}\tseen_at={e.seen_at}\tupdated={upd}")

    @track_app.command("status")
    def status_cmd(
        arxiv_id: str = typer.Argument(..., help="arXiv id or URL"),
        set_: str = typer.Option(..., "--set", help="read|unread|starred"),
    ) -> None:
        """Set local status for a saved paper."""
        if set_ not in {"read", "unread", "starred"}:
            raise typer.BadParameter("--set must be read|unread|starred")

        norm = normalize_arxiv_id(arxiv_id)
        lib = Library()
        items = lib.load()
        found = False
        for it in items:
            if it.arxiv_id == norm:
                it.status = set_  # type: ignore[assignment]
                found = True
                break

        if not found:
            typer.echo(f"Not found\t{norm}")
            raise typer.Exit(code=1)

        lib.save(items)
        typer.echo(f"OK\t{norm}\tstatus={set_}")

    @track_app.command("tag")
    def tag_cmd(
        arxiv_id: str = typer.Argument(..., help="arXiv id or URL"),
        add: list[str] = typer.Option([], "--add", help="Tag(s) to add (repeatable)"),
        remove: list[str] = typer.Option([], "--remove", help="Tag(s) to remove (repeatable)"),
    ) -> None:
        """Add/remove local tags for a saved paper."""
        if not add and not remove:
            raise typer.BadParameter("Provide --add and/or --remove")

        norm = normalize_arxiv_id(arxiv_id)
        lib = Library()
        items = lib.load()
        for it in items:
            if it.arxiv_id != norm:
                continue

            tagset = set(it.tags)
            for t in add:
                t = t.strip()
                if t:
                    tagset.add(t)
            for t in remove:
                t = t.strip()
                if t:
                    tagset.discard(t)

            it.tags = sorted(tagset)
            lib.save(items)
            typer.echo(f"OK\t{norm}\ttags={','.join(it.tags)}")
            return

        typer.echo(f"Not found\t{norm}")
        raise typer.Exit(code=1)

    app.add_typer(track_app, name="track")

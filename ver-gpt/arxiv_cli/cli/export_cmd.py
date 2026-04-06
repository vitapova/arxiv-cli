from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from arxiv_cli.export.bibtex import bibtex_dump
from arxiv_cli.export.csl import csl_dump
from arxiv_cli.storage.library import Library, default_library_path


def add_export_command(app: typer.Typer) -> None:
    @app.command("export")
    def export(
        format_: str = typer.Option("bibtex", "--format", help="bibtex|csl"),
        library_path: Path = typer.Option(
            default_library_path(),
            "--library",
            help="Path to local library JSON (default: ./.arxiv-cli-library.json)",
        ),
        tag: list[str] = typer.Option([], "--tag", help="Filter by tag (repeatable)"),
        category: list[str] = typer.Option([], "--category", "--cat", help="Filter by category (repeatable)"),
        out: Optional[Path] = typer.Option(None, "--out", help="Write output to file instead of stdout"),
    ) -> None:
        """Export bibliographic data for saved library items."""

        if format_ not in {"bibtex", "csl"}:
            raise typer.BadParameter("--format must be bibtex or csl")

        items = Library(library_path).load()

        if tag:
            tag_set = set(tag)
            items = [it for it in items if tag_set.intersection(it.tags)]

        if category:
            cat_set = set(category)
            items = [it for it in items if cat_set.intersection(it.categories)]

        if format_ == "bibtex":
            text = bibtex_dump(items)
        else:
            text = csl_dump(items)

        if out:
            out.write_text(text, encoding="utf-8")
        else:
            typer.echo(text, nl=False)

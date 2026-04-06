from __future__ import annotations

from typing import Iterable

from rich.table import Table

from arxiv_cli.api.models import Paper


def _short_authors(p: Paper, n: int = 3) -> str:
    if not p.authors:
        return ""
    s = ", ".join(p.authors[:n])
    if len(p.authors) > n:
        s += " et al."
    return s


def format_papers_text(papers: Iterable[Paper], *, show_summary: bool = False) -> str:
    """Verbose multi-line output (default)."""
    lines: list[str] = []
    for i, p in enumerate(papers, start=1):
        cats = ",".join(p.categories)
        pub = p.published.date().isoformat() if p.published else "?"
        lines.append(f"{i}. {p.title}")
        lines.append(f"   id: {p.arxiv_id}  published: {pub}")
        authors = ", ".join(p.authors[:5]) + (" et al." if len(p.authors) > 5 else "")
        if authors:
            lines.append(f"   authors: {authors}")
        if cats:
            lines.append(f"   categories: {cats}")
        if p.links.get("abs"):
            lines.append(f"   abs: {p.links['abs']}")
        if p.pdf_url:
            lines.append(f"   pdf: {p.pdf_url}")
        if show_summary and p.summary:
            lines.append(f"   summary: {p.summary}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n" if lines else ""


def format_papers_compact(papers: Iterable[Paper]) -> str:
    """Compact one-line-per-paper output."""
    lines: list[str] = []
    for p in papers:
        pub = p.published.date().isoformat() if p.published else "?"
        authors = _short_authors(p)
        cats = ",".join(p.categories)
        lines.append(f"{p.arxiv_id}\t{pub}\t{cats}\t{authors}\t{p.title}")
    return "\n".join(lines).rstrip() + "\n" if lines else ""


def build_papers_table(papers: Iterable[Paper]) -> Table:
    """Rich table for terminal rendering."""
    table = Table(title="arXiv results", show_lines=False)
    table.add_column("id", no_wrap=True)
    table.add_column("published", no_wrap=True)
    table.add_column("cat", no_wrap=True)
    table.add_column("authors")
    table.add_column("title")

    for p in papers:
        pub = p.published.date().isoformat() if p.published else "?"
        cats = ",".join(p.categories[:2]) + ("…" if len(p.categories) > 2 else "")
        table.add_row(p.arxiv_id, pub, cats, _short_authors(p), p.title)

    return table

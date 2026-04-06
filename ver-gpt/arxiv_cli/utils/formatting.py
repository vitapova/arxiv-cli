from __future__ import annotations

from typing import Iterable

from arxiv_cli.api.models import Paper


def format_papers_text(papers: Iterable[Paper], *, show_summary: bool = False) -> str:
    lines: list[str] = []
    for i, p in enumerate(papers, start=1):
        authors = ", ".join(p.authors[:5]) + (" et al." if len(p.authors) > 5 else "")
        cats = ",".join(p.categories)
        pub = p.published.date().isoformat() if p.published else "?"
        lines.append(f"{i}. {p.title}")
        lines.append(f"   id: {p.arxiv_id}  published: {pub}")
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

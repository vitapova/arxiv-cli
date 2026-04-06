from __future__ import annotations

from typing import Iterable

from arxiv_cli.storage.library import LibraryItem


def _bibtex_key(item: LibraryItem) -> str:
    # {id}_{first_author}_{year} style key (without punctuation issues)
    first_author = (item.authors[0] if item.authors else "unknown").split()[-1]
    year = (item.published or "")[0:4] or "????"
    base = f"{item.arxiv_id}_{first_author}_{year}"
    # BibTeX keys: keep simple
    return "".join(ch for ch in base if ch.isalnum() or ch in "_-:")


def bibtex_dump(items: Iterable[LibraryItem]) -> str:
    entries: list[str] = []
    for it in items:
        key = _bibtex_key(it)
        authors = " and ".join(it.authors)
        year = (it.published or "")[0:4]
        fields = {
            "title": it.title,
            "author": authors,
            "year": year,
            "eprint": it.arxiv_id,
            "archivePrefix": "arXiv",
            "primaryClass": it.categories[0] if it.categories else "",
        }
        # Minimal escaping: wrap in braces
        lines = [f"@misc{{{key},"]
        for k, v in fields.items():
            if not v:
                continue
            lines.append(f"  {k} = {{{v}}},")
        # remove trailing comma on last field
        if lines[-1].endswith(","):
            lines[-1] = lines[-1][:-1]
        lines.append("}")
        entries.append("\n".join(lines))
    return "\n\n".join(entries).rstrip() + ("\n" if entries else "")

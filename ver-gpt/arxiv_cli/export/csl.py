from __future__ import annotations

from typing import Any, Iterable

from arxiv_cli.storage.library import LibraryItem


def csl_dump(items: Iterable[LibraryItem]) -> str:
    out: list[dict[str, Any]] = []
    for it in items:
        year = None
        if it.published and len(it.published) >= 4:
            try:
                year = int(it.published[0:4])
            except ValueError:
                year = None

        out.append(
            {
                "id": it.arxiv_id,
                "type": "article",
                "title": it.title,
                "author": [{"literal": a} for a in it.authors],
                "issued": {"date-parts": [[year]]} if year else None,
                "archive": "arXiv",
                "archive_location": it.arxiv_id,
                "categories": it.categories,
                "tags": it.tags,
                "URL": f"https://arxiv.org/abs/{it.arxiv_id}",
            }
        )

    # Strip None values
    for obj in out:
        for k in list(obj.keys()):
            if obj[k] is None:
                del obj[k]

    import json

    return json.dumps(out, ensure_ascii=False, indent=2) + "\n"

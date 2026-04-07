from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date

from arxiv_cli.api.models import Paper


@dataclass
class Digest:
    period: str
    from_date: date
    to_date: date
    total: int
    by_category: dict[str, int]
    groups: dict[str, list[Paper]]


def build_digest(
    papers: list[Paper],
    *,
    period: str,
    from_date: date,
    to_date: date,
) -> Digest:
    # stats by primary category
    counts = Counter()
    groups: dict[str, list[Paper]] = defaultdict(list)

    for p in papers:
        primary = p.categories[0] if p.categories else "unknown"
        counts[primary] += 1
        groups[primary].append(p)

    # sort papers inside groups by published desc
    for k in list(groups.keys()):
        groups[k].sort(key=lambda x: x.published.isoformat() if x.published else "", reverse=True)

    # sort groups by count desc then name
    sorted_groups = dict(sorted(groups.items(), key=lambda kv: (-counts[kv[0]], kv[0])))

    return Digest(
        period=period,
        from_date=from_date,
        to_date=to_date,
        total=len(papers),
        by_category=dict(counts),
        groups=sorted_groups,
    )


def digest_to_markdown(d: Digest, *, query_desc: str) -> str:
    lines: list[str] = []
    lines.append(f"# arXiv digest ({d.period})")
    lines.append("")
    lines.append(f"Period: **{d.from_date.isoformat()}** → **{d.to_date.isoformat()}**")
    lines.append(f"Query: `{query_desc}`")
    lines.append(f"Total papers: **{d.total}**")
    lines.append("")

    # Stats
    lines.append("## Stats")
    lines.append("")
    lines.append("| Category | New papers |")
    lines.append("|---|---:|")
    for cat, n in sorted(d.by_category.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| {cat} | {n} |")
    lines.append("")

    # Groups
    lines.append("## Papers")
    lines.append("")
    for theme, papers in d.groups.items():
        lines.append(f"### {theme} ({len(papers)})")
        lines.append("")
        for p in papers:
            pub = p.published.date().isoformat() if p.published else "?"
            authors = ", ".join(p.authors[:8]) + (" et al." if len(p.authors) > 8 else "")
            abs_url = p.links.get("abs", f"https://arxiv.org/abs/{p.arxiv_id}")
            pdf_url = p.pdf_url or f"https://arxiv.org/pdf/{p.arxiv_id}.pdf"
            lines.append(f"- **{p.title}**  ")
            lines.append(f"  - id: `{p.arxiv_id}` | published: {pub}")
            if authors:
                lines.append(f"  - authors: {authors}")
            lines.append(f"  - links: [abs]({abs_url}) · [pdf]({pdf_url})")
            if p.summary:
                lines.append(f"  - summary: {p.summary}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"

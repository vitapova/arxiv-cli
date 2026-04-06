from __future__ import annotations

from datetime import datetime
from typing import Optional
from xml.etree import ElementTree as ET

from .models import Paper


NS = {
    "atom": "http://www.w3.org/2005/Atom",
}


def _text(el: Optional[ET.Element]) -> str:
    if el is None or el.text is None:
        return ""
    return el.text.strip()


def _parse_dt(s: str) -> Optional[datetime]:
    s = s.strip()
    if not s:
        return None
    # arXiv uses RFC3339-like: 2020-01-01T00:00:00Z
    try:
        if s.endswith("Z"):
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def parse_feed(xml_text: str) -> list[Paper]:
    """Parse arXiv Atom feed XML into list of Paper."""
    root = ET.fromstring(xml_text)
    papers: list[Paper] = []

    for entry in root.findall("atom:entry", NS):
        entry_id = _text(entry.find("atom:id", NS))
        # arXiv id is last path segment in the entry id URL
        arxiv_id = entry_id.rsplit("/", 1)[-1] if entry_id else ""

        title = " ".join(_text(entry.find("atom:title", NS)).split())
        summary = " ".join(_text(entry.find("atom:summary", NS)).split())

        authors = [
            _text(a.find("atom:name", NS))
            for a in entry.findall("atom:author", NS)
            if _text(a.find("atom:name", NS))
        ]

        categories = [
            c.attrib.get("term", "").strip()
            for c in entry.findall("atom:category", NS)
            if c.attrib.get("term")
        ]

        published = _parse_dt(_text(entry.find("atom:published", NS)))
        updated = _parse_dt(_text(entry.find("atom:updated", NS)))

        links: dict[str, str] = {}
        for link in entry.findall("atom:link", NS):
            href = link.attrib.get("href")
            rel = link.attrib.get("rel", "")
            ltype = link.attrib.get("type", "")
            title_attr = link.attrib.get("title", "")
            if not href:
                continue

            # Typical patterns:
            # - rel="alternate" -> abstract page
            # - title="pdf" or type="application/pdf" -> pdf
            if title_attr.lower() == "pdf" or ltype == "application/pdf" or rel.endswith("/pdf"):
                links.setdefault("pdf", href)
            elif rel == "alternate":
                links.setdefault("abs", href)

        papers.append(
            Paper(
                arxiv_id=arxiv_id,
                title=title,
                summary=summary,
                authors=authors,
                categories=categories,
                published=published,
                updated=updated,
                links=links,
            )
        )

    return papers

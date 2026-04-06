from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .parser import parse_feed


ARXIV_API_URL = "http://export.arxiv.org/api/query"

SortBy = Literal[
    "relevance",
    "lastUpdatedDate",
    "submittedDate",
]

SortOrder = Literal["ascending", "descending"]


@dataclass(frozen=True)
class ArxivQuery:
    search_query: str
    start: int = 0
    max_results: int = 10
    sortBy: SortBy = "relevance"
    sortOrder: SortOrder = "descending"


class ArxivClient:
    def __init__(self, base_url: str = ARXIV_API_URL, timeout_s: float = 20.0):
        self.base_url = base_url
        self.timeout_s = timeout_s

    def build_url(self, q: ArxivQuery) -> str:
        params = {
            "search_query": q.search_query,
            "start": str(max(q.start, 0)),
            "max_results": str(min(max(q.max_results, 1), 2000)),
            "sortBy": q.sortBy,
            "sortOrder": q.sortOrder,
        }
        return f"{self.base_url}?{urlencode(params)}"

    def search(self, q: ArxivQuery, user_agent: Optional[str] = None):
        url = self.build_url(q)
        headers = {
            "Accept": "application/atom+xml, application/xml;q=0.9, */*;q=0.1",
        }
        if user_agent:
            headers["User-Agent"] = user_agent

        req = Request(url, headers=headers, method="GET")
        with urlopen(req, timeout=self.timeout_s) as resp:
            xml_bytes = resp.read()

        xml_text = xml_bytes.decode("utf-8", errors="replace")
        return parse_feed(xml_text)

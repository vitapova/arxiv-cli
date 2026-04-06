from __future__ import annotations

from arxiv_cli.api.client import ArxivClient, ArxivQuery


def fetch_paper_by_id(arxiv_id: str):
    """Fetch single paper metadata by arXiv id."""
    client = ArxivClient()
    q = ArxivQuery(search_query=f"id:{arxiv_id}", start=0, max_results=1)
    papers = client.search(q)
    return papers[0] if papers else None

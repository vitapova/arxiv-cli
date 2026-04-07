from __future__ import annotations

from arxiv_cli.api.client import ArxivClient, ArxivQuery


def fetch_paper_by_id(arxiv_id: str):
    """Fetch single paper metadata by arXiv id (can include version)."""
    client = ArxivClient()
    q = ArxivQuery(search_query=f"id:{arxiv_id}", start=0, max_results=1)
    papers = client.search(q)
    return papers[0] if papers else None


def fetch_latest_by_base_id(base_id: str):
    """Fetch latest version for a base arXiv id (without vN).

    We query by id:<base> and sort by lastUpdatedDate descending.
    """
    client = ArxivClient()
    q = ArxivQuery(
        search_query=f"id:{base_id}",
        start=0,
        max_results=5,
        sortBy="lastUpdatedDate",
        sortOrder="descending",
    )
    papers = client.search(q)
    return papers[0] if papers else None

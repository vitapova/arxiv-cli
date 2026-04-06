from __future__ import annotations

import json
from typing import Optional

import typer

from arxiv_cli.api.client import ArxivClient, ArxivQuery
from arxiv_cli.utils.formatting import format_papers_text

app = typer.Typer(add_completion=False, help="CLI for arXiv: search, digests, watch, PDF, export")


@app.command("search")
def search(
    query: str = typer.Argument(..., help="Raw arXiv search_query (e.g. 'cat:cs.CL AND au:Smith')"),
    start: int = typer.Option(0, help="Result offset"),
    max_results: int = typer.Option(10, "--max-results", help="Number of results to fetch"),
    sort_by: str = typer.Option("relevance", "--sort-by", help="relevance|lastUpdatedDate|submittedDate"),
    sort_order: str = typer.Option("descending", "--sort-order", help="ascending|descending"),
    json_out: bool = typer.Option(False, "--json", help="Output JSON"),
    summary: bool = typer.Option(False, "--summary", help="Include summary in text output"),
    user_agent: Optional[str] = typer.Option(None, "--user-agent", help="Custom User-Agent"),
) -> None:
    """Search arXiv via the official export API."""
    client = ArxivClient()
    q = ArxivQuery(
        search_query=query,
        start=start,
        max_results=max_results,
        sortBy=sort_by,  # validated later
        sortOrder=sort_order,  # validated later
    )

    try:
        papers = client.search(q, user_agent=user_agent)
    except Exception as e:
        raise typer.Exit(code=2) from e

    if json_out:
        typer.echo(json.dumps([p.to_dict() for p in papers], ensure_ascii=False, indent=2))
    else:
        typer.echo(format_papers_text(papers, show_summary=summary), nl=False)


def main() -> None:
    app()


if __name__ == "__main__":
    main()

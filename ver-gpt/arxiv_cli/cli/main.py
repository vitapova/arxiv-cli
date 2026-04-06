from __future__ import annotations

import json
from typing import Optional

import typer

from arxiv_cli.api.client import ArxivClient, ArxivQuery
from arxiv_cli.utils.formatting import format_papers_text

app = typer.Typer(add_completion=False, help="CLI for arXiv: search, digests, watch, PDF, export")


@app.command("search")
def search(
    raw_query: Optional[str] = typer.Argument(
        None,
        help="Raw arXiv search_query (e.g. 'cat:cs.CL AND au:Smith'). If omitted, it will be built from flags.",
    ),
    author: list[str] = typer.Option(
        [],
        "--author",
        "-a",
        help="Author name (repeatable). Builds au:<value>",
    ),
    category: list[str] = typer.Option(
        [],
        "--category",
        "--cat",
        "-c",
        help="arXiv category (repeatable), e.g. cs.CL. Builds cat:<value>",
    ),
    title: Optional[str] = typer.Option(None, "--title", help="Search in title. Builds ti:<value>"),
    abstract: Optional[str] = typer.Option(None, "--abstract", help="Search in abstract. Builds abs:<value>"),
    all_fields: Optional[str] = typer.Option(None, "--all", help="Full-text style search. Builds all:<value>"),
    arxiv_id: Optional[str] = typer.Option(None, "--id", help="Exact arXiv id (e.g. 2402.05964v2). Builds id:<value>"),
    since: Optional[str] = typer.Option(
        None,
        "--since",
        help="Filter results by published date (YYYY-MM-DD). Applied client-side.",
    ),
    start: int = typer.Option(0, help="Result offset"),
    max_results: int = typer.Option(10, "--max-results", help="Number of results to fetch"),
    sort_by: str = typer.Option("relevance", "--sort-by", help="relevance|lastUpdatedDate|submittedDate"),
    sort_order: str = typer.Option("descending", "--sort-order", help="ascending|descending"),
    json_out: bool = typer.Option(False, "--json", help="Output JSON"),
    summary: bool = typer.Option(False, "--summary", help="Include summary in text output"),
    user_agent: Optional[str] = typer.Option(None, "--user-agent", help="Custom User-Agent"),
) -> None:
    """Search arXiv via the official export API."""

    allowed_sort_by = {"relevance", "lastUpdatedDate", "submittedDate"}
    allowed_sort_order = {"ascending", "descending"}
    if sort_by not in allowed_sort_by:
        raise typer.BadParameter(f"sort-by must be one of: {', '.join(sorted(allowed_sort_by))}")
    if sort_order not in allowed_sort_order:
        raise typer.BadParameter(f"sort-order must be one of: {', '.join(sorted(allowed_sort_order))}")

    def term(field: str, value: str) -> str:
        # If user passes a complex value with spaces, wrap in quotes for arXiv syntax.
        v = value.strip()
        if not v:
            return ""
        if any(ch.isspace() for ch in v):
            v = '"' + v.replace('"', "") + '"'
        return f"{field}:{v}"

    built_parts: list[str] = []
    built_parts += [term("au", a) for a in author]
    built_parts += [term("cat", c) for c in category]
    if title:
        built_parts.append(term("ti", title))
    if abstract:
        built_parts.append(term("abs", abstract))
    if all_fields:
        built_parts.append(term("all", all_fields))
    if arxiv_id:
        built_parts.append(term("id", arxiv_id))
    built_parts = [p for p in built_parts if p]

    query = raw_query.strip() if raw_query else ""
    if not query:
        if not built_parts:
            raise typer.BadParameter("Provide QUERY or at least one of: --author/--category/--title/--abstract/--all/--id")
        query = " AND ".join(built_parts)

    since_date = None
    if since:
        try:
            from datetime import date

            since_date = date.fromisoformat(since)
        except ValueError as e:
            raise typer.BadParameter("--since must be YYYY-MM-DD") from e

    client = ArxivClient()
    q = ArxivQuery(
        search_query=query,
        start=start,
        max_results=max_results,
        sortBy=sort_by,
        sortOrder=sort_order,
    )

    try:
        papers = client.search(q, user_agent=user_agent)
    except Exception as e:
        raise typer.Exit(code=2) from e

    if since_date:
        papers = [p for p in papers if p.published and p.published.date() >= since_date]

    if json_out:
        typer.echo(json.dumps([p.to_dict() for p in papers], ensure_ascii=False, indent=2))
    else:
        typer.echo(format_papers_text(papers, show_summary=summary), nl=False)


def main() -> None:
    app()


if __name__ == "__main__":
    main()

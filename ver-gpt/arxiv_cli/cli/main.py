from __future__ import annotations

import json
from typing import Optional

import typer
from rich.console import Console

from arxiv_cli.api.client import ArxivClient, ArxivQuery
from arxiv_cli.utils.formatting import (
    build_papers_table,
    format_papers_compact,
    format_papers_text,
)

app = typer.Typer(add_completion=False, help="CLI for arXiv: search, digests, watch, PDF, export")

# Subcommands
from arxiv_cli.cli.download import add_download_command
from arxiv_cli.cli.export_cmd import add_export_command
from arxiv_cli.cli.track_cmd import add_track_commands
from arxiv_cli.cli.list_cmd import add_list_command
from arxiv_cli.cli.subscribe_cmd import add_subscribe_commands
from arxiv_cli.cli.digest_cmd import add_digest_command

add_download_command(app)
add_export_command(app)
add_track_commands(app)
add_list_command(app)
add_subscribe_commands(app)
add_digest_command(app)


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
    all_fields: Optional[str] = typer.Option(None, "--all", help="Search in all fields. Builds all:<value>"),
    arxiv_id: Optional[str] = typer.Option(None, "--id", help="Exact arXiv id (e.g. 2402.05964v2). Builds id:<value>"),
    # Pagination (preferred UX)
    page: int = typer.Option(1, "--page", min=1, help="Page number (1-based)"),
    per_page: int = typer.Option(10, "--per-page", min=1, max=2000, help="Results per page"),
    # Legacy pagination (advanced)
    start: Optional[int] = typer.Option(None, "--start", help="Result offset (advanced/legacy)"),
    max_results: Optional[int] = typer.Option(None, "--max-results", help="Number of results to fetch (advanced/legacy)"),
    # Sorting (preferred UX)
    sort: str = typer.Option("relevance", "--sort", help="relevance|date (date=submittedDate)"),
    sort_by_legacy: Optional[str] = typer.Option(
        None,
        "--sort-by",
        help="Legacy: relevance|lastUpdatedDate|submittedDate (maps to --sort).",
    ),
    sort_order: str = typer.Option("descending", "--sort-order", help="ascending|descending"),
    # Date filtering
    date_from: Optional[str] = typer.Option(None, "--from", help="Published date from (YYYY-MM-DD), inclusive"),
    date_to: Optional[str] = typer.Option(None, "--to", help="Published date to (YYYY-MM-DD), inclusive"),
    # Output
    format_: str = typer.Option("table", "--format", help="table|compact|text"),
    json_out: bool = typer.Option(False, "--json", help="Output JSON"),
    summary: bool = typer.Option(False, "--summary", help="Include summary in text output"),
    user_agent: Optional[str] = typer.Option(None, "--user-agent", help="Custom User-Agent"),
) -> None:
    """Search arXiv via the official export API."""

    allowed_sort_order = {"ascending", "descending"}
    if sort_order not in allowed_sort_order:
        raise typer.BadParameter(f"sort-order must be one of: {', '.join(sorted(allowed_sort_order))}")

    sort_by_map = {
        "relevance": "relevance",
        "date": "submittedDate",
    }

    # Backward compatibility: accept old --sort-by values.
    if sort_by_legacy:
        if sort_by_legacy == "relevance":
            sort = "relevance"
        elif sort_by_legacy == "submittedDate":
            sort = "date"
        elif sort_by_legacy == "lastUpdatedDate":
            # Keep access to API capability via legacy flag.
            sort_by_map["date"] = "lastUpdatedDate"
            sort = "date"
        else:
            raise typer.BadParameter("--sort-by must be relevance|lastUpdatedDate|submittedDate")

    if sort not in sort_by_map:
        raise typer.BadParameter("--sort must be 'relevance' or 'date'")

    allowed_formats = {"table", "compact", "text"}
    if format_ not in allowed_formats:
        raise typer.BadParameter("--format must be one of: table|compact|text")

    def term(field: str, value: str) -> str:
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
            raise typer.BadParameter("Provide RAW_QUERY or at least one of: --author/--category/--title/--abstract/--all/--id")
        query = " AND ".join(built_parts)

    # Pagination: if advanced options are provided, they override page/per-page.
    if start is None:
        start_val = (page - 1) * per_page
    else:
        start_val = max(start, 0)

    if max_results is None:
        max_results_val = per_page
    else:
        max_results_val = max(1, min(max_results, 2000))

    # Date range parsing (client-side filtering)
    from datetime import date

    from_date = None
    to_date = None
    if date_from:
        try:
            from_date = date.fromisoformat(date_from)
        except ValueError as e:
            raise typer.BadParameter("--from must be YYYY-MM-DD") from e
    if date_to:
        try:
            to_date = date.fromisoformat(date_to)
        except ValueError as e:
            raise typer.BadParameter("--to must be YYYY-MM-DD") from e
    if from_date and to_date and from_date > to_date:
        raise typer.BadParameter("--from must be <= --to")

    client = ArxivClient()
    q = ArxivQuery(
        search_query=query,
        start=start_val,
        max_results=max_results_val,
        sortBy=sort_by_map[sort],
        sortOrder=sort_order,
    )

    try:
        papers = client.search(q, user_agent=user_agent)
    except Exception as e:
        raise typer.Exit(code=2) from e

    if from_date or to_date:
        filtered = []
        for p in papers:
            if not p.published:
                continue
            d = p.published.date()
            if from_date and d < from_date:
                continue
            if to_date and d > to_date:
                continue
            filtered.append(p)
        papers = filtered

    if json_out:
        typer.echo(json.dumps([p.to_dict() for p in papers], ensure_ascii=False, indent=2))
        return

    if format_ == "compact":
        typer.echo(format_papers_compact(papers), nl=False)
        return

    if format_ == "text":
        typer.echo(format_papers_text(papers, show_summary=summary), nl=False)
        return

    console = Console()
    console.print(build_papers_table(papers))


def main() -> None:
    app()


if __name__ == "__main__":
    main()

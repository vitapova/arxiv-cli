from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from arxiv_cli.api.client import ArxivClient, ArxivQuery
from arxiv_cli.api.rate_limit import RateLimiter
from arxiv_cli.storage.subscriptions import (
    Subscription,
    SubscriptionsState,
    SubscriptionsStore,
)
from arxiv_cli.utils.formatting import format_papers_text


def _build_search_query(query: str, categories: list[str]) -> str:
    query = query.strip()
    parts: list[str] = []
    if query:
        # Use all:<query> so users can pass natural text.
        q = query.replace('"', "").strip()
        if " " in q:
            q = f'"{q}"'
        parts.append(f"all:{q}")

    if categories:
        cats = " OR ".join(f"cat:{c}" for c in categories)
        parts.append(f"({cats})")

    if not parts:
        raise typer.BadParameter("Provide --query and/or --category")

    return " AND ".join(parts)


def add_subscribe_commands(app: typer.Typer) -> None:
    sub_app = typer.Typer(help="Manage saved search subscriptions")

    @sub_app.command("add")
    def add(
        query: Optional[str] = typer.Option(None, "--query", help="Search text (used as all:<query>)"),
        category: list[str] = typer.Option([], "--category", "--cat", help="Category filter (repeatable)"),
    ) -> None:
        q = query or ""
        search_q = _build_search_query(q, category)
        sub = Subscription.create(query=q, categories=category)
        SubscriptionsStore().add(sub)
        typer.echo(f"Added\t{sub.id}\t{search_q}")

    @sub_app.command("list")
    def list_cmd() -> None:
        subs = SubscriptionsStore().load()
        if not subs:
            typer.echo("No subscriptions")
            return

        table = Table(title=f"Subscriptions ({len(subs)})")
        table.add_column("id", no_wrap=True)
        table.add_column("created", no_wrap=True)
        table.add_column("query")
        table.add_column("categories")

        for s in subs:
            table.add_row(s.id, s.created_at[0:10], s.query, ",".join(s.categories))

        Console().print(table)

    @sub_app.command("remove")
    def remove(sub_id: str = typer.Argument(..., help="Subscription id")) -> None:
        ok = SubscriptionsStore().remove(sub_id)
        SubscriptionsState().remove(sub_id)
        if not ok:
            typer.echo(f"Not found\t{sub_id}")
            raise typer.Exit(code=1)
        typer.echo(f"Removed\t{sub_id}")

    @sub_app.command("check")
    def check(
        max_results: int = typer.Option(25, "--max-results", help="Results to fetch per subscription"),
        show_summary: bool = typer.Option(False, "--summary", help="Include summary in output"),
        min_interval_s: float = typer.Option(
            3.0,
            "--min-interval",
            help="Minimum seconds between API requests (rate limiting)",
        ),
    ) -> None:
        subs = SubscriptionsStore().load()
        if not subs:
            typer.echo("No subscriptions")
            return

        state = SubscriptionsState()
        client = ArxivClient(timeout_s=60.0)
        limiter = RateLimiter(min_interval_s=min_interval_s)

        total_new = 0
        for s in subs:
            search_q = _build_search_query(s.query, s.categories)
            q = ArxivQuery(
                search_query=search_q,
                start=0,
                max_results=max_results,
                sortBy="submittedDate",
                sortOrder="descending",
            )

            try:
                limiter.sleep_if_needed()
                papers = client.search(q)
            except Exception as e:
                typer.echo(f"\n# Subscription {s.id}: query={search_q}\n")
                typer.echo(f"ERR\t{type(e).__name__}: {e}")
                continue

            seen = state.get_seen(s.id)
            new_papers = [p for p in papers if p.arxiv_id not in seen]

            # Update seen: mark everything we fetched as seen.
            seen.update(p.arxiv_id for p in papers)
            state.set_seen(s.id, seen)

            if not new_papers:
                continue

            total_new += len(new_papers)
            typer.echo(f"\n# Subscription {s.id}: query={search_q}\n")
            typer.echo(format_papers_text(new_papers, show_summary=show_summary), nl=False)

        typer.echo(f"\nNew papers: {total_new}")
        # Exit code 1 when there are no new papers is useful for scripting.
        if total_new == 0:
            raise typer.Exit(code=1)

    app.add_typer(sub_app, name="subscribe")

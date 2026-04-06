from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import typer

from arxiv_cli.api.metadata import fetch_paper_by_id
from arxiv_cli.api.utils import normalize_arxiv_id
from arxiv_cli.utils.paths import safe_filename


def pdf_url(arxiv_id: str) -> str:
    return f"https://arxiv.org/pdf/{arxiv_id}.pdf"


@dataclass
class DownloadResult:
    arxiv_id: str
    ok: bool
    path: Optional[Path] = None
    error: Optional[str] = None


def _default_name(arxiv_id: str, first_author: str, year: str) -> str:
    return f"{safe_filename(arxiv_id)}_{safe_filename(first_author)}_{safe_filename(year)}.pdf"


def _download_one(arxiv_id: str, out_dir: Path, *, user_agent: Optional[str] = None) -> DownloadResult:
    out_dir.mkdir(parents=True, exist_ok=True)

    paper = fetch_paper_by_id(arxiv_id)
    if paper is None:
        return DownloadResult(arxiv_id=arxiv_id, ok=False, error="metadata not found")

    first_author = (paper.authors[0] if paper.authors else "unknown").split()[-1]
    year = str(paper.published.year) if paper.published else "unknown"

    filename = _default_name(arxiv_id, first_author, year)
    path = out_dir / filename

    url = pdf_url(arxiv_id)
    headers = {}
    if user_agent:
        headers["User-Agent"] = user_agent
    req = Request(url, headers=headers, method="GET")

    try:
        with urlopen(req, timeout=60) as resp:
            data = resp.read()
    except HTTPError as e:
        return DownloadResult(arxiv_id=arxiv_id, ok=False, error=f"HTTP {e.code}")
    except Exception as e:
        return DownloadResult(arxiv_id=arxiv_id, ok=False, error=str(e))

    # Basic sanity check
    if not data.startswith(b"%PDF"):
        # arXiv sometimes returns HTML on rate-limit/other issues
        return DownloadResult(arxiv_id=arxiv_id, ok=False, error="response is not a PDF")

    path.write_bytes(data)
    return DownloadResult(arxiv_id=arxiv_id, ok=True, path=path)


def _read_batch_ids(path: Path) -> list[str]:
    ids: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        ids.append(s)
    return ids


def run_download(
    ids: Iterable[str],
    output_dir: Path,
    *,
    user_agent: Optional[str] = None,
) -> list[DownloadResult]:
    results: list[DownloadResult] = []
    for raw in ids:
        try:
            arxiv_id = normalize_arxiv_id(raw)
        except ValueError as e:
            results.append(DownloadResult(arxiv_id=raw, ok=False, error=str(e)))
            continue

        results.append(_download_one(arxiv_id, output_dir, user_agent=user_agent))
    return results


def add_download_command(app: typer.Typer) -> None:
    @app.command("download")
    def download(
        arxiv_id: Optional[str] = typer.Argument(None, help="arXiv id (e.g. 2402.05964v2)"),
        output_dir: Path = typer.Option(Path("."), "--output-dir", "-o", help="Directory to save PDFs"),
        batch: Optional[Path] = typer.Option(
            None,
            "--batch",
            help="Path to a file with one arXiv id per line (comments with # allowed)",
        ),
        user_agent: Optional[str] = typer.Option(None, "--user-agent", help="Custom User-Agent"),
    ) -> None:
        """Download arXiv PDF by id (or batch)."""

        if not arxiv_id and not batch:
            raise typer.BadParameter("Provide ARXIV_ID or --batch")
        if arxiv_id and batch:
            raise typer.BadParameter("Provide either ARXIV_ID or --batch, not both")

        ids = [arxiv_id] if arxiv_id else _read_batch_ids(batch)  # type: ignore[arg-type]
        started = datetime.now()
        results = run_download(ids, output_dir, user_agent=user_agent)
        dt = (datetime.now() - started).total_seconds()

        ok = [r for r in results if r.ok]
        bad = [r for r in results if not r.ok]

        for r in ok:
            typer.echo(f"OK\t{r.arxiv_id}\t{r.path}")
        for r in bad:
            typer.echo(f"ERR\t{r.arxiv_id}\t{r.error}")

        typer.echo(f"\nDownloaded: {len(ok)}/{len(results)} in {dt:.1f}s")
        if bad:
            raise typer.Exit(code=1)

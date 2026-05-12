#!/usr/bin/env python3
"""
arXiv CLI Web UI

Локальный веб-интерфейс для управления библиотекой статей
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import sys

# Добавляем путь к arxiv_cli
sys.path.insert(0, str(Path(__file__).parent.parent))

from arxiv_cli.utils.library import (
    get_entries, get_stats, update_status, toggle_starred,
    add_note, get_notes, get_entry
)
from arxiv_cli.utils.authors import list_authors, get_author_stats
from arxiv_cli.commands.export import export_library

app = FastAPI(title="arXiv Assistant")

# Шаблоны
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# Static files через роут
@app.get("/static/css/style.css")
async def get_css():
    """Отдача CSS файла."""
    css_path = Path(__file__).parent / "static" / "css" / "style.css"
    return FileResponse(css_path, media_type="text/css")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Главная страница - библиотека."""
    stats = get_stats()
    entries = get_entries(sort_by='added_at', sort_order='desc')
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "stats": stats,
        "entries": entries,
        "page_title": "Библиотека"
    })


@app.get("/paper/{arxiv_id}", response_class=HTMLResponse)
async def paper_detail(request: Request, arxiv_id: str):
    """Детальная информация о статье."""
    entry = get_entry(arxiv_id)
    
    if not entry:
        return RedirectResponse(url="/")
    
    # Получаем заметки
    notes_data = get_notes(arxiv_id=arxiv_id)
    notes = notes_data[0].get('notes', []) if notes_data else []
    
    return templates.TemplateResponse("paper.html", {
        "request": request,
        "entry": entry,
        "notes": notes,
        "page_title": entry['title'][:50]
    })


@app.post("/paper/{arxiv_id}/status")
async def update_paper_status(arxiv_id: str, status: str = Form(...)):
    """Обновить статус статьи."""
    update_status(arxiv_id, status)
    return RedirectResponse(url=f"/paper/{arxiv_id}", status_code=303)


@app.post("/paper/{arxiv_id}/star")
async def toggle_paper_star(arxiv_id: str):
    """Переключить starred."""
    toggle_starred(arxiv_id)
    return RedirectResponse(url=f"/paper/{arxiv_id}", status_code=303)


@app.post("/paper/{arxiv_id}/note")
async def add_paper_note(arxiv_id: str, note_text: str = Form(...)):
    """Добавить заметку."""
    if note_text.strip():
        add_note(arxiv_id, note_text.strip())
    return RedirectResponse(url=f"/paper/{arxiv_id}", status_code=303)


@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, q: str = ""):
    """Страница поиска."""
    results = []
    
    if q:
        results = get_entries(search_query=q)
    
    return templates.TemplateResponse("search.html", {
        "request": request,
        "query": q,
        "results": results,
        "page_title": "Поиск"
    })


@app.get("/authors", response_class=HTMLResponse)
async def authors_page(request: Request):
    """Страница отслеживаемых авторов."""
    authors_data = list_authors()
    stats = get_author_stats()
    
    return templates.TemplateResponse("authors.html", {
        "request": request,
        "authors": authors_data,
        "stats": stats,
        "page_title": "Авторы"
    })


@app.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request):
    """Страница статистики."""
    stats = get_stats()
    
    # Топ категории
    top_categories = sorted(
        stats['categories'].items(),
        key=lambda x: -x[1]
    )[:10]
    
    return templates.TemplateResponse("stats.html", {
        "request": request,
        "stats": stats,
        "top_categories": top_categories,
        "page_title": "Статистика"
    })


@app.get("/export/bibtex")
async def export_bibtex_route():
    """Экспорт BibTeX."""
    from fastapi.responses import PlainTextResponse
    
    result = export_library(format='bibtex')
    
    return PlainTextResponse(
        result,
        media_type='application/x-bibtex',
        headers={'Content-Disposition': 'attachment; filename="library.bib"'}
    )


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting arXiv Assistant Web UI...")
    print("📍 Open: http://localhost:5000")
    print("⌨️  Press Ctrl+C to stop")
    print()
    
    uvicorn.run(app, host="127.0.0.1", port=5000)

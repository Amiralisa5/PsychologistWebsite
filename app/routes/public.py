import re
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.models import TherapistProfile, Article, ClinicEvent
from app.translations import get_translations
from app.templates_config import templates

router = APIRouter()


def resolve_lang(request: Request) -> str:
    lang = request.query_params.get("lang")
    if lang in ["en", "fa"]:
        return lang
    cookie_lang = request.cookies.get("site_lang")
    if cookie_lang in ["en", "fa"]:
        return cookie_lang
    return "en"


def get_public_context(db: Session, request: Request, active_page: str = "") -> dict:
    lang = resolve_lang(request)
    t = get_translations(lang)
    profile = db.query(TherapistProfile).first()
    event = db.query(ClinicEvent).filter(ClinicEvent.is_active == True).order_by(ClinicEvent.event_date.asc()).first()
    return {
        "t": t,
        "profile": profile,
        "upcoming_event": event,
        "active_page": active_page
    }


def markdown_to_html(md_text: str) -> str:
    if not md_text:
        return ""
    html = md_text
    # Escape simple angle brackets for safety if needed, or format markdown:
    # Headers
    html = re.sub(r'^### (.*?)$', r'<h3 style="margin: 1.5rem 0 0.75rem; color: #111827;">\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2 style="margin: 2rem 0 1rem; color: #111827; font-size: 1.6rem;">\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1 style="margin: 2.25rem 0 1.25rem; color: #111827;">\1</h1>', html, flags=re.MULTILINE)
    # Bold & Italic
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    # Blockquotes
    html = re.sub(r'^> (.*?)$', r'<blockquote style="border-left: 4px solid var(--primary); padding-left: 1rem; margin: 1.5rem 0; color: var(--text-muted); font-style: italic;">\1</blockquote>', html, flags=re.MULTILINE)
    # Paragraphs (split by double newline)
    paragraphs = html.split('\n\n')
    formatted = []
    for p in paragraphs:
        p_stripped = p.strip()
        if p_stripped.startswith('<h') or p_stripped.startswith('<blockquote'):
            formatted.append(p_stripped)
        elif p_stripped:
            # Check for numbered list or bullet list
            if re.match(r'^\d+\. ', p_stripped) or p_stripped.startswith('- ') or p_stripped.startswith('• '):
                lines = p_stripped.split('\n')
                list_items = "".join(f"<li style='margin-bottom: 0.5rem;'>{re.sub(r'^(\d+\. |- |• )', '', line)}</li>" for line in lines if line.strip())
                formatted.append(f"<ul style='margin: 1rem 0 1.5rem; padding-left: 1.5rem;'>{list_items}</ul>")
            else:
                formatted.append(f"<p style='margin-bottom: 1.25rem;'>{p_stripped}</p>")
    return "\n".join(formatted)


@router.get("/", response_class=HTMLResponse)
def index_view(request: Request, db: Session = Depends(get_db)):
    ctx = get_public_context(db, request, active_page="home")
    featured_articles = db.query(Article).filter(Article.published == True).order_by(Article.created_at.desc()).limit(3).all()
    ctx["articles"] = featured_articles

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=ctx
    )


@router.get("/about", response_class=HTMLResponse)
def about_view(request: Request, db: Session = Depends(get_db)):
    ctx = get_public_context(db, request, active_page="about")
    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context=ctx
    )


@router.get("/services", response_class=HTMLResponse)
def services_view(request: Request, db: Session = Depends(get_db)):
    ctx = get_public_context(db, request, active_page="services")
    return templates.TemplateResponse(
        request=request,
        name="services.html",
        context=ctx
    )


@router.get("/blog", response_class=HTMLResponse)
def blog_view(request: Request, category: str = None, db: Session = Depends(get_db)):
    ctx = get_public_context(db, request, active_page="blog")

    query = db.query(Article).filter(Article.published == True)
    if category:
        query = query.filter(Article.category == category)
    articles = query.order_by(Article.created_at.desc()).all()
    all_categories = [c[0] for c in db.query(Article.category).distinct().all() if c[0]]

    ctx["articles"] = articles
    ctx["categories"] = all_categories
    ctx["current_cat"] = category

    return templates.TemplateResponse(
        request=request,
        name="blog.html",
        context=ctx
    )


@router.get("/blog/{slug}", response_class=HTMLResponse)
def blog_detail_view(slug: str, request: Request, db: Session = Depends(get_db)):
    ctx = get_public_context(db, request, active_page="blog")
    article = db.query(Article).filter(Article.slug == slug, Article.published == True).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article.views_count = (article.views_count or 0) + 1
    db.commit()

    content = article.content_fa if ctx["t"]["lang_code"] == "fa" else article.content_en
    rendered = markdown_to_html(content)

    ctx["article"] = article
    ctx["rendered_content"] = rendered

    return templates.TemplateResponse(
        request=request,
        name="blog_detail.html",
        context=ctx
    )


@router.get("/booking", response_class=HTMLResponse)
def booking_view(request: Request, db: Session = Depends(get_db)):
    ctx = get_public_context(db, request, active_page="booking")
    return templates.TemplateResponse(
        request=request,
        name="booking.html",
        context=ctx
    )

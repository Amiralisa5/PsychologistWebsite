import os
from fastapi import APIRouter, Request, Depends, HTTPException, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AdminUser, TherapistProfile, AppointmentRequest, Article
from app.auth import verify_password, create_session_token, verify_session_token

router = APIRouter(prefix="/admin")

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def get_admin_user_from_cookie(request: Request):
    token = request.cookies.get("admin_session")
    payload = verify_session_token(token)
    return payload


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    user = get_admin_user_from_cookie(request)
    if user:
        return RedirectResponse(url="/admin", status_code=302)
    return templates.TemplateResponse(request=request, name="admin/login.html", context={"error": None})


@router.post("/login", response_class=HTMLResponse)
def login_action(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    admin = db.query(AdminUser).filter(AdminUser.username == username.strip()).first()
    if not admin or not verify_password(password, admin.password_hash, admin.salt):
        return templates.TemplateResponse(
            request=request,
            name="admin/login.html",
            context={"error": "Invalid username or password. Please try again."},
            status_code=400
        )

    # Valid login -> create session token & set cookie
    token = create_session_token(admin.username, admin.role)
    redirect = RedirectResponse(url="/admin", status_code=303)
    redirect.set_cookie(
        key="admin_session",
        value=token,
        httponly=True,
        max_age=86400 * 7,  # 7 days
        samesite="lax"
    )
    return redirect


@router.get("/logout")
def logout_action():
    redirect = RedirectResponse(url="/admin/login", status_code=302)
    redirect.delete_cookie(key="admin_session")
    return redirect


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def dashboard_view(request: Request, db: Session = Depends(get_db)):
    user = get_admin_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=302)

    total_appointments = db.query(AppointmentRequest).count()
    pending_count = db.query(AppointmentRequest).filter(AppointmentRequest.status == "Pending").count()
    confirmed_count = db.query(AppointmentRequest).filter(AppointmentRequest.status == "Confirmed").count()
    articles_count = db.query(Article).count()

    recent_appointments = db.query(AppointmentRequest).order_by(AppointmentRequest.created_at.desc()).limit(8).all()

    stats = {
        "total_appointments": total_appointments,
        "pending_count": pending_count,
        "confirmed_count": confirmed_count,
        "articles_count": articles_count
    }

    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "user": user,
            "stats": stats,
            "recent_appointments": recent_appointments,
            "active_tab": "dashboard"
        }
    )


@router.get("/appointments", response_class=HTMLResponse)
def appointments_view(request: Request, db: Session = Depends(get_db)):
    user = get_admin_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=302)

    appointments = db.query(AppointmentRequest).order_by(AppointmentRequest.created_at.desc()).all()
    
    counts = {
        "pending": sum(1 for a in appointments if a.status == "Pending"),
        "confirmed": sum(1 for a in appointments if a.status == "Confirmed"),
        "completed": sum(1 for a in appointments if a.status == "Completed"),
        "cancelled": sum(1 for a in appointments if a.status == "Cancelled"),
    }

    return templates.TemplateResponse(
        request=request,
        name="admin/appointments.html",
        context={
            "user": user,
            "appointments": appointments,
            "counts": counts,
            "active_tab": "appointments"
        }
    )


@router.get("/articles", response_class=HTMLResponse)
def articles_view(request: Request, db: Session = Depends(get_db)):
    user = get_admin_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=302)

    articles = db.query(Article).order_by(Article.created_at.desc()).all()

    return templates.TemplateResponse(
        request=request,
        name="admin/articles.html",
        context={
            "user": user,
            "articles": articles,
            "active_tab": "articles"
        }
    )


@router.post("/articles/create")
def create_article_action(
    request: Request,
    title_en: str = Form(...),
    title_fa: str = Form(...),
    slug: str = Form(...),
    category: str = Form(...),
    read_time: int = Form(5),
    featured_image: str = Form("/static/images/article-default.svg"),
    excerpt_en: str = Form(...),
    excerpt_fa: str = Form(...),
    content_en: str = Form(...),
    content_fa: str = Form(...),
    published: bool = Form(False),
    db: Session = Depends(get_db)
):
    user = get_admin_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=302)

    # Check slug collision
    existing = db.query(Article).filter(Article.slug == slug.strip()).first()
    if existing:
        slug = f"{slug.strip()}-{int(os.urandom(2).hex(), 16)}"

    new_art = Article(
        title_en=title_en.strip(),
        title_fa=title_fa.strip(),
        slug=slug.strip(),
        category=category.strip(),
        read_time=read_time,
        featured_image=featured_image.strip() or "/static/images/article-default.svg",
        excerpt_en=excerpt_en.strip(),
        excerpt_fa=excerpt_fa.strip(),
        content_en=content_en.strip(),
        content_fa=content_fa.strip(),
        published=published
    )

    db.add(new_art)
    db.commit()

    return RedirectResponse(url="/admin/articles", status_code=303)


@router.get("/profile", response_class=HTMLResponse)
def profile_view(request: Request, success: str = None, db: Session = Depends(get_db)):
    user = get_admin_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=302)

    profile = db.query(TherapistProfile).first()

    return templates.TemplateResponse(
        request=request,
        name="admin/profile.html",
        context={
            "user": user,
            "profile": profile,
            "success_msg": "Therapist profile updated successfully!" if success else None,
            "active_tab": "profile"
        }
    )


@router.post("/profile")
def update_profile_action(
    request: Request,
    name_en: str = Form(...),
    name_fa: str = Form(...),
    title_en: str = Form(...),
    title_fa: str = Form(...),
    years_experience: int = Form(12),
    photo_url: str = Form(...),
    bio_en: str = Form(...),
    bio_fa: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    telegram_url: str = Form("https://t.me/dasein_journal"),
    instagram_url: str = Form("https://instagram.com/dasein.journal"),
    address_en: str = Form(...),
    address_fa: str = Form(...),
    credentials_en: str = Form(""),
    credentials_fa: str = Form(""),
    specializations_en: str = Form(""),
    specializations_fa: str = Form(""),
    db: Session = Depends(get_db)
):
    user = get_admin_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=302)

    profile = db.query(TherapistProfile).first()
    if not profile:
        profile = TherapistProfile()
        db.add(profile)

    profile.name_en = name_en.strip()
    profile.name_fa = name_fa.strip()
    profile.title_en = title_en.strip()
    profile.title_fa = title_fa.strip()
    profile.years_experience = years_experience
    profile.photo_url = photo_url.strip()
    profile.bio_en = bio_en.strip()
    profile.bio_fa = bio_fa.strip()
    profile.email = email.strip()
    profile.phone = phone.strip()
    profile.telegram_url = telegram_url.strip()
    profile.instagram_url = instagram_url.strip()
    profile.address_en = address_en.strip()
    profile.address_fa = address_fa.strip()

    # Split lines into lists
    profile.credentials_en = [c.strip() for c in credentials_en.split("\n") if c.strip()]
    profile.credentials_fa = [c.strip() for c in credentials_fa.split("\n") if c.strip()]
    profile.specializations_en = [s.strip() for s in specializations_en.split("\n") if s.strip()]
    profile.specializations_fa = [s.strip() for s in specializations_fa.split("\n") if s.strip()]

    db.commit()

    return RedirectResponse(url="/admin/profile?success=1", status_code=303)

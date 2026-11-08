import os
from fastapi import APIRouter, Request, Depends, HTTPException, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AdminUser, TherapistProfile, AppointmentRequest, Article, SocialSettings, ClinicEvent
from app.auth import verify_password, create_session_token, verify_session_token
from app.services.social_service import (
    send_telegram_post,
    send_instagram_post,
    format_article_for_telegram,
    format_article_for_instagram
)
from app.templates_config import templates

router = APIRouter(prefix="/admin")


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
    post_telegram: bool = Form(False),
    post_instagram: bool = Form(False),
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
    db.refresh(new_art)

    # Auto-broadcast to social channels if selected
    social = db.query(SocialSettings).first()
    base_url = str(request.base_url).rstrip("/")

    if post_telegram and social and social.telegram_bot_token:
        tg_text = format_article_for_telegram(new_art, base_url)
        ok, msg_id = send_telegram_post(
            bot_token=social.telegram_bot_token,
            chat_id=social.telegram_channel_id or "@dasein_journal",
            text=tg_text
        )
        if ok:
            new_art.telegram_posted = True
            new_art.telegram_post_id = msg_id
            db.commit()

    if post_instagram and social and social.instagram_access_token and social.instagram_account_id:
        ig_caption = format_article_for_instagram(new_art, base_url)
        # Note: image_url needs to be public HTTPS; if local, this is logged/prepared
        ok, post_id = send_instagram_post(
            account_id=social.instagram_account_id,
            access_token=social.instagram_access_token,
            caption=ig_caption,
            image_url=f"{base_url}{new_art.featured_image}"
        )
        if ok:
            new_art.instagram_posted = True
            new_art.instagram_post_id = post_id
            db.commit()

    return RedirectResponse(url="/admin/articles", status_code=303)


@router.get("/social", response_class=HTMLResponse)
def social_view(request: Request, success: str = None, error: str = None, db: Session = Depends(get_db)):
    user = get_admin_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=302)

    social = db.query(SocialSettings).first()
    if not social:
        social = SocialSettings()
        db.add(social)
        db.commit()

    articles = db.query(Article).order_by(Article.created_at.desc()).all()

    return templates.TemplateResponse(
        request=request,
        name="admin/social.html",
        context={
            "user": user,
            "social": social,
            "articles": articles,
            "success_msg": "Social channels settings updated successfully!" if success else None,
            "error_msg": error,
            "active_tab": "social"
        }
    )


@router.post("/social")
def update_social_action(
    request: Request,
    section: str = Form("telegram"),
    telegram_enabled: bool = Form(False),
    telegram_channel_id: str = Form("@dasein_journal"),
    telegram_bot_token: str = Form(""),
    telegram_auto_publish: bool = Form(False),
    instagram_enabled: bool = Form(False),
    instagram_page_handle: str = Form("dasein.journal"),
    instagram_account_id: str = Form(""),
    instagram_access_token: str = Form(""),
    instagram_auto_publish: bool = Form(False),
    db: Session = Depends(get_db)
):
    user = get_admin_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=302)

    social = db.query(SocialSettings).first()
    if not social:
        social = SocialSettings()
        db.add(social)

    if section == "telegram":
        social.telegram_enabled = telegram_enabled
        social.telegram_channel_id = telegram_channel_id.strip()
        social.telegram_bot_token = telegram_bot_token.strip()
        social.telegram_auto_publish = telegram_auto_publish
    elif section == "instagram":
        social.instagram_enabled = instagram_enabled
        social.instagram_page_handle = instagram_page_handle.strip()
        social.instagram_account_id = instagram_account_id.strip()
        social.instagram_access_token = instagram_access_token.strip()
        social.instagram_auto_publish = instagram_auto_publish

    db.commit()
    return RedirectResponse(url="/admin/social?success=1", status_code=303)


@router.post("/social/test-telegram")
async def test_telegram_action(request: Request):
    user = get_admin_user_from_cookie(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    body = await request.json()
    bot_token = body.get("bot_token", "")
    channel_id = body.get("channel_id", "@dasein_journal")

    test_message = (
        "🌿 <b>تست اتصال ژورنال دازاین | Dasein Journal</b>\n\n"
        "این یک پیام آزمایشی برای تایید اتصال خودکار پنل مدیریت به کانال تلگرام است.\n"
        "🆔 @dasein_journal"
    )

    ok, res = send_telegram_post(bot_token=bot_token, chat_id=channel_id, text=test_message)
    if ok:
        return {"success": True, "message_id": res}
    else:
        raise HTTPException(status_code=400, detail=res)


@router.post("/articles/{id}/publish-telegram")
def publish_article_to_telegram(
    id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_admin_user_from_cookie(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    article = db.query(Article).filter(Article.id == id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    social = db.query(SocialSettings).first()
    if not social or not social.telegram_bot_token:
        raise HTTPException(status_code=400, detail="Telegram Bot Token is not configured. Please enter your Bot Token in the 'Social Channels' tab.")

    base_url = str(request.base_url).rstrip("/")
    tg_text = format_article_for_telegram(article, base_url)

    ok, res = send_telegram_post(
        bot_token=social.telegram_bot_token,
        chat_id=social.telegram_channel_id or "@dasein_journal",
        text=tg_text
    )

    if ok:
        article.telegram_posted = True
        article.telegram_post_id = res
        db.commit()
        return {"success": True, "message_id": res}
    else:
        raise HTTPException(status_code=400, detail=f"Telegram Error: {res}")

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
    default_meet_link: str = Form("https://meet.google.com/das-ein-meet"),
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
    profile.default_meet_link = default_meet_link.strip() if default_meet_link else "https://meet.google.com/das-ein-meet"

    # Split lines into lists
    profile.credentials_en = [c.strip() for c in credentials_en.split("\n") if c.strip()]
    profile.credentials_fa = [c.strip() for c in credentials_fa.split("\n") if c.strip()]
    profile.specializations_en = [s.strip() for s in specializations_en.split("\n") if s.strip()]
    profile.specializations_fa = [s.strip() for s in specializations_fa.split("\n") if s.strip()]

    db.commit()

    return RedirectResponse(url="/admin/profile?success=1", status_code=303)

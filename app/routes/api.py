import re
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AppointmentRequest, Article, TherapistProfile, ClinicEvent
from app.auth import verify_session_token
from app.translations import get_translations
from app.utils.persian_calendar import (
    to_english_digits,
    format_jalali_date,
    format_jalali_short,
    gregorian_to_jalali,
    jalali_to_gregorian,
    generate_google_calendar_url
)

router = APIRouter(prefix="/api")


class BookingRequestSchema(BaseModel):
    client_name: str
    email: str
    phone: str
    service_type: Optional[str] = "Individual Therapy"
    session_format: Optional[str] = "Online"
    preferred_date: Optional[str] = None
    preferred_date_shamsi: Optional[str] = None
    preferred_time: Optional[str] = None
    notes: Optional[str] = None
    language_used: Optional[str] = "en"


class UpdateAppointmentStatusSchema(BaseModel):
    status: str


class UpdateAppointmentDetailsSchema(BaseModel):
    status: str
    therapist_notes: Optional[str] = ""
    meet_link: Optional[str] = None


def get_current_admin(request: Request):
    token = request.cookies.get("admin_session")
    payload = verify_session_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Unauthorized admin session")
    return payload


@router.post("/appointments/book")
@router.post("/appointments")
def book_consultation(data: BookingRequestSchema, db: Session = Depends(get_db)):
    if not data.client_name.strip() or not data.phone.strip():
        raise HTTPException(status_code=400, detail="Name and phone number are required.")

    profile = db.query(TherapistProfile).first()
    default_meet = profile.default_meet_link if (profile and profile.default_meet_link) else "https://meet.google.com/das-ein-meet"

    # Handle dates in both Gregorian and Shamsi
    pref_gregorian = (data.preferred_date or "").strip()
    pref_shamsi = (data.preferred_date_shamsi or "").strip()

    # If shamsi date provided without gregorian or vice-versa, cross-convert
    if pref_shamsi and not pref_gregorian:
        try:
            clean_shamsi = to_english_digits(pref_shamsi)
            parts = clean_shamsi.replace("-", "/").split("/")
            if len(parts) == 3:
                jy, jm, jd = int(parts[0]), int(parts[1]), int(parts[2])
                greg_d = jalali_to_gregorian(jy, jm, jd)
                pref_gregorian = greg_d.strftime("%Y-%m-%d")
        except Exception:
            pass

    if pref_gregorian and not pref_shamsi:
        try:
            pref_shamsi = format_jalali_date(pref_gregorian)
        except Exception:
            pass

    new_request = AppointmentRequest(
        client_name=data.client_name.strip(),
        email=data.email.strip(),
        phone=data.phone.strip(),
        service_type=data.service_type,
        session_format=data.session_format,
        preferred_date=pref_gregorian,
        preferred_date_shamsi=pref_shamsi,
        preferred_time=data.preferred_time,
        meet_link=default_meet,
        notes=data.notes,
        status="Pending",
        language_used=data.language_used if data.language_used in ["en", "fa"] else "en"
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    t = get_translations(data.language_used)

    cal_url = new_request.google_calendar_link

    return {
        "success": True,
        "id": new_request.id,
        "title": t["form_success_title"],
        "message": t["form_success_message"],
        "session_format": new_request.session_format,
        "preferred_date": new_request.preferred_date,
        "preferred_date_shamsi": new_request.display_shamsi_date,
        "preferred_time": new_request.preferred_time,
        "meet_link": new_request.meet_link,
        "google_calendar_url": cal_url,
        "client_name": new_request.client_name,
        "service_type": new_request.service_type
    }


@router.patch("/admin/appointments/{id}/status")
def update_appointment_status(
    id: int,
    data: UpdateAppointmentStatusSchema,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    appt = db.query(AppointmentRequest).filter(AppointmentRequest.id == id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment request not found")

    valid_statuses = ["Pending", "Confirmed", "Completed", "Cancelled"]
    if data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")

    appt.status = data.status
    db.commit()

    return {"success": True, "id": id, "status": appt.status}


@router.patch("/admin/appointments/{id}")
def update_appointment_details(
    id: int,
    data: UpdateAppointmentDetailsSchema,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    appt = db.query(AppointmentRequest).filter(AppointmentRequest.id == id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment request not found")

    appt.status = data.status
    appt.therapist_notes = data.therapist_notes
    if data.meet_link:
        appt.meet_link = data.meet_link.strip()
    db.commit()

    return {
        "success": True,
        "id": id,
        "status": appt.status,
        "meet_link": appt.meet_link,
        "google_calendar_url": appt.google_calendar_link
    }


@router.get("/events")
def list_events(db: Session = Depends(get_db)):
    events = db.query(ClinicEvent).filter(ClinicEvent.is_active == True).order_by(ClinicEvent.event_date.asc()).all()
    return [
        {
            "id": e.id,
            "title_en": e.title_en,
            "title_fa": e.title_fa,
            "description_en": e.description_en,
            "description_fa": e.description_fa,
            "event_date": e.event_date,
            "event_date_shamsi": e.display_shamsi_date,
            "event_time": e.event_time,
            "event_format": e.event_format,
            "meet_link": e.meet_link,
            "location_en": e.location_en,
            "location_fa": e.location_fa,
            "google_calendar_url": e.google_calendar_link
        }
        for e in events
    ]


@router.get("/admin/notifications")
def get_admin_notifications(admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    pending = db.query(AppointmentRequest).filter(AppointmentRequest.status == "Pending").order_by(AppointmentRequest.created_at.desc()).all()
    confirmed = db.query(AppointmentRequest).filter(AppointmentRequest.status == "Confirmed").order_by(AppointmentRequest.created_at.desc()).limit(5).all()
    events = db.query(ClinicEvent).filter(ClinicEvent.is_active == True).order_by(ClinicEvent.event_date.asc()).limit(3).all()

    return {
        "pending_count": len(pending),
        "pending_items": [
            {
                "id": p.id,
                "client_name": p.client_name,
                "phone": p.phone,
                "service_type": p.service_type,
                "session_format": p.session_format,
                "date": p.preferred_date,
                "date_shamsi": p.display_shamsi_date,
                "time": p.preferred_time,
                "meet_link": p.meet_link,
                "google_calendar_url": p.google_calendar_link
            }
            for p in pending
        ],
        "confirmed_items": [
            {
                "id": c.id,
                "client_name": c.client_name,
                "session_format": c.session_format,
                "date": c.preferred_date,
                "date_shamsi": c.display_shamsi_date,
                "time": c.preferred_time,
                "meet_link": c.meet_link,
                "google_calendar_url": c.google_calendar_link
            }
            for c in confirmed
        ],
        "events": [
            {
                "id": e.id,
                "title_fa": e.title_fa,
                "title_en": e.title_en,
                "date_shamsi": e.display_shamsi_date,
                "meet_link": e.meet_link,
                "google_calendar_url": e.google_calendar_link
            }
            for e in events
        ]
    }


@router.delete("/admin/articles/{id}")
def delete_article(
    id: int,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    article = db.query(Article).filter(Article.id == id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    db.delete(article)
    db.commit()

    return {"success": True, "id": id}


@router.get("/articles")
def list_articles(db: Session = Depends(get_db)):
    articles = db.query(Article).filter(Article.published == True).order_by(Article.created_at.desc()).all()
    return [
        {
            "id": a.id,
            "slug": a.slug,
            "title_en": a.title_en,
            "title_fa": a.title_fa,
            "excerpt_en": a.excerpt_en,
            "excerpt_fa": a.excerpt_fa,
            "category": a.category,
            "read_time": a.read_time,
            "featured_image": a.featured_image,
            "published": a.published,
            "telegram_posted": a.telegram_posted,
            "instagram_posted": a.instagram_posted,
            "created_at": a.created_at.isoformat() if a.created_at else None
        }
        for a in articles
    ]

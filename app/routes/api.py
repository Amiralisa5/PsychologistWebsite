import re
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AppointmentRequest, Article
from app.auth import verify_session_token
from app.translations import get_translations

router = APIRouter(prefix="/api")


class BookingRequestSchema(BaseModel):
    client_name: str
    email: str
    phone: str
    service_type: Optional[str] = "Individual Therapy"
    session_format: Optional[str] = "Online"
    preferred_date: Optional[str] = None
    preferred_time: Optional[str] = None
    notes: Optional[str] = None
    language_used: Optional[str] = "en"


class UpdateAppointmentStatusSchema(BaseModel):
    status: str


class UpdateAppointmentDetailsSchema(BaseModel):
    status: str
    therapist_notes: Optional[str] = ""


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

    new_request = AppointmentRequest(
        client_name=data.client_name.strip(),
        email=data.email.strip(),
        phone=data.phone.strip(),
        service_type=data.service_type,
        session_format=data.session_format,
        preferred_date=data.preferred_date,
        preferred_time=data.preferred_time,
        notes=data.notes,
        status="Pending",
        language_used=data.language_used if data.language_used in ["en", "fa"] else "en"
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    t = get_translations(data.language_used)

    return {
        "success": True,
        "id": new_request.id,
        "title": t["form_success_title"],
        "message": t["form_success_message"]
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
    db.commit()

    return {"success": True, "id": id, "status": appt.status}


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

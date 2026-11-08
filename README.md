# 🌿 Dasein Journal — Dr. Hassan Agha Nasiri
### ژورنال دازاین | وب‌سایت تخصصی روان‌درمانی اگزیستانسیال و بالینی دکتر حسن آقانصیری

A modern, compassionate, and production-ready **bilingual (English & Persian / فارسی)** web application designed for **Dasein Journal** and the clinical psychology practice of **Dr. Hassan Agha Nasiri (دکتر حسن آقانصیری)**.

---

## 📱 Contact & Community

- **Phone / WhatsApp**: [+98 912 519 7973](tel:+989125197973)
- **Telegram Group**: [@dasein_journal](https://t.me/dasein_journal)
- **Instagram Page**: [@dasein.journal](https://instagram.com/dasein.journal)
- **Email**: contact@daseinjournal.com

---

## ✨ Highlights & Features

### 1. 🌐 Public Bilingual Website (LTR & RTL)
- **Instant Language Toggle**: Seamlessly switch between **English (LTR)** and **فارسی (RTL)** with persistent language preferences.
- **Hero & Trust Section**: Warm, calming aesthetic with clinical experience metrics (12+ years, 4,800+ hours, certified confidentiality).
- **Therapist Profile & About**: Comprehensive background for **Dr. Hassan Agha Nasiri** (دکتر حسن آقانصیری), clinical credentials, degrees, and existential therapeutic philosophy.
- **Specialties & Clinical Approaches**: Dedicated showcases for:
  - Anxiety, Panic & Existential Dread (CBT & Somatics)
  - Depression & Emotional Regulation
  - Couples & Relationship Healing (Emotionally Focused Therapy - EFT)
  - Trauma & EMDR / Grief Processing
  - Life Transitions & Identity Authenticity
  - Mindfulness & Existential Psychotherapy
- **Mental Health Blog & Resources**: Clinical guides and existential reflections with category filtering, reading time estimates, and full markdown rendering.
- **Interactive Consultation Booking**: AJAX consultation scheduling with instant validation, date/time preference, session format (Online / In-Person), and bilingual feedback.
- **Emergency Crisis Guidance**: Direct hotline numbers (123 / 1480 in Iran, 988 / 911 international).

### 2. 🔐 Therapist / Admin Management Portal (`/admin`)
- **Secure Authentication**: Session-based auth with cryptographic HMAC signatures and PBKDF2 password hashing.
- **Dashboard Overview**: Real-time metrics for pending inquiries, confirmed sessions, total inquiries, and articles.
- **Consultation Request Manager**:
  - Filter by status: *All*, *Pending*, *Confirmed*, *Completed*, *Cancelled*.
  - Live client search by name, email, or phone.
  - Quick status dropdown selector.
  - Interactive Modal to review client intake notes and record **private internal therapist notes**.
- **Article & Content Publishing**:
  - Create and publish new articles with separate English and Persian titles, excerpts, and content.
  - Toggle published/draft status.
  - Delete articles with instant confirmation.
- **Live Therapist Profile Editor**:
  - Update personal names, credentials, clinical bio, phone, email, telegram, instagram, and addresses in both languages without changing code.

---

## 🛠️ Tech Stack

- **Backend**: Python 3, [FastAPI](https://fastapi.tiangolo.com/), Uvicorn, Pydantic, SQLAlchemy
- **Database**: SQLite (`psychologist.db`), automatically seeded with rich bilingual data on first launch
- **Frontend / Templating**: Jinja2, Responsive CSS3 with custom variables, Typography (DM Sans, Playfair Display, Vazirmatn)
- **Security**: PBKDF2 password hashing with salt, HMAC-signed session cookies

---

## 🚀 Quick Start Guide

### 1. Activate the Virtual Environment
```bash
cd /Users/amirrili/Documents/GitHub/PsychologistWebSite
source .venv/bin/activate
```

*(If setting up on a new machine, create the venv and install dependencies via `pip install -r requirements.txt`)*

### 2. Run the Application
```bash
python run.py
```
Or directly with Uvicorn:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Open in Browser
- **Public Website (English)**: [http://127.0.0.1:8000/?lang=en](http://127.0.0.1:8000/?lang=en)
- **Public Website (فارسی)**: [http://127.0.0.1:8000/?lang=fa](http://127.0.0.1:8000/?lang=fa)
- **Therapist Admin Portal**: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

> **Default Admin Credentials**:
> - **Username**: `admin`
> - **Password**: `psychologist2026`

---

## 📂 Project Architecture

```
PsychologistWebSite/
├── app/
│   ├── auth.py              # PBKDF2 hashing, HMAC session tokens
│   ├── database.py          # SQLAlchemy SQLite connection & session
│   ├── main.py              # FastAPI app initialization, routes mounting
│   ├── models.py            # TherapistProfile, AppointmentRequest, Article, AdminUser
│   ├── seed_data.py         # Database seeder with bilingual articles & profile
│   ├── translations.py      # English & Farsi translation dictionaries
│   ├── routes/
│   │   ├── admin.py         # Admin portal dashboard, appointments, articles, profile
│   │   ├── api.py           # REST API for booking consultation & admin actions
│   │   └── public.py        # Public views: Home, About, Services, Blog, Booking
│   ├── static/
│   │   ├── css/style.css    # Responsive design with full LTR & RTL support
│   │   ├── js/main.js       # Client language switcher, AJAX booking form
│   │   ├── js/admin.js      # Admin search, filters, modals, status changes
│   │   └── images/          # Professional SVG therapist & article illustrations
│   └── templates/
│       ├── base.html        # Public layout with navigation & footer
│       ├── index.html       # Landing page (Hero, Welcome, Specialties, Approach)
│       ├── about.html       # Dr. Fathi's credentials, bio, and philosophy
│       ├── services.html    # Clinical specialties catalog & interactive FAQ
│       ├── blog.html        # Mental health articles with category filter
│       ├── blog_detail.html # Article reading view (bilingual)
│       ├── booking.html     # Dedicated consultation booking form
│       └── admin/           # Therapist management portal templates
├── requirements.txt         # Pinned Python dependencies
├── run.py                   # One-click startup script
└── README.md
```

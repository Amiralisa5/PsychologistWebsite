import datetime
import json
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.database import Base


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    salt = Column(String(64), nullable=False)
    role = Column(String(50), default="admin")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class TherapistProfile(Base):
    __tablename__ = "therapist_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name_en = Column(String(200), default="Dr. Hassan Agha Nasiri")
    name_fa = Column(String(200), default="دکتر حسن آقانصیری")
    title_en = Column(String(200), default="Licensed Clinical Psychologist & Psychotherapist")
    title_fa = Column(String(200), default="روانشناس بالینی و روان‌درمانگر رسمی")
    
    bio_en = Column(Text, nullable=False)
    bio_fa = Column(Text, nullable=False)
    
    # JSON-encoded lists
    specializations_en_json = Column(Text, default="[]")
    specializations_fa_json = Column(Text, default="[]")
    credentials_en_json = Column(Text, default="[]")
    credentials_fa_json = Column(Text, default="[]")
    
    years_experience = Column(Integer, default=12)
    email = Column(String(150), default="contact@daseinjournal.com")
    phone = Column(String(50), default="+989125197973")
    telegram_url = Column(String(200), default="https://t.me/dasein_journal")
    instagram_url = Column(String(200), default="https://instagram.com/dasein.journal")
    address_en = Column(String(300), default="Suite 402, North Kargar Ave, Tehran / Online Worldwide")
    address_fa = Column(String(300), default="تهران، خیابان کارگر شمالی، ساختمان پزشکان، واحد ۴۰۲ / جلسات آنلاین بین‌المللی")
    photo_url = Column(String(300), default="/static/images/dr-hassan-aghanasiri.jpg")
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    @property
    def specializations_en(self):
        try:
            return json.loads(self.specializations_en_json or "[]")
        except Exception:
            return []

    @specializations_en.setter
    def specializations_en(self, val):
        self.specializations_en_json = json.dumps(val, ensure_ascii=False)

    @property
    def specializations_fa(self):
        try:
            return json.loads(self.specializations_fa_json or "[]")
        except Exception:
            return []

    @specializations_fa.setter
    def specializations_fa(self, val):
        self.specializations_fa_json = json.dumps(val, ensure_ascii=False)

    @property
    def credentials_en(self):
        try:
            return json.loads(self.credentials_en_json or "[]")
        except Exception:
            return []

    @credentials_en.setter
    def credentials_en(self, val):
        self.credentials_en_json = json.dumps(val, ensure_ascii=False)

    @property
    def credentials_fa(self):
        try:
            return json.loads(self.credentials_fa_json or "[]")
        except Exception:
            return []

    @credentials_fa.setter
    def credentials_fa(self, val):
        self.credentials_fa_json = json.dumps(val, ensure_ascii=False)


class AppointmentRequest(Base):
    __tablename__ = "appointment_requests"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    phone = Column(String(50), nullable=False)
    preferred_date = Column(String(50), nullable=True)
    preferred_time = Column(String(50), nullable=True)
    service_type = Column(String(100), default="Individual Therapy")
    session_format = Column(String(50), default="Online")  # Online or In-Person
    notes = Column(Text, nullable=True)
    status = Column(String(50), default="Pending")  # Pending, Confirmed, Completed, Cancelled
    therapist_notes = Column(Text, nullable=True)
    language_used = Column(String(10), default="en")  # en or fa
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(150), unique=True, index=True, nullable=False)
    title_en = Column(String(250), nullable=False)
    title_fa = Column(String(250), nullable=False)
    excerpt_en = Column(Text, nullable=False)
    excerpt_fa = Column(Text, nullable=False)
    content_en = Column(Text, nullable=False)
    content_fa = Column(Text, nullable=False)
    category = Column(String(100), default="Mental Health")
    read_time = Column(Integer, default=5)
    featured_image = Column(String(300), default="/static/images/article-default.svg")
    published = Column(Boolean, default=True)
    views_count = Column(Integer, default=0)
    
    # Social channels tracking
    telegram_posted = Column(Boolean, default=False)
    telegram_post_id = Column(String(100), nullable=True)
    instagram_posted = Column(Boolean, default=False)
    instagram_post_id = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class SocialSettings(Base):
    __tablename__ = "social_settings"

    id = Column(Integer, primary_key=True, index=True)
    
    # Telegram Bot Settings
    telegram_enabled = Column(Boolean, default=False)
    telegram_bot_token = Column(String(200), default="")
    telegram_channel_id = Column(String(100), default="@dasein_journal")
    telegram_auto_publish = Column(Boolean, default=True)

    # Instagram Graph API Settings
    instagram_enabled = Column(Boolean, default=False)
    instagram_account_id = Column(String(100), default="")
    instagram_access_token = Column(Text, default="")
    instagram_page_handle = Column(String(100), default="dasein.journal")
    instagram_auto_publish = Column(Boolean, default=False)

    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


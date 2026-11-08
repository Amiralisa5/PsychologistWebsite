import datetime
import urllib.parse
from typing import Optional, Tuple
import jdatetime

jdatetime.set_locale("fa_IR")

PERSIAN_MONTHS = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
]

PERSIAN_DIGITS_MAP = {
    "0": "۰", "1": "۱", "2": "۲", "3": "۳", "4": "۴",
    "5": "۵", "6": "۶", "7": "۷", "8": "۸", "9": "۹"
}

ENGLISH_DIGITS_MAP = {v: k for k, v in PERSIAN_DIGITS_MAP.items()}
# Also handle Arabic digits
ARABIC_DIGITS_MAP = {
    "٠": "0", "١": "1", "٢": "2", "٣": "3", "٤": "4",
    "٥": "5", "٦": "6", "٧": "7", "٨": "8", "٩": "9"
}


def to_persian_digits(val: any) -> str:
    """Converts standard ASCII digits to Persian digits."""
    if val is None:
        return ""
    text = str(val)
    return "".join(PERSIAN_DIGITS_MAP.get(ch, ch) for ch in text)


def to_english_digits(val: any) -> str:
    """Converts Persian and Arabic digits to standard ASCII digits."""
    if val is None:
        return ""
    text = str(val)
    res = []
    for ch in text:
        if ch in ENGLISH_DIGITS_MAP:
            res.append(ENGLISH_DIGITS_MAP[ch])
        elif ch in ARABIC_DIGITS_MAP:
            res.append(ARABIC_DIGITS_MAP[ch])
        else:
            res.append(ch)
    return "".join(res)


def gregorian_to_jalali(*args) -> Tuple[int, int, int]:
    """
    Takes either:
      - (year: int, month: int, day: int)
      - or (dt_or_str: datetime.date | datetime.datetime | 'YYYY-MM-DD' | 'YYYY/MM/DD')
    and returns (year, month, day) in Jalali calendar.
    """
    if len(args) == 3:
        try:
            y, m, d = int(args[0]), int(args[1]), int(args[2])
            jd = jdatetime.date.fromgregorian(year=y, month=m, day=d)
            return jd.year, jd.month, jd.day
        except Exception:
            today = datetime.date.today()
            jd = jdatetime.date.fromgregorian(date=today)
            return jd.year, jd.month, jd.day

    dt_or_str = args[0] if len(args) == 1 else None

    if not dt_or_str:
        today = datetime.date.today()
        jd = jdatetime.date.fromgregorian(date=today)
        return jd.year, jd.month, jd.day

    if isinstance(dt_or_str, (datetime.datetime, datetime.date)):
        d = dt_or_str.date() if isinstance(dt_or_str, datetime.datetime) else dt_or_str
        jd = jdatetime.date.fromgregorian(date=d)
        return jd.year, jd.month, jd.day

    clean_str = to_english_digits(str(dt_or_str).strip())
    # Try parsing YYYY-MM-DD
    try:
        parts = clean_str.split("-")
        if len(parts) == 3:
            y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
            jd = jdatetime.date.fromgregorian(year=y, month=m, day=d)
            return jd.year, jd.month, jd.day
    except Exception:
        pass

    # Try parsing YYYY/MM/DD
    try:
        parts = clean_str.split("/")
        if len(parts) == 3:
            # If year > 1700 it is gregorian
            y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
            if y > 1700:
                jd = jdatetime.date.fromgregorian(year=y, month=m, day=d)
                return jd.year, jd.month, jd.day
            else:
                return y, m, d
    except Exception:
        pass

    today = datetime.date.today()
    jd = jdatetime.date.fromgregorian(date=today)
    return jd.year, jd.month, jd.day


def format_jalali_date(dt_or_str: any, persian_digits: bool = True) -> str:
    """Formats a date as '۱۷ آبان ۱۴۰۵' or '1405/08/17'."""
    try:
        jy, jm, jd = gregorian_to_jalali(dt_or_str)
        month_name = PERSIAN_MONTHS[jm - 1] if 1 <= jm <= 12 else str(jm)
        res = f"{jd} {month_name} {jy}"
        return to_persian_digits(res) if persian_digits else res
    except Exception:
        return str(dt_or_str) if dt_or_str else ""


def format_jalali_short(dt_or_str: any, persian_digits: bool = True) -> str:
    """Formats date as '۱۴۰۵/۰۸/۱۷'."""
    try:
        jy, jm, jd = gregorian_to_jalali(dt_or_str)
        res = f"{jy}/{jm:02d}/{jd:02d}"
        return to_persian_digits(res) if persian_digits else res
    except Exception:
        return str(dt_or_str) if dt_or_str else ""


def jalali_to_gregorian(jy: int, jm: int, jd: int) -> datetime.date:
    """Converts Jalali year, month, day to Gregorian datetime.date."""
    j_date = jdatetime.date(jy, jm, jd)
    return j_date.togregorian()


def generate_google_calendar_url(
    title: str,
    date_str: Optional[str] = None,
    time_slot: Optional[str] = None,
    service_type: Optional[str] = "Clinical Psychology & Psychotherapy",
    client_name: Optional[str] = "",
    meet_link: Optional[str] = "https://meet.google.com/das-ein-meet",
    session_format: Optional[str] = "Online",
    notes: Optional[str] = None
) -> str:
    """
    Generates a 1-click Google Calendar TEMPLATE URL with Meet details prefilled.
    Format: https://calendar.google.com/calendar/render?action=TEMPLATE&text=...&dates=...&details=...&location=...
    """
    clean_date = to_english_digits(date_str or "")
    start_dt = None

    # Parse date
    if clean_date:
        try:
            if "-" in clean_date:
                parts = clean_date.split("-")
                start_dt = datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
            elif "/" in clean_date:
                parts = clean_date.split("/")
                y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
                if y < 1700:
                    start_dt = jalali_to_gregorian(y, m, d)
                else:
                    start_dt = datetime.date(y, m, d)
        except Exception:
            start_dt = None

    if not start_dt:
        start_dt = datetime.date.today() + datetime.timedelta(days=1)

    # Determine hour based on time_slot
    slot_lower = (time_slot or "").lower()
    if "morning" in slot_lower or "صبح" in slot_lower or "9" in slot_lower:
        hour_start = 10
    elif "afternoon" in slot_lower or "عصر" in slot_lower or "14" in slot_lower or "ظهر" in slot_lower:
        hour_start = 15
    elif "evening" in slot_lower or "شب" in slot_lower or "18" in slot_lower:
        hour_start = 18
    else:
        hour_start = 11

    start_datetime = datetime.datetime.combine(start_dt, datetime.time(hour=hour_start, minute=0))
    end_datetime = start_datetime + datetime.timedelta(minutes=50)

    # Convert to UTC format: YYYYMMDDTHHMMSSZ (Assuming Tehran time UTC+3:30)
    # Tehran is UTC+3:30
    tz_offset = datetime.timedelta(hours=3, minutes=30)
    utc_start = start_datetime - tz_offset
    utc_end = end_datetime - tz_offset

    dates_param = f"{utc_start.strftime('%Y%m%dT%H%M%SZ')}/{utc_end.strftime('%Y%m%dT%H%M%SZ')}"

    # Build description details
    desc_lines = [
        f"جلسه روان‌درمانی و مشاوره تخصصی — دکتر حسن آقانصیری | ژورنال دازاین",
        f"Psychotherapy Consultation — Dr. Hassan Agha Nasiri (Dasein Journal)",
        f"--------------------------------------------------",
        f"📌 Service / خدمت: {service_type}",
        f"👤 Client / مراجع: {client_name or 'Client'}",
        f"🌐 Format / نوع جلسه: {session_format}",
    ]

    if session_format == "Online" and meet_link:
        desc_lines.extend([
            f"📹 Google Meet Link / لینک اتاق آنلاین:",
            f"{meet_link}",
            f"(لطفاً ۵ دقیقه پیش از شروع جلسه روی لینک بالا کلیک فرمایید)",
        ])
    else:
        desc_lines.append("📍 Address / نشانی حضوری: تهران، کارگر شمالی، ساختمان پزشکان، واحد ۴۰۲")

    desc_lines.extend([
        f"📞 Phone / تلفن مطب: +989125197973",
        f"✈️ Telegram: @dasein_journal (https://t.me/dasein_journal)",
        f"📸 Instagram: dasein.journal (https://instagram.com/dasein.journal)",
    ])

    if notes:
        desc_lines.append(f"📝 Notes / توضیحات: {notes}")

    details_text = "\n".join(desc_lines)
    location_text = meet_link if (session_format == "Online" and meet_link) else "Suite 402, North Kargar Ave, Tehran"

    params = {
        "action": "TEMPLATE",
        "text": title,
        "dates": dates_param,
        "details": details_text,
        "location": location_text
    }

    return "https://calendar.google.com/calendar/render?" + urllib.parse.urlencode(params)

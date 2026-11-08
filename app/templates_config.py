import os
from fastapi.templating import Jinja2Templates
from app.utils.persian_calendar import (
    to_persian_digits,
    to_english_digits,
    format_jalali_date,
    format_jalali_short,
    generate_google_calendar_url,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Register Jinja2 custom filters
templates.env.filters["shamsi_date"] = format_jalali_date
templates.env.filters["shamsi_short"] = format_jalali_short
templates.env.filters["persian_digits"] = to_persian_digits
templates.env.filters["english_digits"] = to_english_digits

# Register Jinja2 global functions
templates.env.globals["google_cal_url"] = generate_google_calendar_url
templates.env.globals["to_persian_digits"] = to_persian_digits

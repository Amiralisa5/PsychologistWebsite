import asyncio
import json
import unittest
import urllib.parse
from app.main import app
from app.utils.persian_calendar import (
    format_jalali_date,
    format_jalali_short,
    gregorian_to_jalali,
    jalali_to_gregorian,
    generate_google_calendar_url,
    to_persian_digits
)


async def asgi_request(method="GET", path="/", query="", headers=None, body=b""):
    if "?" in path and not query:
        path, query = path.split("?", 1)
    if headers is None:
        headers = []
    response_headers = {}
    response_status = 200
    body_chunks = []

    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": method,
        "path": path,
        "raw_path": path.encode(),
        "query_string": query.encode() if isinstance(query, str) else query,
        "headers": [(k.lower().encode(), v.encode()) for k, v in headers],
        "server": ("127.0.0.1", 8000),
        "client": ("127.0.0.1", 50000),
    }

    body_sent = False

    async def receive():
        nonlocal body_sent
        if not body_sent:
            body_sent = True
            return {"type": "http.request", "body": body, "more_body": False}
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        nonlocal response_status, response_headers
        if message["type"] == "http.response.start":
            response_status = message["status"]
            for k, v in message.get("headers", []):
                response_headers[k.decode().lower()] = v.decode()
        elif message["type"] == "http.response.body":
            body_chunks.append(message.get("body", b""))

    await app(scope, receive, send)
    return response_status, response_headers, b"".join(body_chunks).decode("utf-8", errors="replace")


def request(method="GET", path="/", query="", headers=None, body=b""):
    return asyncio.run(asgi_request(method, path, query, headers, body))


class DaseinJournalIntegrationTests(unittest.TestCase):
    def test_public_homepage(self):
        # English
        status, hdrs, text = request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn("Dasein Journal", text)
        self.assertIn("Dr. Hassan Agha Nasiri", text)
        self.assertIn("+989125197973", text)
        self.assertIn("/static/images/logo.jpg", text)
        self.assertIn("/static/images/dr-hassan-aghanasiri.jpg", text)
        self.assertIn("t.me/dasein_journal", text)
        self.assertIn("instagram.com/dasein.journal", text)

        # Persian
        status_fa, hdrs_fa, text_fa = request("GET", "/", query="lang=fa")
        self.assertEqual(status_fa, 200)
        self.assertIn("ژورنال دازاین", text_fa)
        self.assertIn("دکتر حسن آقانصیری", text_fa)

    def test_blog_and_crawled_articles(self):
        # Persian blog lists all 7 authentic articles
        status_fa, hdrs_fa, text_fa = request("GET", "/blog", query="lang=fa")
        self.assertEqual(status_fa, 200)
        self.assertIn("مهاجرت یک نفره، ترومای دسته‌جمعی", text_fa)
        self.assertIn("روان‌شناسی و تاریخ بیهقی", text_fa)
        self.assertIn("سوگ", text_fa)
        self.assertIn("تروما فراتر از زخم‌های نادیدنی", text_fa)
        self.assertIn("نجاستت را پنهان کن", text_fa)
        self.assertIn("آبان ۱۴۰۵", text_fa)  # Persian calendar in article meta

        # English blog lists English counterparts
        status_en, hdrs_en, text_en = request("GET", "/blog", query="lang=en")
        self.assertEqual(status_en, 200)
        self.assertIn("Individual Migration, Collective Trauma", text_en)
        self.assertIn("Tarikh-e Beyhaqi", text_en)
        self.assertIn("Grief (Soog)", text_en)

    def test_article_detail_page(self):
        status, hdrs, text = request(
            "GET",
            "/blog/psychology-and-tarikh-e-beyhaqi-classical-literature",
            query="lang=fa"
        )
        self.assertEqual(status, 200)
        self.assertIn("تاریخ بیهقی", text)
        self.assertIn("t.me/dasein_journal/14", text)

        status_grief, hdrs_grief, text_grief = request(
            "GET",
            "/blog/grief-soog-psychology-philosophy-iranian-rituals",
            query="lang=fa"
        )
        self.assertEqual(status_grief, 200)
        self.assertIn("سوگ‌نگاره شاهنامه", text_grief)
        self.assertIn("t.me/dasein_journal/22", text_grief)

    def test_google_calendar_and_meet_integration(self):
        # Booking online consultation returns Google Meet & Google Calendar links
        payload = json.dumps({
            "client_name": "Online Client",
            "email": "online@example.com",
            "phone": "+989127778899",
            "preferred_date": "2026-11-20",
            "preferred_time": "Evening (17:00 - 20:00)",
            "service_type": "Existential Therapy",
            "session_format": "Online",
            "notes": "Testing Google Meet link generation.",
            "language_used": "fa"
        }).encode("utf-8")

        status, hdrs, body = request(
            "POST",
            "/api/appointments",
            headers=[("content-type", "application/json")],
            body=payload
        )
        self.assertEqual(status, 200)
        res = json.loads(body)
        self.assertTrue(res.get("success"))
        self.assertIn("meet_link", res)
        self.assertIn("meet.google.com", res["meet_link"])
        self.assertIn("google_calendar_url", res)
        self.assertIn("calendar.google.com/calendar/render", res["google_calendar_url"])
        self.assertIn("das-ein-meet", res["google_calendar_url"])

    def test_persian_calendar_conversions(self):
        # Unit tests on Jalali utility
        jy, jm, jd = gregorian_to_jalali(2026, 11, 20)
        self.assertEqual(jy, 1405)
        self.assertEqual(jm, 8)
        self.assertEqual(jd, 29)

        g_date = jalali_to_gregorian(1405, 8, 29)
        self.assertEqual(str(g_date), "2026-11-20")

        shamsi_text = format_jalali_date("2026-11-20")
        self.assertIn("آبان ۱۴۰۵", shamsi_text)

        # Booking with Shamsi date converts to Gregorian correctly
        payload = json.dumps({
            "client_name": "Shamsi Booking Client",
            "email": "shamsi@example.com",
            "phone": "+989123334455",
            "preferred_date_shamsi": "1405/08/29",
            "preferred_time": "Morning (9:00 - 12:00)",
            "service_type": "Anxiety & Stress Management",
            "session_format": "Online",
            "notes": "Preferred date picked in Persian calendar.",
            "language_used": "fa"
        }).encode("utf-8")

        status, hdrs, body = request(
            "POST",
            "/api/appointments",
            headers=[("content-type", "application/json")],
            body=payload
        )
        self.assertEqual(status, 200)
        res = json.loads(body)
        self.assertEqual(res["preferred_date"], "2026-11-20")
        self.assertIn("۱۴۰۵", res["preferred_date_shamsi"])

    def test_notification_popups_and_events(self):
        # Homepage has appointment confirmation modal and event notification popup
        status, hdrs, text = request("GET", "/?lang=fa")
        self.assertEqual(status, 200)
        self.assertIn("appointmentSuccessModal", text)
        self.assertIn("eventNotificationPopup", text)
        self.assertIn("کارگاه آنلاین و تخصصی", text)
        self.assertIn("meet.google.com", text)
        self.assertIn("persian_calendar.js", text)

        # Booking page has interactive Persian calendar picker
        status_b, hdrs_b, text_b = request("GET", "/booking?lang=fa")
        self.assertEqual(status_b, 200)
        self.assertIn("shamsiPickerWrap", text_b)
        self.assertIn("shamsiMonth", text_b)

    def test_admin_auth_and_social_panel(self):
        # Login
        login_body = urllib.parse.urlencode({
            "username": "admin",
            "password": "psychologist2026"
        }).encode("utf-8")
        status, hdrs, body = request(
            "POST",
            "/admin/login",
            headers=[("content-type", "application/x-www-form-urlencoded")],
            body=login_body
        )
        self.assertEqual(status, 303)
        cookie = hdrs.get("set-cookie")
        self.assertIsNotNone(cookie)
        cookie_header = cookie.split(";")[0]

        auth_headers = [("cookie", cookie_header)]

        # Dashboard contains notification bell
        status_dash, hdrs_dash, text_dash = request("GET", "/admin", headers=auth_headers)
        self.assertEqual(status_dash, 200)
        self.assertIn("Dasein Journal", text_dash)
        self.assertIn("adminNotifBell", text_dash)
        self.assertIn("adminNotifDropdown", text_dash)

        # Admin notifications API
        status_notif, hdrs_notif, body_notif = request("GET", "/api/admin/notifications", headers=auth_headers)
        self.assertEqual(status_notif, 200)
        notif_data = json.loads(body_notif)
        self.assertIn("pending_count", notif_data)
        self.assertIn("events", notif_data)

        # Appointments management shows Shamsi date & Meet link
        status_appts, hdrs_appts, text_appts = request("GET", "/admin/appointments", headers=auth_headers)
        self.assertEqual(status_appts, 200)
        self.assertIn("Meet", text_appts)
        self.assertIn("Cal", text_appts)

        # Social Panel
        status_soc, hdrs_soc, text_soc = request("GET", "/admin/social", headers=auth_headers)
        self.assertEqual(status_soc, 200)
        self.assertIn("Telegram Channel Auto-Post", text_soc)
        self.assertIn("Instagram Auto-Publish", text_soc)
        self.assertIn("@dasein_journal", text_soc)
        self.assertIn("dasein.journal", text_soc)


if __name__ == "__main__":
    unittest.main()

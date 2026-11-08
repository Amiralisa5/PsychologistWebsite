import asyncio
import json
import unittest
import urllib.parse
from app.main import app


async def asgi_request(method="GET", path="/", query="", headers=None, body=b""):
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

    def test_api_endpoints(self):
        # Appointments API
        payload = json.dumps({
            "client_name": "Test Client",
            "email": "test@example.com",
            "phone": "+989120000000",
            "preferred_date": "2026-12-01",
            "preferred_time": "Morning (9:00 - 12:00)",
            "service_type": "Existential Therapy",
            "session_format": "Online",
            "notes": "Testing appointment booking flow.",
            "language_used": "en"
        }).encode("utf-8")
        status, hdrs, body = request(
            "POST",
            "/api/appointments",
            headers=[("content-type", "application/json")],
            body=payload
        )
        self.assertEqual(status, 200)
        resp_json = json.loads(body)
        self.assertTrue(resp_json.get("success"))

        # Articles API
        status_art, hdrs_art, body_art = request("GET", "/api/articles")
        self.assertEqual(status_art, 200)
        arts = json.loads(body_art)
        self.assertGreaterEqual(len(arts), 7)

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

        # Dashboard
        status_dash, hdrs_dash, text_dash = request("GET", "/admin", headers=auth_headers)
        self.assertEqual(status_dash, 200)
        self.assertIn("Dasein Journal", text_dash)
        self.assertIn("Dashboard Overview", text_dash)

        # Social Panel
        status_soc, hdrs_soc, text_soc = request("GET", "/admin/social", headers=auth_headers)
        self.assertEqual(status_soc, 200)
        self.assertIn("Telegram Channel Auto-Post", text_soc)
        self.assertIn("Instagram Auto-Publish", text_soc)
        self.assertIn("@dasein_journal", text_soc)
        self.assertIn("dasein.journal", text_soc)

        # Save social settings (telegram section)
        social_body = urllib.parse.urlencode({
            "section": "telegram",
            "telegram_enabled": "true",
            "telegram_bot_token": "TEST_TOKEN_123",
            "telegram_channel_id": "@dasein_journal",
            "telegram_auto_publish": "true"
        }).encode("utf-8")

        status_save, hdrs_save, text_save = request(
            "POST",
            "/admin/social",
            headers=auth_headers + [("content-type", "application/x-www-form-urlencoded")],
            body=social_body
        )
        self.assertEqual(status_save, 303)

        # Verify updated settings
        status_soc2, hdrs_soc2, text_soc2 = request("GET", "/admin/social", headers=auth_headers)
        self.assertEqual(status_soc2, 200)
        self.assertIn("TEST_TOKEN_123", text_soc2)

        # Articles management panel
        status_arts, hdrs_arts, text_arts = request("GET", "/admin/articles", headers=auth_headers)
        self.assertEqual(status_arts, 200)
        self.assertIn("Telegram", text_arts)
        self.assertIn("Instagram", text_arts)


if __name__ == "__main__":
    unittest.main()

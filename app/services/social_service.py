import urllib.request
import urllib.parse
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def send_telegram_post(bot_token: str, chat_id: str, text: str, photo_url: Optional[str] = None) -> tuple[bool, str]:
    """
    Sends message or photo to a Telegram channel/group using Telegram Bot API.
    """
    if not bot_token or not chat_id:
        return False, "Telegram Bot Token or Channel/Chat ID not configured."

    # Normalize chat_id
    chat_id = chat_id.strip()
    if not chat_id.startswith("@") and not chat_id.startswith("-") and not chat_id.isdigit():
        chat_id = f"@{chat_id}"

    try:
        if photo_url and photo_url.startswith("http"):
            api_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            payload = {
                "chat_id": chat_id,
                "photo": photo_url,
                "caption": text[:1024],  # Telegram caption max 1024 chars
                "parse_mode": "HTML"
            }
        else:
            api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text[:4096],  # Telegram text max 4096 chars
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            api_url,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            if resp_data.get("ok"):
                msg_id = str(resp_data.get("result", {}).get("message_id", "sent"))
                return True, msg_id
            else:
                return False, resp_data.get("description", "Unknown Telegram API error")

    except Exception as e:
        logger.error(f"Error publishing to Telegram: {e}")
        return False, str(e)


def send_instagram_post(account_id: str, access_token: str, caption: str, image_url: str) -> tuple[bool, str]:
    """
    Publishes an image post to an Instagram Business/Creator account via Meta Graph API.
    """
    if not account_id or not access_token:
        return False, "Instagram Account ID or Graph API Access Token not configured."

    if not image_url or not image_url.startswith("http"):
        return False, "Instagram publishing requires a publicly accessible HTTPS image URL."

    try:
        # Step 1: Create media container
        create_url = f"https://graph.facebook.com/v19.0/{account_id}/media"
        params = urllib.parse.urlencode({
            "image_url": image_url,
            "caption": caption[:2200],
            "access_token": access_token
        }).encode("utf-8")

        req = urllib.request.Request(create_url, data=params)
        with urllib.request.urlopen(req, timeout=15) as resp:
            create_res = json.loads(resp.read().decode("utf-8"))
            creation_id = create_res.get("id")

        if not creation_id:
            return False, "Failed to create Instagram media container."

        # Step 2: Publish media container
        publish_url = f"https://graph.facebook.com/v19.0/{account_id}/media_publish"
        publish_params = urllib.parse.urlencode({
            "creation_id": creation_id,
            "access_token": access_token
        }).encode("utf-8")

        publish_req = urllib.request.Request(publish_url, data=publish_params)
        with urllib.request.urlopen(publish_req, timeout=15) as resp:
            publish_res = json.loads(resp.read().decode("utf-8"))
            post_id = publish_res.get("id")
            if post_id:
                return True, str(post_id)
            else:
                return False, "Could not publish media container."

    except Exception as e:
        logger.error(f"Error publishing to Instagram: {e}")
        return False, str(e)


def format_article_for_telegram(article, base_url: str = "http://127.0.0.1:8000") -> str:
    article_link = f"{base_url}/blog/{article.slug}?lang=fa"
    tags = f"#روانشناسی #دازاین #اگزیستانسیال #{article.category.replace(' ', '_').replace('&', '_')}"
    
    return (
        f"🌿 <b>ژورنال دازاین | Dasein Journal</b>\n"
        f"دکتر حسن آقانصیری | روانشناس بالینی و روان‌درمانگر\n\n"
        f"📌 <b>{article.title_fa}</b>\n"
        f"<i>{article.title_en}</i>\n\n"
        f"دسته: {article.category} | ⏱️ {article.read_time} دقیقه مطالعه\n\n"
        f"💬 <b>چکیده:</b>\n"
        f"{article.excerpt_fa}\n\n"
        f"🔗 <b>مطالعه متن کامل مقاله در وب‌سایت:</b>\n"
        f"<a href=\"{article_link}\">{article_link}</a>\n\n"
        f"🆔 @dasein_journal\n"
        f"📸 instagram.com/dasein.journal\n"
        f"{tags}"
    )


def format_article_for_instagram(article, base_url: str = "http://127.0.0.1:8000") -> str:
    article_link = f"{base_url}/blog/{article.slug}?lang=fa"
    return (
        f"🌿 {article.title_fa}\n"
        f"({article.title_en})\n\n"
        f"دکتر حسن آقانصیری | ژورنال دازاین\n\n"
        f"{article.excerpt_fa}\n\n"
        f"─── ⋆⋅☆⋅⋆ ───\n"
        f"برای مطالعه متن کامل و تحلیلی این نوشتار، به وب‌سایت دازاین (لینک در بیو) یا کانال تلگرام مراجعه فرمایید.\n\n"
        f"🔗 وب‌سایت: {article_link}\n"
        f"✈️ تلگرام: @dasein_journal\n\n"
        f"#دکتر_حسن_آقانصیری #دازاین #روانشناسی #اگزیستانسیال #روانکاوی #تروما #سلامت_روان #dasein_journal"
    )

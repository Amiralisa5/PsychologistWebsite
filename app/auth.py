import hashlib
import hmac
import os
import secrets
import json
import base64
from typing import Optional

SECRET_KEY = os.environ.get("SECRET_KEY", "psy-fathi-safe-secret-key-2026-secure-session")


def hash_password(password: str) -> tuple[str, str]:
    salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations=100000
    ).hex()
    return pw_hash, salt


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations=100000
    ).hex()
    return hmac.compare_digest(pw_hash, stored_hash)


def create_session_token(username: str, role: str) -> str:
    payload = {
        "username": username,
        "role": role,
        "nonce": secrets.token_hex(8)
    }
    payload_json = json.dumps(payload, separators=(',', ':'))
    b64_payload = base64.urlsafe_b64encode(payload_json.encode()).decode()
    signature = hmac.new(SECRET_KEY.encode(), b64_payload.encode(), hashlib.sha256).hexdigest()
    return f"{b64_payload}.{signature}"


def verify_session_token(token: Optional[str]) -> Optional[dict]:
    if not token or "." not in token:
        return None
    try:
        b64_payload, signature = token.split(".", 1)
        expected_sig = hmac.new(SECRET_KEY.encode(), b64_payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return None
        payload_bytes = base64.urlsafe_b64decode(b64_payload.encode())
        payload = json.loads(payload_bytes.decode())
        return payload
    except Exception:
        return None

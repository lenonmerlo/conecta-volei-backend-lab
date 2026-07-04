import base64
import hashlib
import hmac
import json
import time
from typing import Any


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("utf-8")

def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}")

def create_access_token(
        *,
        subject: str,
        secret_key: str,
        expires_in_minutes: int,
) -> str:
    now = int(time.time())
    header = {
        "alg": "HS256",
        "typ": "JWT",
    }
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + expires_in_minutes * 60,
    }

    encoded_header = _base64url_encode(
        json.dumps(header, separators=(",", ":")).encode(),
    )
    encoded_payload = _base64url_encode(
        json.dumps(payload, separators=(",", ":")).encode(),
    )
    signing_input = f"{encoded_header}.{encoded_payload}".encode()

    signature = hmac.new(
        secret_key.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()

    return f"{encoded_header}.{encoded_payload}.{_base64url_encode(signature)}"

def decode_access_token(token: str, *, secret_key: str) -> dict[str, Any] | None:
    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".")
    except ValueError:
        return None

    signing_input = f"{encoded_header}.{encoded_payload}".encode()
    expected_signature = hmac.new(
        secret_key.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()

    received_signature = _base64url_decode(encoded_signature)
    if not hmac.compare_digest(expected_signature, received_signature):
        return None

    payload = json.loads(_base64url_decode(encoded_payload))
    expires_at = payload.get("exp")

    if not isinstance(expires_at, int) or expires_at < int(time.time()):
        return None

    return payload




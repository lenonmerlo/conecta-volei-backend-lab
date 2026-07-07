import base64
import hashlib
import hmac
import json
import time
from typing import Any

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("utf-8")


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}")


def _create_token(
    *,
    subject: str,
    secret_key: str,
    expires_in_minutes: int,
    token_type: str,
) -> str:
    now = int(time.time())
    header = {
        "alg": "HS256",
        "typ": "JWT",
    }
    payload = {
        "sub": subject,
        "type": token_type,
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


def _decode_token(
    token: str,
    *,
    secret_key: str,
    expected_type: str,
) -> dict[str, Any] | None:
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
    token_type = payload.get("type")

    if not isinstance(expires_at, int) or expires_at < int(time.time()):
        return None

    if token_type != expected_type:
        return None

    return payload


def create_access_token(
    *,
    subject: str,
    secret_key: str,
    expires_in_minutes: int,
) -> str:
    return _create_token(
        subject=subject,
        secret_key=secret_key,
        expires_in_minutes=expires_in_minutes,
        token_type=ACCESS_TOKEN_TYPE,
    )


def create_refresh_token(
    *,
    subject: str,
    secret_key: str,
    expires_in_minutes: int,
) -> str:
    return _create_token(
        subject=subject,
        secret_key=secret_key,
        expires_in_minutes=expires_in_minutes,
        token_type=REFRESH_TOKEN_TYPE,
    )


def decode_access_token(token: str, *, secret_key: str) -> dict[str, Any] | None:
    return _decode_token(
        token,
        secret_key=secret_key,
        expected_type=ACCESS_TOKEN_TYPE,
    )


def decode_refresh_token(token: str, *, secret_key: str) -> dict[str, Any] | None:
    return _decode_token(
        token,
        secret_key=secret_key,
        expected_type=REFRESH_TOKEN_TYPE,
    )
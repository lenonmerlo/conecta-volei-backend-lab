import json
from typing import Any

from redis import Redis

from app.core.config import settings

redis_client = Redis.from_url(
    settings.redis_url,
    decode_responses=True,
)

def ping_cache() -> bool:
    return redis_client.ping()

def get_json(key: str) -> Any | None:
    cached_value = redis_client.get(key)
    if cached_value is None:
        return None

    return json.loads(cached_value)

def set_json(key: str, value: Any, *, ttl_seconds: int = 60) -> None:
    redis_client.set(
        key,
        json.dumps(value),
        ex=ttl_seconds,
    )

def delete_key(key: str) -> None:
    redis_client.delete(key)
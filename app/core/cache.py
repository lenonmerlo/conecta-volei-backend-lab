from redis import Redis

from app.core.config import settings

redis_client = Redis.from_url(
    settings.redis_url,
    decode_responses=True,
)

def ping_cache() -> bool:
    return redis_client.ping()
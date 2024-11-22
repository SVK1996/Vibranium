# app/core/cache.py
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis
from ..core.config import settings

async def setup_cache():
  redis = aioredis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
  FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
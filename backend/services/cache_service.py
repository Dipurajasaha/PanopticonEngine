import os
import json
import redis
from datetime import timedelta
import logging
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL","redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

#############################################################################
# -- Cache Keys --
#############################################################################
DASHBOARD_CACHE_KEY = "global_dashboard_summary"
FINANCE_DATA_VERSION_KEY = "finance_data_version"

#############################################################################
# -- Dashboard Cache Operations --
#############################################################################
def get_dashboard_cache():
    try:
        cached_data = redis_client.get(DASHBOARD_CACHE_KEY)
    except RedisError as exc:
        logger.warning("Redis unavailable while reading dashboard cache: %s", exc)
        return None

    if cached_data:
        try:
            return json.loads(cached_data)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON in dashboard cache; ignoring cached payload")
            return None
    return None

def set_dashboard_cache(data: dict):
    try:
        redis_client.setex(
            DASHBOARD_CACHE_KEY,
            timedelta(hours=1),
            value=json.dumps(data)
        )
    except RedisError as exc:
        logger.warning("Redis unavailable while writing dashboard cache: %s", exc)

def invalidate_dashboard_cache():
    try:
        redis_client.delete(DASHBOARD_CACHE_KEY)
    except RedisError as exc:
        logger.warning("Redis unavailable while invalidating dashboard cache: %s", exc)


#############################################################################
# -- Finance Version Operations --
#############################################################################
def get_finance_data_version() -> int:
    try:
        current = redis_client.get(FINANCE_DATA_VERSION_KEY)
        if current is None:
            redis_client.set(FINANCE_DATA_VERSION_KEY, 0)
            return 0
        return int(current)
    except (RedisError, ValueError) as exc:
        logger.warning("Redis unavailable while reading finance data version: %s", exc)
        return 0


def bump_finance_data_version() -> int:
    try:
        return int(redis_client.incr(FINANCE_DATA_VERSION_KEY))
    except (RedisError, ValueError) as exc:
        logger.warning("Redis unavailable while bumping finance data version: %s", exc)
        return 0
from django_redis import cache, exceptions

from django_prometheus.cache.metrics import (
    django_cache_get_fail_total,
    django_cache_get_total,
    django_cache_hits_total,
    django_cache_misses_total,
)


class RedisCache(cache.RedisCache):
    """Inherit redis to add metrics about hit/miss/interruption ratio"""

    @cache.omit_exception
    def get(self, key, default=None, version=None, client=None):
        try:
            django_cache_get_total.labels(backend='redis').inc()
            cached = self.client.get(
                key,
                default=None,
                version=version,
                client=client
            )
        except exceptions.ConnectionInterrupted as e:
            django_cache_get_fail_total.labels(backend='redis').inc()
            if cache.DJANGO_REDIS_IGNORE_EXCEPTIONS or self._ignore_exceptions:
                if cache.DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS:
                    cache.logger.error(str(e))
                return default
            raise
        else:
            if cached is not None:
                django_cache_hits_total.labels(backend='redis').inc()
            else:
                django_cache_misses_total.labels(backend='redis').inc()
            return cached or default

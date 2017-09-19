from django.core.cache import caches
from django.core.cache.backends.base import BaseCache, DEFAULT_TIMEOUT


class FallthroughCache(BaseCache):
    def __init__(self, location, params):
        options = params.get('OPTIONS', {})
        cache_names = options.get('cache_names', [])

        if len(cache_names) == 0:
            raise ValueError('FallthroughCache requires at least 1 cache')

        self.caches = [caches[name] for name in cache_names]
        if any(cache.default_timeout is None for cache in self.caches[0:-1]):
            raise ValueError('All but the last cache used by FallthroughCache '
                             'must have a timeout')

        self.root_cache = self.caches[-1]

    def add(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        return self.root_cache.add(key, value, timeout=timeout,
                                   version=version)

    def get(self, key, default=None, version=None):
        for index, cache in enumerate(self.caches):
            value = cache.get(key, version=version)

            if value is not None:
                for prior_cache in reversed(self.caches[:index]):
                    prior_cache.set(key, value, version=version)
                return value

        return default

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        self.root_cache.set(key, value, timeout=timeout, version=version)

        # Invalidate non-root caches to avoid surprising behavior where getting
        # a value immediately after setting it (e.g. in the span of a single
        # web request) returns a stale result.
        for cache in reversed(self.caches[:-1]):
            cache.delete(key, version=version)

    def set_many(self, data, timeout=DEFAULT_TIMEOUT, version=None):
        self.root_cache.set_many(data, timeout=timeout, version=version)

        # Invalidate non-root caches to avoid surprising behavior where getting
        # a value immediately after setting it (e.g. in the span of a single
        # web request) returns a stale result.
        for cache in reversed(self.caches[:-1]):
            cache.delete_many(data.keys(), version=version)

    def delete(self, key, version=None):
        self.root_cache.delete(key, version=version)

    def delete_many(self, keys, version=None):
        self.root_cache.delete_many(keys, version=version)

    def clear(self):
        self.root_cache.clear()

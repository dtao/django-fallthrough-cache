from django.core.cache import caches
from django.core.cache.backends.base import BaseCache, DEFAULT_TIMEOUT


class FallthroughCache(BaseCache):
    @classmethod
    def create(cls, cache_names):
        return cls(None, {
            'OPTIONS': {
                'cache_names': cache_names
            }
        })

    def __init__(self, location, params):
        options = params.get('OPTIONS', {})
        cache_names = options.get('cache_names', [])

        if len(cache_names) == 0:
            raise ValueError('FallthroughCache requires at least 1 cache')

        self.caches = [caches[name] for name in cache_names]

    def add(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        return self.caches[-1].add(key, value, timeout=timeout,
                                   version=version)

    def get(self, key, default=None, version=None):
        return self._get_with_fallthrough(key, 0, default=default,
                                          version=version)

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        self.caches[-1].set(key, value, timeout=timeout, version=version)

    def set_many(self, data, timeout=DEFAULT_TIMEOUT, version=None):
        self.caches[-1].set_many(data, timeout=timeout, version=version)

    def delete(self, key, version=None):
        self.caches[-1].delete(key, version=version)

    def delete_many(self, keys, version=None):
        self.caches[-1].delete_many(keys, version=version)

    def clear(self):
        self.caches[-1].clear()

    def _get_with_fallthrough(self, key, index, default, version):
        cache = self.caches[index]
        if index == len(self.caches) - 1:
            return cache.get(key, default=default, version=version)
        return cache.get_or_set(
            key, lambda: self._get_with_fallthrough(key, index + 1, default,
                                                    version),
            version=version)

from django.core.cache import caches
from django.core.cache.backends.base import BaseCache


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

    def get(self, key, *args, **kwargs):
        return self._get_with_fallthrough(key, 0)

    def set(self, key, value, *args, **kwargs):
        self.caches[-1].set(key, value)

    def delete(self, key, *args, **kwargs):
        self.caches[-1].delete(key)

    def _get_with_fallthrough(self, key, index):
        cache = self.caches[index]
        if index == len(self.caches) - 1:
            return cache.get(key)
        return cache.get_or_set(
            key, lambda: self._get_with_fallthrough(key, index + 1))

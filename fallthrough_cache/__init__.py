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
        index = 0
        value = None

        while index < len(self.caches):
            cache = self.caches[index]
            if index == len(self.caches) - 1:
                value = cache.get(key, default=default, version=version)
            else:
                value = cache.get(key, version=version)

            if value is not None:
                break

            index += 1

        # Only back-populate caches if a value other than None was retrieved
        # This implementation is unfortunately necessary due to what I would
        # describe as a bug in Django, which won't be fixed until 1.11.6 at the
        # absolute earliest.
        # https://github.com/django/django/pull/9087
        if value is not None:
            while index > 0:
                index -= 1
                self.caches[index].set(key, value, version=version)

        return value

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

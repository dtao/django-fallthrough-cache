# django-fallthrough-cache

An implementation of Django's cache backend interface that allows you to put a
fast cache (e.g. `LocMemCache`) in front of a slower one (e.g. `PyLibMCCache`).

## Usage

The configuration below sets up 3 caches: 'locmem', 'memcache', and
'fallthrough'. The fallthrough cache will look up values in the local memory
cache, and on cache misses it will fall through to memcache.

```python
CACHES = {
    'locmem': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'local-memory',
        'TIMEOUT': 60,
        'VERSION': 1
    },
    'memcache': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': os.environ['MEMCACHE_HOST'],
        'TIMEOUT': None,
        'OPTIONS': {
            'connect_timeout': 1000,
            'receive_timeout': 1000000,
            'send_timeout': 1000000,
            'dead_timeout': 5,
        },
        'VERSION': 1
    },
    'fallthrough': {
        'BACKEND': 'fallthrough_cache.FallthroughCache',
        'OPTIONS': {
            'cache_names': ['locmem', 'memcache']
        }
    }
}
```

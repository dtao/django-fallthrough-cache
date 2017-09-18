TEST_RUNNER = 'django.test.runner.DiscoverRunner'

SECRET_KEY = 'whatever'

CACHES = {
    'a': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'a',
        'TIMEOUT': 60,
        'VERSION': 1
    },
    'b': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'b',
        'TIMEOUT': 3600,
        'VERSION': 1
    },
    'c': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'c',
        'TIMEOUT': None,
        'VERSION': 1
    },
    'fallthrough': {
        'BACKEND': 'fallthrough_cache.FallthroughCache',
        'LOCATION': 'fallthrough',
        'OPTIONS': {
            'cache_names': ['a', 'b', 'c']
        }
    },
    'notimeout': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'notimeout',
        'TIMEOUT': None,
        'VERSION': 1
    }
}

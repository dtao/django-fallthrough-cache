import pytest

from django.core.cache import caches

from fallthrough_cache import FallthroughCache


def setup():
    caches['a'].clear()
    caches['b'].clear()
    caches['c'].clear()


def test_get_picks_first_result():
    cache = FallthroughCache.create(['a', 'b', 'c'])

    caches['a'].add('foo', 1)
    caches['b'].add('foo', 2)
    caches['c'].add('foo', 3)

    assert cache.get('foo') == 1


def test_get_falls_through():
    cache = FallthroughCache.create(['a', 'b', 'c'])

    caches['b'].add('foo', 2)
    caches['c'].add('foo', 3)

    assert cache.get('foo') == 2

    # Getting foo from b should have populated a
    assert caches['a'].get('foo') == 2

    caches['a'].delete('foo')
    caches['b'].delete('foo')

    assert cache.get('foo') == 3

    # Getting foo from c should have populated a and b
    assert caches['a'].get('foo') == 3
    assert caches['b'].get('foo') == 3


def test_set_updates_bottom_cache():
    cache = FallthroughCache.create(['a', 'b', 'c'])

    cache.set('foo', 3)

    assert caches['c'].get('foo') == 3


def test_delete_updates_bottom_cache():
    cache = FallthroughCache.create(['a', 'b', 'c'])

    caches['a'].set('foo', 1)
    caches['b'].set('foo', 2)
    caches['c'].set('foo', 3)

    cache.delete('foo')

    assert caches['c'].get('foo') is None


def test_django_configuration():
    cache = caches['fallthrough']

    caches['a'].set('foo', 1)
    caches['b'].set('foo', 2)
    caches['c'].set('foo', 3)

    assert cache.get('foo') == 1

    caches['a'].delete('foo')
    assert cache.get('foo') == 2

    caches['a'].delete('foo')
    caches['b'].delete('foo')
    assert cache.get('foo') == 3

    caches['a'].delete('foo')
    caches['b'].delete('foo')
    caches['c'].delete('foo')
    assert cache.get('foo') is None


def test_requires_at_least_one_cache():
    with pytest.raises(ValueError):
        FallthroughCache.create([])

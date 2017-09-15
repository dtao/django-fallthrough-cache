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


def test_get_supports_default():
    cache = FallthroughCache.create(['a', 'b', 'c'])

    caches['a'].set('foo', 1)
    caches['b'].set('bar', 2)
    caches['c'].set('baz', 3)

    assert cache.get('quux', default=4) == 4


def test_get_respects_version():
    cache = FallthroughCache.create(['a', 'b', 'c'])

    caches['a'].set('foo', 1, version=1)
    caches['b'].set('foo', 2, version=2)
    caches['c'].set('foo', 3, version=3)

    assert cache.get('foo', version=4) is None
    assert cache.get('foo', version=2) == 2

    # Ensure existing versions have not been overwritten
    assert caches['a'].get('foo', version=1) == 1
    assert caches['b'].get('foo', version=2) == 2
    assert caches['c'].get('foo', version=3) == 3


def test_get_many():
    cache = FallthroughCache.create(['a', 'b', 'c'])

    caches['a'].add('foo', 1)
    caches['b'].add('bar', 2)
    caches['c'].add('baz', 3)

    assert cache.get_many(['foo', 'bar', 'baz']) == {
        'foo': 1,
        'bar': 2,
        'baz': 3
    }
    assert caches['a'].get('bar') == 2
    assert caches['a'].get('baz') == 3
    assert caches['b'].get('baz') == 3


def test_get_or_set():
    cache = FallthroughCache.create(['a', 'b'])

    assert cache.get('foo') is None

    # Previous call to get, returning None, should not have populated a
    caches['b'].add('foo', 1)
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


def test_set_respects_version():
    cache = FallthroughCache.create(['a', 'b', 'c'])

    cache.set('foo', 3, version=2)

    assert caches['c'].get('foo') is None
    assert caches['c'].get('foo', version=1) is None
    assert caches['c'].get('foo', version=2) == 3


def test_set_many():
    cache = FallthroughCache.create(['a', 'b', 'c'])

    cache.set_many({'foo': 1, 'bar': 2, 'baz': 3})

    assert caches['c'].get_many(['foo', 'bar', 'baz']) == {
        'foo': 1,
        'bar': 2,
        'baz': 3
    }


def test_add_updates_bottom_cache():
    cache = FallthroughCache.create(['a', 'b', 'c'])

    cache.add('foo', 1)

    assert caches['c'].get('foo') == 1

    # Ensure calling add does not replace existing value
    cache.add('foo', 2)
    assert caches['c'].get('foo') == 1


def test_delete_updates_bottom_cache():
    cache = FallthroughCache.create(['a', 'b', 'c'])

    caches['a'].set('foo', 1)
    caches['b'].set('foo', 2)
    caches['c'].set('foo', 3)

    cache.delete('foo')

    assert caches['c'].get('foo') is None


def test_delete_respects_version():
    cache = FallthroughCache.create(['a', 'b', 'c'])

    caches['c'].set('foo', 1, version=1)
    caches['c'].set('foo', 2, version=2)
    caches['c'].set('foo', 3, version=3)

    cache.delete('foo', version=2)

    assert caches['c'].get('foo', version=1) == 1
    assert caches['c'].get('foo', version=2) is None
    assert caches['c'].get('foo', version=3) == 3


def test_delete_many():
    cache = FallthroughCache.create(['a', 'b', 'c'])

    caches['c'].set('foo', 1)
    caches['c'].set('bar', 2)
    caches['c'].set('baz', 3)

    cache.delete_many(['bar', 'baz'])
    assert caches['c'].get_many(['foo', 'bar', 'baz']) == {'foo': 1}


def test_clear_updates_bottom_cache():
    cache = FallthroughCache.create(['a', 'b', 'c'])

    caches['c'].set('foo', 1)
    caches['c'].set('bar', 2)
    caches['c'].set('baz', 3)

    cache.clear()

    assert caches['c'].get_many(['foo', 'bar', 'baz']) == {}


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

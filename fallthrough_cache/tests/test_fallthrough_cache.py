import pytest

from django.core.cache import caches

from fallthrough_cache import FallthroughCache


def setup():
    caches['a'].clear()
    caches['b'].clear()
    caches['c'].clear()


def create_fallthrough_cache(cache_names):
    return FallthroughCache(None, {
        'OPTIONS': {
            'cache_names': cache_names
        }
    })


def test_get_picks_first_result():
    cache = create_fallthrough_cache(['a', 'b', 'c'])

    caches['a'].add('foo', 1)
    caches['b'].add('foo', 2)
    caches['c'].add('foo', 3)

    assert cache.get('foo') == 1


def test_get_supports_default():
    cache = create_fallthrough_cache(['a', 'b', 'c'])

    caches['a'].set('foo', 1)
    caches['b'].set('bar', 2)
    caches['c'].set('baz', 3)

    assert cache.get('quux', default=4) == 4


def test_get_respects_version():
    cache = create_fallthrough_cache(['a', 'b', 'c'])

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
    cache = create_fallthrough_cache(['a', 'b', 'c'])

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
    cache = create_fallthrough_cache(['a', 'b'])

    assert cache.get_or_set('foo', 5) == 5

    assert cache.get('foo') == 5
    assert caches['b'].get('foo') == 5


def test_get_falls_through():
    cache = create_fallthrough_cache(['a', 'b', 'c'])

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


def test_get_does_not_update_on_none():
    cache = create_fallthrough_cache(['a', 'b'])

    assert cache.get('foo') is None

    # Previous call to get, returning None, should not have populated a
    caches['b'].add('foo', 1)
    assert cache.get('foo') == 1


def test_get_does_not_update_on_default():
    cache = create_fallthrough_cache(['a', 'b'])

    assert cache.get('foo', default='bar') == 'bar'

    # Default value should not have been stored in any cache
    assert caches['a'].get('foo') is None
    assert caches['b'].get('foo') is None


def test_set_updates_bottom_cache():
    cache = create_fallthrough_cache(['a', 'b', 'c'])

    cache.set('foo', 3)

    assert caches['c'].get('foo') == 3


def test_set_invalidates_upper_caches():
    cache = create_fallthrough_cache(['a', 'b', 'c'])

    caches['a'].set('foo', 1)
    caches['b'].set('foo', 2)
    cache.set('foo', 3)

    assert caches['a'].get('foo') is None
    assert caches['b'].get('foo') is None
    assert caches['c'].get('foo') == 3


def test_set_respects_version():
    cache = create_fallthrough_cache(['a', 'b', 'c'])

    cache.set('foo', 3, version=2)

    assert caches['c'].get('foo') is None
    assert caches['c'].get('foo', version=1) is None
    assert caches['c'].get('foo', version=2) == 3


def test_set_many():
    cache = create_fallthrough_cache(['a', 'b', 'c'])

    cache.set_many({'foo': 1, 'bar': 2, 'baz': 3})

    assert caches['c'].get_many(['foo', 'bar', 'baz']) == {
        'foo': 1,
        'bar': 2,
        'baz': 3
    }


def test_set_many_invalidates_upper_caches():
    cache = create_fallthrough_cache(['a', 'b', 'c'])

    caches['a'].set_many({'foo': 'a', 'bar': 'a', 'baz': 'a'})
    caches['b'].set_many({'foo': 'b', 'bar': 'b', 'baz': 'b'})

    cache.set_many({'foo': 1, 'bar': 2, 'baz': 3})

    assert caches['a'].get_many(['foo', 'bar', 'baz']) == {}
    assert caches['b'].get_many(['foo', 'bar', 'baz']) == {}
    assert caches['c'].get_many(['foo', 'bar', 'baz']) == {
        'foo': 1,
        'bar': 2,
        'baz': 3
    }


def test_add_updates_bottom_cache():
    cache = create_fallthrough_cache(['a', 'b', 'c'])

    cache.add('foo', 1)

    assert caches['c'].get('foo') == 1

    # Ensure calling add does not replace existing value
    cache.add('foo', 2)
    assert caches['c'].get('foo') == 1


def test_delete_updates_bottom_cache():
    cache = create_fallthrough_cache(['a', 'b', 'c'])

    caches['a'].set('foo', 1)
    caches['b'].set('foo', 2)
    caches['c'].set('foo', 3)

    cache.delete('foo')

    assert caches['c'].get('foo') is None


def test_delete_respects_version():
    cache = create_fallthrough_cache(['a', 'b', 'c'])

    caches['c'].set('foo', 1, version=1)
    caches['c'].set('foo', 2, version=2)
    caches['c'].set('foo', 3, version=3)

    cache.delete('foo', version=2)

    assert caches['c'].get('foo', version=1) == 1
    assert caches['c'].get('foo', version=2) is None
    assert caches['c'].get('foo', version=3) == 3


def test_delete_many():
    cache = create_fallthrough_cache(['a', 'b', 'c'])

    caches['c'].set('foo', 1)
    caches['c'].set('bar', 2)
    caches['c'].set('baz', 3)

    cache.delete_many(['bar', 'baz'])
    assert caches['c'].get_many(['foo', 'bar', 'baz']) == {'foo': 1}


def test_clear_updates_bottom_cache():
    cache = create_fallthrough_cache(['a', 'b', 'c'])

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
        create_fallthrough_cache([])


def test_non_root_caches_must_have_timeouts():
    with pytest.raises(ValueError):
        create_fallthrough_cache(['notimeout', 'c'])

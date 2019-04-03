# -*- coding: utf-8 -*-
"""
Tests for the resurrected Py2-like class:`dict` type.
"""

from __future__ import absolute_import, unicode_literals, print_function
import os
import sys

from future.utils import implements_iterator, PY3
from future.tests.base import unittest, skip26
from past.builtins import dict


class TestOldDict(unittest.TestCase):
    def setUp(self):
        self.d1 = dict({'C': 1, 'B': 2, 'A': 3})
        self.d2 = dict(key1='value1', key2='value2')

    def test_dict_empty(self):
        """
        dict() -> {}
        """
        self.assertEqual(dict(), {})

    def test_dict_eq(self):
        d = self.d1
        self.assertEqual(dict(d), d)

    def test_dict_keys(self):
        """
        The keys, values and items methods should now return lists on
        Python 3.x.
        """
        d = self.d1
        self.assertEqual(set(dict(d)), set(d))
        self.assertEqual(set(dict(d).keys()), set(d.keys()))
        keys = dict(d).keys()
        assert isinstance(keys, list)
        key0 = keys[0]

    def test_dict_values(self):
        d = self.d1
        self.assertEqual(set(dict(d).values()), set(d.values()))
        values = dict(d).values()
        assert isinstance(values, list)
        val0 = values[0]

    def test_dict_items(self):
        d = self.d1
        self.assertEqual(set(dict(d).items()), set(d.items()))
        items = dict(d).items()
        assert isinstance(items, list)
        item0 = items[0]

    def test_isinstance_dict(self):
        self.assertTrue(isinstance(self.d1, dict))

    def test_dict_getitem(self):
        d = dict({'C': 1, 'B': 2, 'A': 3})
        self.assertEqual(d['C'], 1)
        self.assertEqual(d['B'], 2)
        self.assertEqual(d['A'], 3)
        with self.assertRaises(KeyError):
            self.assertEqual(d['D'])

    def test_methods_produce_lists(self):
        for d in (dict(self.d1), self.d2):
            assert isinstance(d.keys(), list)
            assert isinstance(d.values(), list)
            assert isinstance(d.items(), list)

    @unittest.skipIf(sys.version_info[:2] == (2, 6),
             'set-like behaviour of dict methods is only available in Py2.7+')
    def test_set_like_behaviour(self):
        d1, d2 = self.d1, self.d2
        self.assertEqual(dict(d1).viewkeys() & dict(d2).viewkeys(), set())
        self.assertEqual(dict(d1).viewkeys() | dict(d2).viewkeys(),
                         set(['key1', 'key2', 'C', 'B', 'A']))
        self.assertTrue(isinstance(d1.viewvalues() | d2.viewkeys(), set))
        self.assertTrue(isinstance(d1.viewitems() | d2.viewitems(), set))

        with self.assertRaises(TypeError):
            d1.values() | d2.values()
            d1.keys() | d2.keys()
            d1.items() | d2.items()

    def test_braces_create_newdict_object(self):
        """
        It would nice if the {} dict syntax could be coaxed
        into producing our new dict objects somehow ...
        """
        d = self.d1
        if False:    # This doesn't work ...
            self.assertTrue(type(d) == dict)


# import UserDict
import random, string
import gc, weakref


class Py2DictTest(unittest.TestCase):
    """
    These are Py2/3-compatible ports of the unit tests from Python 2.7's
    tests/test_dict.py
    """

    def test_constructor(self):
        # calling built-in types without argument must return empty
        self.assertEqual(dict(), {})
        self.assertIsNot(dict(), {})

    @skip26
    def test_literal_constructor(self):
        # check literal constructor for different sized dicts
        # (to exercise the BUILD_MAP oparg).
        for n in (0, 1, 6, 256, 400):
            items = [(''.join(random.sample(string.ascii_letters, 8)), i)
                     for i in range(n)]
            random.shuffle(items)
            formatted_items = ('{!r}: {:d}'.format(k, v) for k, v in items)
            dictliteral = '{' + ', '.join(formatted_items) + '}'
            self.assertEqual(eval(dictliteral), dict(items))

    def test_bool(self):
        self.assertIs(not dict(), True)
        self.assertTrue(dict({1: 2}))
        self.assertIs(bool(dict({})), False)
        self.assertIs(bool(dict({1: 2})), True)

    def test_keys(self):
        d = dict()
        self.assertEqual(d.keys(), [])
        d = dict({'a': 1, 'b': 2})
        k = d.keys()
        self.assertTrue(d.has_key('a'))
        self.assertTrue(d.has_key('b'))

        self.assertRaises(TypeError, d.keys, None)

    def test_values(self):
        d = dict()
        self.assertEqual(d.values(), [])
        d = dict({1:2})
        self.assertEqual(d.values(), [2])

        self.assertRaises(TypeError, d.values, None)

    def test_items(self):
        d = dict()
        self.assertEqual(d.items(), [])

        d = dict({1:2})
        self.assertEqual(d.items(), [(1, 2)])

        self.assertRaises(TypeError, d.items, None)

    def test_has_key(self):
        d = dict()
        self.assertFalse(d.has_key('a'))
        d = dict({'a': 1, 'b': 2})
        k = d.keys()
        k.sort()
        self.assertEqual(k, ['a', 'b'])

        self.assertRaises(TypeError, d.has_key)

    def test_contains(self):
        d = dict()
        self.assertNotIn('a', d)
        self.assertFalse('a' in d)
        self.assertTrue('a' not in d)
        d = dict({'a': 1, 'b': 2})
        self.assertIn('a', d)
        self.assertIn('b', d)
        self.assertNotIn('c', d)

        self.assertRaises(TypeError, d.__contains__)

    def test_len(self):
        d = dict()
        self.assertEqual(len(d), 0)
        d = dict({'a': 1, 'b': 2})
        self.assertEqual(len(d), 2)

    def test_getitem(self):
        d = dict({'a': 1, 'b': 2})
        self.assertEqual(d['a'], 1)
        self.assertEqual(d['b'], 2)
        d['c'] = 3
        d['a'] = 4
        self.assertEqual(d['c'], 3)
        self.assertEqual(d['a'], 4)
        del d['b']
        self.assertEqual(d, dict({'a': 4, 'c': 3}))

        self.assertRaises(TypeError, d.__getitem__)

        class BadEq(object):
            def __eq__(self, other):
                raise Exc()
            def __hash__(self):
                return 24

        d = dict()
        d[BadEq()] = 42
        self.assertRaises(KeyError, d.__getitem__, 23)

        class Exc(Exception): pass

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise Exc()
                else:
                    return 42

        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(Exc, d.__getitem__, x)

    def test_clear(self):
        d = dict({1:1, 2:2, 3:3})
        d.clear()
        self.assertEqual(d, {})

        self.assertRaises(TypeError, d.clear, None)

    def test_update(self):
        d = dict()
        d.update({1:100})
        d.update(dict({2:20}))
        d.update({1:1, 2:2, 3:3})
        self.assertEqual(d, {1:1, 2:2, 3:3})

        d.update()
        self.assertEqual(d, {1:1, 2:2, 3:3})

        self.assertRaises((TypeError, AttributeError), d.update, None)

        class SimpleUserDict:
            def __init__(self):
                self.d = dict({1:1, 2:2, 3:3})
            def keys(self):
                return self.d.keys()
            def __getitem__(self, i):
                return self.d[i]
        d.clear()
        d.update(SimpleUserDict())
        self.assertEqual(d, {1:1, 2:2, 3:3})

        class Exc(Exception): pass

        d.clear()
        class FailingUserDict:
            def keys(self):
                raise Exc
        self.assertRaises(Exc, d.update, FailingUserDict())

        class FailingUserDict:
            def keys(self):
                @implements_iterator
                class BogonIter:
                    def __init__(self):
                        self.i = 1
                    def __iter__(self):
                        return self
                    def __next__(self):
                        if self.i:
                            self.i = 0
                            return 'a'
                        raise Exc
                return BogonIter()
            def __getitem__(self, key):
                return key
        self.assertRaises(Exc, d.update, FailingUserDict())

        class FailingUserDict:
            def keys(self):
                @implements_iterator
                class BogonIter:
                    def __init__(self):
                        self.i = ord('a')
                    def __iter__(self):
                        return self
                    def __next__(self):
                        if self.i <= ord('z'):
                            rtn = chr(self.i)
                            self.i += 1
                            return rtn
                        raise StopIteration
                return BogonIter()
            def __getitem__(self, key):
                raise Exc
        self.assertRaises(Exc, d.update, FailingUserDict())

        @implements_iterator
        class badseq(object):
            def __iter__(self):
                return self
            def __next__(self):
                raise Exc()

        self.assertRaises(Exc, {}.update, badseq())

        self.assertRaises(ValueError, {}.update, [(1, 2, 3)])

    def test_fromkeys(self):
        self.assertEqual(dict.fromkeys('abc'), {'a':None, 'b':None, 'c':None})
        d = dict()
        self.assertIsNot(d.fromkeys('abc'), d)
        self.assertEqual(d.fromkeys('abc'), {'a':None, 'b':None, 'c':None})
        self.assertEqual(d.fromkeys((4,5),0), {4:0, 5:0})
        self.assertEqual(d.fromkeys([]), {})
        def g():
            yield 1
        self.assertEqual(d.fromkeys(g()), {1:None})
        self.assertRaises(TypeError, dict().fromkeys, 3)
        class dictlike(dict): pass
        self.assertEqual(dictlike.fromkeys('a'), {'a':None})
        self.assertEqual(dictlike().fromkeys('a'), {'a':None})
        self.assertIsInstance(dictlike.fromkeys('a'), dictlike)
        self.assertIsInstance(dictlike().fromkeys('a'), dictlike)
        # class mydict(dict):
        #     def __new__(cls):
        #         return UserDict.UserDict()
        # ud = mydict.fromkeys('ab')
        # self.assertEqual(ud, {'a':None, 'b':None})
        # self.assertIsInstance(ud, UserDict.UserDict)
        # self.assertRaises(TypeError, dict.fromkeys)

        class Exc(Exception): pass

        class baddict1(dict):
            def __init__(self):
                raise Exc()

        self.assertRaises(Exc, baddict1.fromkeys, [1])

        @implements_iterator
        class BadSeq(object):
            def __iter__(self):
                return self
            def __next__(self):
                raise Exc()

        self.assertRaises(Exc, dict.fromkeys, BadSeq())

        class baddict2(dict):
            def __setitem__(self, key, value):
                raise Exc()

        self.assertRaises(Exc, baddict2.fromkeys, [1])

        # test fast path for dictionary inputs
        d = dict(zip(range(6), range(6)))
        self.assertEqual(dict.fromkeys(d, 0), dict(zip(range(6), [0]*6)))

        class baddict3(dict):
            def __new__(cls):
                return d
        d = dict((i, i) for i in range(10))
        res = d.copy()
        res.update(a=None, b=None, c=None)
        # Was: self.assertEqual(baddict3.fromkeys(set(["a", "b", "c"])), res)
        # Infinite loop on Python 2.6 and 2.7 ...

    def test_copy(self):
        d = dict({1:1, 2:2, 3:3})
        self.assertEqual(d.copy(), {1:1, 2:2, 3:3})
        self.assertEqual({}.copy(), {})
        self.assertRaises(TypeError, d.copy, None)

    def test_get(self):
        d = dict()
        self.assertIs(d.get('c'), None)
        self.assertEqual(d.get('c', 3), 3)
        d = dict({'a': 1, 'b': 2})
        self.assertIs(d.get('c'), None)
        self.assertEqual(d.get('c', 3), 3)
        self.assertEqual(d.get('a'), 1)
        self.assertEqual(d.get('a', 3), 1)
        self.assertRaises(TypeError, d.get)
        self.assertRaises(TypeError, d.get, None, None, None)

    @skip26
    def test_setdefault(self):
        # dict.setdefault()
        d = dict()
        self.assertIs(d.setdefault('key0'), None)
        d.setdefault('key0', [])
        self.assertIs(d.setdefault('key0'), None)
        d.setdefault('key', []).append(3)
        self.assertEqual(d['key'][0], 3)
        d.setdefault('key', []).append(4)
        self.assertEqual(len(d['key']), 2)
        self.assertRaises(TypeError, d.setdefault)

        class Exc(Exception): pass

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise Exc()
                else:
                    return 42

        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(Exc, d.setdefault, x, [])

    @skip26
    def test_setdefault_atomic(self):
        # Issue #13521: setdefault() calls __hash__ and __eq__ only once.
        class Hashed(object):
            def __init__(self):
                self.hash_count = 0
                self.eq_count = 0
            def __hash__(self):
                self.hash_count += 1
                return 42
            def __eq__(self, other):
                self.eq_count += 1
                return id(self) == id(other)
        hashed1 = Hashed()
        y = dict({hashed1: 5})
        hashed2 = Hashed()
        y.setdefault(hashed2, [])
        self.assertEqual(hashed1.hash_count, 1)
        if PY3:
            self.assertEqual(hashed2.hash_count, 1)
            self.assertEqual(hashed1.eq_count + hashed2.eq_count, 1)

    def test_popitem(self):
        # dict.popitem()
        for copymode in -1, +1:
            # -1: b has same structure as a
            # +1: b is a.copy()
            for log2size in range(12):
                size = 2**log2size
                a = dict()
                b = dict()
                for i in range(size):
                    a[repr(i)] = i
                    if copymode < 0:
                        b[repr(i)] = i
                if copymode > 0:
                    b = a.copy()
                for i in range(size):
                    ka, va = ta = a.popitem()
                    self.assertEqual(va, int(ka))
                    kb, vb = tb = b.popitem()
                    self.assertEqual(vb, int(kb))
                    self.assertFalse(copymode < 0 and ta != tb)
                self.assertFalse(a)
                self.assertFalse(b)

        d = dict()
        self.assertRaises(KeyError, d.popitem)

    def test_pop(self):
        # Tests for pop with specified key
        d = dict()
        k, v = 'abc', 'def'
        d[k] = v
        self.assertRaises(KeyError, d.pop, 'ghi')

        self.assertEqual(d.pop(k), v)
        self.assertEqual(len(d), 0)

        self.assertRaises(KeyError, d.pop, k)

        self.assertEqual(d.pop(k, v), v)
        d[k] = v
        self.assertEqual(d.pop(k, 1), v)

        self.assertRaises(TypeError, d.pop)

        class Exc(Exception): pass

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise Exc()
                else:
                    return 42

        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(Exc, d.pop, x)

    def test_mutatingiteration(self):
        # changing dict size during iteration
        d = dict()
        d[1] = 1
        with self.assertRaises(RuntimeError):
            for i in d:
                d[i+1] = 1

    def test_repr(self):
        d = dict()
        self.assertEqual(repr(d), '{}')
        d[1] = 2
        self.assertEqual(repr(d), '{1: 2}')
        d = dict()
        d[1] = d
        self.assertEqual(repr(d), '{1: {...}}')

        class Exc(Exception): pass

        class BadRepr(object):
            def __repr__(self):
                raise Exc()

        d = dict({1: BadRepr()})
        self.assertRaises(Exc, repr, d)

    @unittest.skip('Comparing dicts for order has not been forward-ported')
    def test_le(self):
        self.assertFalse(dict() < {})
        self.assertFalse(dict() < dict())
        self.assertFalse(dict({1: 2}) < {1: 2})

        class Exc(Exception): pass

        class BadCmp(object):
            def __eq__(self, other):
                raise Exc()
            def __hash__(self):
                return 42

        d1 = dict({BadCmp(): 1})
        d2 = dict({1: 1})

        with self.assertRaises(Exc):
            d1 < d2

    @skip26
    def test_missing(self):
        # Make sure dict doesn't have a __missing__ method
        self.assertFalse(hasattr(dict, "__missing__"))
        self.assertFalse(hasattr(dict(), "__missing__"))
        # Test several cases:
        # (D) subclass defines __missing__ method returning a value
        # (E) subclass defines __missing__ method raising RuntimeError
        # (F) subclass sets __missing__ instance variable (no effect)
        # (G) subclass doesn't define __missing__ at a all
        class D(dict):
            def __missing__(self, key):
                return 42
        d = D({1: 2, 3: 4})
        self.assertEqual(d[1], 2)
        self.assertEqual(d[3], 4)
        self.assertNotIn(2, d)
        self.assertNotIn(2, d.keys())
        self.assertEqual(d[2], 42)

        class E(dict):
            def __missing__(self, key):
                raise RuntimeError(key)
        e = E()
        with self.assertRaises(RuntimeError) as c:
            e[42]
        self.assertEqual(c.exception.args, (42,))

        class F(dict):
            def __init__(self):
                # An instance variable __missing__ should have no effect
                self.__missing__ = lambda key: None
        f = F()
        with self.assertRaises(KeyError) as c:
            f[42]
        self.assertEqual(c.exception.args, (42,))

        class G(dict):
            pass
        g = G()
        with self.assertRaises(KeyError) as c:
            g[42]
        self.assertEqual(c.exception.args, (42,))

    @skip26
    def test_tuple_keyerror(self):
        # SF #1576657
        d = dict()
        with self.assertRaises(KeyError) as c:
            d[(1,)]
        self.assertEqual(c.exception.args, ((1,),))

    # def test_bad_key(self):
    #     # Dictionary lookups should fail if __cmp__() raises an exception.
    #     class CustomException(Exception):
    #         pass

    #     class BadDictKey:
    #         def __hash__(self):
    #             return hash(self.__class__)

    #         def __cmp__(self, other):
    #             if isinstance(other, self.__class__):
    #                 raise CustomException
    #             return other

    #     d = dict()
    #     x1 = BadDictKey()
    #     x2 = BadDictKey()
    #     d[x1] = 1
    #     for stmt in ['d[x2] = 2',
    #                  'z = d[x2]',
    #                  'x2 in d',
    #                  'd.has_key(x2)',
    #                  'd.get(x2)',
    #                  'd.setdefault(x2, 42)',
    #                  'd.pop(x2)',
    #                  'd.update({x2: 2})']:
    #         with self.assertRaises(CustomException):
    #             utils.exec_(stmt, locals())
    #
    # def test_resize1(self):
    #     # Dict resizing bug, found by Jack Jansen in 2.2 CVS development.
    #     # This version got an assert failure in debug build, infinite loop in
    #     # release build.  Unfortunately, provoking this kind of stuff requires
    #     # a mix of inserts and deletes hitting exactly the right hash codes in
    #     # exactly the right order, and I can't think of a randomized approach
    #     # that would be *likely* to hit a failing case in reasonable time.

    #     d = {}
    #     for i in range(5):
    #         d[i] = i
    #     for i in range(5):
    #         del d[i]
    #     for i in range(5, 9):  # i==8 was the problem
    #         d[i] = i

    # def test_resize2(self):
    #     # Another dict resizing bug (SF bug #1456209).
    #     # This caused Segmentation faults or Illegal instructions.

    #     class X(object):
    #         def __hash__(self):
    #             return 5
    #         def __eq__(self, other):
    #             if resizing:
    #                 d.clear()
    #             return False
    #     d = {}
    #     resizing = False
    #     d[X()] = 1
    #     d[X()] = 2
    #     d[X()] = 3
    #     d[X()] = 4
    #     d[X()] = 5
    #     # now trigger a resize
    #     resizing = True
    #     d[9] = 6

    # def test_empty_presized_dict_in_freelist(self):
    #     # Bug #3537: if an empty but presized dict with a size larger
    #     # than 7 was in the freelist, it triggered an assertion failure
    #     with self.assertRaises(ZeroDivisionError):
    #         d = {'a': 1 // 0, 'b': None, 'c': None, 'd': None, 'e': None,
    #              'f': None, 'g': None, 'h': None}
    #     d = {}

    # def test_container_iterator(self):
    #     # Bug #3680: tp_traverse was not implemented for dictiter objects
    #     class C(object):
    #         pass
    #     iterators = (dict.iteritems, dict.itervalues, dict.iterkeys)
    #     for i in iterators:
    #         obj = C()
    #         ref = weakref.ref(obj)
    #         container = {obj: 1}
    #         obj.x = i(container)
    #         del obj, container
    #         gc.collect()
    #         self.assertIs(ref(), None, "Cycle was not collected")

    # def _not_tracked(self, t):
    #     # Nested containers can take several collections to untrack
    #     gc.collect()
    #     gc.collect()
    #     self.assertFalse(gc.is_tracked(t), t)

    # def _tracked(self, t):
    #     self.assertTrue(gc.is_tracked(t), t)
    #     gc.collect()
    #     gc.collect()
    #     self.assertTrue(gc.is_tracked(t), t)

    # @test_support.cpython_only
    # def test_track_literals(self):
    #     # Test GC-optimization of dict literals
    #     x, y, z, w = 1.5, "a", (1, None), []

    #     self._not_tracked({})
    #     self._not_tracked({x:(), y:x, z:1})
    #     self._not_tracked({1: "a", "b": 2})
    #     self._not_tracked({1: 2, (None, True, False, ()): int})
    #     self._not_tracked({1: object()})

    #     # Dicts with mutable elements are always tracked, even if those
    #     # elements are not tracked right now.
    #     self._tracked({1: []})
    #     self._tracked({1: ([],)})
    #     self._tracked({1: {}})
    #     self._tracked({1: set()})

    # @test_support.cpython_only
    # def test_track_dynamic(self):
    #     # Test GC-optimization of dynamically-created dicts
    #     class MyObject(object):
    #         pass
    #     x, y, z, w, o = 1.5, "a", (1, object()), [], MyObject()

    #     d = dict()
    #     self._not_tracked(d)
    #     d[1] = "a"
    #     self._not_tracked(d)
    #     d[y] = 2
    #     self._not_tracked(d)
    #     d[z] = 3
    #     self._not_tracked(d)
    #     self._not_tracked(d.copy())
    #     d[4] = w
    #     self._tracked(d)
    #     self._tracked(d.copy())
    #     d[4] = None
    #     self._not_tracked(d)
    #     self._not_tracked(d.copy())

    #     # dd isn't tracked right now, but it may mutate and therefore d
    #     # which contains it must be tracked.
    #     d = dict()
    #     dd = dict()
    #     d[1] = dd
    #     self._not_tracked(dd)
    #     self._tracked(d)
    #     dd[1] = d
    #     self._tracked(dd)

    #     d = dict.fromkeys([x, y, z])
    #     self._not_tracked(d)
    #     dd = dict()
    #     dd.update(d)
    #     self._not_tracked(dd)
    #     d = dict.fromkeys([x, y, z, o])
    #     self._tracked(d)
    #     dd = dict()
    #     dd.update(d)
    #     self._tracked(dd)

    #     d = dict(x=x, y=y, z=z)
    #     self._not_tracked(d)
    #     d = dict(x=x, y=y, z=z, w=w)
    #     self._tracked(d)
    #     d = dict()
    #     d.update(x=x, y=y, z=z)
    #     self._not_tracked(d)
    #     d.update(w=w)
    #     self._tracked(d)

    #     d = dict([(x, y), (z, 1)])
    #     self._not_tracked(d)
    #     d = dict([(x, y), (z, w)])
    #     self._tracked(d)
    #     d = dict()
    #     d.update([(x, y), (z, 1)])
    #     self._not_tracked(d)
    #     d.update([(x, y), (z, w)])
    #     self._tracked(d)

    # @test_support.cpython_only
    # def test_track_subtypes(self):
    #     # Dict subtypes are always tracked
    #     class MyDict(dict):
    #         pass
    #     self._tracked(MyDict())


if __name__ == '__main__':
    # Only run these tests on Python 3 ...
    if PY3:
        unittest.main()

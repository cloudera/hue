"""
Tests to make sure the newobject object (which defines Python 2-compatible
``__unicode__`` and ``next`` methods) is working.
"""

from __future__ import absolute_import, division
from future import utils
from future.builtins import object, str, next, int, super
from future.utils import implements_iterator, python_2_unicode_compatible
from future.tests.base import unittest, expectedFailurePY2


class TestNewObject(unittest.TestCase):
    def test_object_implements_py2_unicode_method(self):
        my_unicode_str = u'Unicode string: \u5b54\u5b50'
        class A(object):
            def __str__(self):
                return my_unicode_str
        a = A()
        self.assertEqual(len(str(a)), 18)
        if utils.PY2:
            self.assertTrue(hasattr(a, '__unicode__'))
        else:
            self.assertFalse(hasattr(a, '__unicode__'))
        self.assertEqual(str(a), my_unicode_str)
        self.assertTrue(isinstance(str(a).encode('utf-8'), bytes))
        if utils.PY2:
            self.assertTrue(type(unicode(a)) == unicode)
            self.assertEqual(unicode(a), my_unicode_str)

        # Manual equivalent on Py2 without the decorator:
        if not utils.PY3:
            class B(object):
                def __unicode__(self):
                    return u'Unicode string: \u5b54\u5b50'
                def __str__(self):
                    return unicode(self).encode('utf-8')
            b = B()
            assert str(a) == str(b)

    def test_implements_py2_iterator(self):
        
        class Upper(object):
            def __init__(self, iterable):
                self._iter = iter(iterable)
            def __next__(self):                 # note the Py3 interface
                return next(self._iter).upper()
            def __iter__(self):
                return self

        self.assertEqual(list(Upper('hello')), list('HELLO'))

        # Try combining it with the next() function:

        class MyIter(object):
            def __next__(self):
                return 'Next!'
            def __iter__(self):
                return self
        
        itr = MyIter()
        self.assertEqual(next(itr), 'Next!')

        itr2 = MyIter()
        for i, item in enumerate(itr2):
            if i >= 10:
                break
            self.assertEqual(item, 'Next!')

    def test_implements_py2_nonzero(self):
        
        class EvenIsTrue(object):
            """
            An integer that evaluates to True if even.
            """
            def __init__(self, my_int):
                self.my_int = my_int
            def __bool__(self):
                return self.my_int % 2 == 0
            def __add__(self, other):
                return type(self)(self.my_int + other)

        k = EvenIsTrue(5)
        self.assertFalse(k)
        self.assertFalse(bool(k))
        self.assertTrue(k + 1)
        self.assertTrue(bool(k + 1))
        self.assertFalse(k + 2)


    def test_int_implements_py2_nonzero(self):
        """
        Tests whether the newint object provides a __nonzero__ method that
        maps to __bool__ in case the user redefines __bool__ in a subclass of
        newint.
        """
        
        class EvenIsTrue(int):
            """
            An integer that evaluates to True if even.
            """
            def __bool__(self):
                return self % 2 == 0
            def __add__(self, other):
                val = super().__add__(other)
                return type(self)(val)

        k = EvenIsTrue(5)
        self.assertFalse(k)
        self.assertFalse(bool(k))
        self.assertTrue(k + 1)
        self.assertTrue(bool(k + 1))
        self.assertFalse(k + 2)

    def test_non_iterator(self):
        """
        The default behaviour of next(o) for a newobject o should be to raise a
        TypeError, as with the corresponding builtin object.
        """
        o = object()
        with self.assertRaises(TypeError):
            next(o)

    def test_bool_empty_object(self):
        """
        The default result of bool(newobject()) should be True, as with builtin
        objects.
        """
        o = object()
        self.assertTrue(bool(o))

        class MyClass(object):
            pass

        obj = MyClass()
        self.assertTrue(bool(obj))

    def test_isinstance_object_subclass(self):
        """
        This was failing before 
        """
        class A(object):
            pass
        a = A()

        class B(object):
            pass
        b = B()

        self.assertFalse(isinstance(a, B))
        self.assertFalse(isinstance(b, A))
        self.assertTrue(isinstance(a, A))
        self.assertTrue(isinstance(b, B))

        class C(A):
            pass
        c = C()

        self.assertTrue(isinstance(c, A))
        self.assertFalse(isinstance(c, B))
        self.assertFalse(isinstance(a, C))
        self.assertFalse(isinstance(b, C))
        self.assertTrue(isinstance(c, C))

    @expectedFailurePY2
    def test_types_isinstance_newobject(self):
        a = list()
        b = dict()
        c = set()
        self.assertTrue(isinstance(a, object))
        self.assertTrue(isinstance(b, object))
        self.assertTrue(isinstance(c, object))

        # Old-style class instances on Py2 should still report as an instance
        # of object as usual on Py2:
        class D:
            pass
        d = D()
        self.assertTrue(isinstance(d, object))

        e = object()
        self.assertTrue(isinstance(e, object))

        class F(object):
            pass
        f = F()
        self.assertTrue(isinstance(f, object))

        class G(F):
            pass
        g = G()
        self.assertTrue(isinstance(g, object))

        class H():
            pass
        h = H()
        self.assertTrue(isinstance(h, object))

    def test_long_special_method(self):
        class A(object):
            def __int__(self):
                return 0
        a = A()
        self.assertEqual(int(a), 0)
        if utils.PY2:
            self.assertEqual(long(a), 0)

    def test_multiple_inheritance(self):
        """
        Issue #96
        """
        import collections

        class Base(object):
            pass

        class Foo(Base, collections.Container):
            def __contains__(self, item):
                return False

    def test_with_metaclass_and_object(self):
        """
        Issue #91
        """
        from future.utils import with_metaclass

        class MetaClass(type):
            pass

        class TestClass(with_metaclass(MetaClass, object)):
            pass

    def test_bool(self):
        """
        Issue #211
        """
        from builtins import object

        class ResultSet(object):
            def __len__(self):
                return 0

        self.assertTrue(bool(ResultSet()) is False)

        class ResultSet(object):
            def __len__(self):
                return 2

        self.assertTrue(bool(ResultSet()) is True)

    def test_bool2(self):
        """
        If __bool__ is defined, the presence or absence of __len__ should
        be irrelevant.
        """
        from builtins import object

        class TrueThing(object):
            def __bool__(self):
                return True
            def __len__(self):
                raise RuntimeError('__len__ should not be called')

        self.assertTrue(bool(TrueThing()))

        class FalseThing(object):
            def __bool__(self):
                return False
            def __len__(self):
                raise RuntimeError('__len__ should not be called')

        self.assertFalse(bool(FalseThing()))


if __name__ == '__main__':
    unittest.main()

"""
Tests to make sure the decorators (implements_iterator and
python2_unicode_compatible) are working.
"""

from __future__ import absolute_import, division
from future import utils
from future.builtins import *
from future.utils import implements_iterator, python_2_unicode_compatible
from future.tests.base import unittest


class TestDecorators(unittest.TestCase):
    def test_python_2_unicode_compatible_decorator(self):
        my_unicode_str = u'Unicode string: \u5b54\u5b50'
        # With the decorator:
        @python_2_unicode_compatible
        class A(object):
            def __str__(self):
                return my_unicode_str
        a = A()
        assert len(str(a)) == 18
        if not utils.PY3:
            assert hasattr(a, '__unicode__')
        self.assertEqual(str(a), my_unicode_str)
        self.assertTrue(isinstance(str(a).encode('utf-8'), bytes))

        # Manual equivalent on Py2 without the decorator:
        if not utils.PY3:
            class B(object):
                def __unicode__(self):
                    return u'Unicode string: \u5b54\u5b50'
                def __str__(self):
                    return unicode(self).encode('utf-8')
            b = B()
            assert str(a) == str(b)

    def test_implements_iterator(self):

        @implements_iterator
        class MyIter(object):
            def __next__(self):
                return 'Next!'
            def __iter__(self):
                return self

        itr = MyIter()
        self.assertEqual(next(itr), 'Next!')

        itr2 = MyIter()
        for i, item in enumerate(itr2):
            if i >= 3:
                break
            self.assertEqual(item, 'Next!')

if __name__ == '__main__':
    unittest.main()

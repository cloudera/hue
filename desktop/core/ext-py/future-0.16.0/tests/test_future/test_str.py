# -*- coding: utf-8 -*-
"""
Tests for the backported class:`str` class.
"""

from __future__ import absolute_import, unicode_literals, print_function
from future.builtins import *
from future import utils
from future.tests.base import unittest, expectedFailurePY2

import os

TEST_UNICODE_STR = u'ℝεα∂@ßʟ℮ ☂ℯṧт υηḯ¢☺ḓ℮'


class TestStr(unittest.TestCase):
    def test_str(self):
        self.assertFalse(str is bytes)
        self.assertEqual(str('blah'), u'blah')  # u'' prefix: Py3.3 and Py2 only
        self.assertEqual(str(b'1234'), "b'1234'")

    def test_bool_str(self):
        s1 = str(u'abc')
        s2 = u'abc'
        s3 = str(u'')
        s4 = u''
        self.assertEqual(bool(s1), bool(s2))
        self.assertEqual(bool(s3), bool(s4))

    def test_os_path_join(self):
        """
        Issue #15: can't os.path.join(u'abc', str(u'def'))
        """
        self.assertEqual(os.path.join(u'abc', str(u'def')),
                         u'abc{0}def'.format(os.sep))

    def test_str_encode_utf8(self):
        b = str(TEST_UNICODE_STR).encode('utf-8')
        self.assertTrue(isinstance(b, bytes))
        self.assertFalse(isinstance(b, str))
        s = b.decode('utf-8')
        self.assertTrue(isinstance(s, str))
        self.assertEqual(s, TEST_UNICODE_STR)

    def test_str_encode_cp1251(self):
        b1 = b'\xcd\xeb\xff'
        s1 = str(b1, 'cp1251')
        self.assertEqual(s1, u'Нля')

        b2 = bytes(b'\xcd\xeb\xff')
        s2 = str(b2, 'cp1251')
        self.assertEqual(s2, u'Нля')

    def test_str_encode_decode_with_py2_str_arg(self):
        # Try passing a standard Py2 string (as if unicode_literals weren't imported)
        b = str(TEST_UNICODE_STR).encode(utils.bytes_to_native_str(b'utf-8'))
        self.assertTrue(isinstance(b, bytes))
        self.assertFalse(isinstance(b, str))
        s = b.decode(utils.bytes_to_native_str(b'utf-8'))
        self.assertTrue(isinstance(s, str))
        self.assertEqual(s, TEST_UNICODE_STR)

    def test_str_encode_decode_big5(self):
        a = u'Unicode string: \u5b54\u5b50'
        self.assertEqual(str(a), a.encode('big5').decode('big5'))

    def test_str_empty(self):
        """
        str() -> u''
        """
        self.assertEqual(str(), u'')

    def test_str_iterable_of_ints(self):
        self.assertEqual(str([65, 66, 67]), '[65, 66, 67]')
        self.assertNotEqual(str([65, 66, 67]), 'ABC')

    def test_str_str(self):
        self.assertEqual(str('ABC'), u'ABC')
        self.assertEqual(str('ABC'), 'ABC')

    def test_str_is_str(self):
        s = str(u'ABC')
        self.assertTrue(str(s) is s)
        self.assertEqual(repr(str(s)), "'ABC'")

    def test_str_fromhex(self):
        self.assertFalse(hasattr(str, 'fromhex'))

    def test_str_hasattr_decode(self):
        """
        This test tests whether hasattr(s, 'decode') is False, like it is on Py3.

        Sometimes code (such as http.client in Py3.3) checks hasattr(mystring,
        'decode') to determine if a string-like thing needs encoding. It would
        be nice to have this return False so the string can be treated on Py2
        like a Py3 string.
        """
        s = str(u'abcd')
        self.assertFalse(hasattr(s, 'decode'))
        self.assertTrue(hasattr(s, 'encode'))

    def test_isinstance_str(self):
        self.assertTrue(isinstance(str('blah'), str))

    def test_isinstance_str_subclass(self):
        """
        Issue #89
        """
        value = str(u'abc')
        class Magic(str):
            pass
        self.assertTrue(isinstance(value, str))
        self.assertFalse(isinstance(value, Magic))

    def test_str_getitem(self):
        s = str('ABCD')
        self.assertNotEqual(s[0], 65)
        self.assertEqual(s[0], 'A')
        self.assertEqual(s[-1], 'D')
        self.assertEqual(s[0:1], 'A')
        self.assertEqual(s[:], u'ABCD')

    @unittest.expectedFailure
    def test_u_literal_creates_newstr_object(self):
        """
        It would nice if the u'' or '' literal syntax could be coaxed
        into producing our new str objects somehow ...
        """
        s = u'ABCD'
        self.assertTrue(isinstance(s, str))
        self.assertFalse(repr(b).startswith('b'))

    def test_repr(self):
        s = str('ABCD')
        self.assertFalse(repr(s).startswith('b'))

    def test_str(self):
        b = str('ABCD')
        self.assertTrue(str(b), 'ABCD')

    def test_str_setitem(self):
        s = 'ABCD'
        with self.assertRaises(TypeError):
            s[0] = b'B'

    def test_str_iteration(self):
        s = str('ABCD')
        for item in s:
            self.assertFalse(isinstance(item, int))
            self.assertTrue(isinstance(item, str))
        self.assertNotEqual(list(s), [65, 66, 67, 68])
        self.assertEqual(list(s), ['A', 'B', 'C', 'D'])

    def test_str_plus_bytes(self):
        s = str(u'ABCD')
        b = b'EFGH'
        # We allow this now:
        # with self.assertRaises(TypeError):
        #     s + b
        # str objects don't have an __radd__ method, so the following
        # does not raise a TypeError. Is this a problem?
        # with self.assertRaises(TypeError):
        #     b + s

        # Now with our custom bytes object:
        b2 = bytes(b'EFGH')
        with self.assertRaises(TypeError):
            s + b2
        with self.assertRaises(TypeError):
            b2 + s

    def test_str_plus_str(self):
        s1 = str('ABCD')
        s2 = s1 + s1
        self.assertEqual(s2, u'ABCDABCD')
        self.assertTrue(isinstance(s2, str))

        s3 = s1 + u'ZYXW'
        self.assertEqual(s3, 'ABCDZYXW')
        self.assertTrue(isinstance(s3, str))

        s4 = 'ZYXW' + s1
        self.assertEqual(s4, 'ZYXWABCD')
        self.assertTrue(isinstance(s4, str))

    def test_str_join_str(self):
        s = str(' * ')
        strings = ['AB', 'EFGH', 'IJKL', TEST_UNICODE_STR]
        result = s.join(strings)
        self.assertEqual(result, 'AB * EFGH * IJKL * ' + TEST_UNICODE_STR)
        self.assertTrue(isinstance(result, str))

    def test_str_join_bytes(self):
        s = str('ABCD')
        byte_strings1 = [b'EFGH', u'IJKL']
        # We allow this on Python 2 for compatibility with old libraries:
        if utils.PY2:
            self.assertEqual(s.join(byte_strings1), u'EFGHABCDIJKL')

        byte_strings2 = [bytes(b'EFGH'), u'IJKL']
        with self.assertRaises(TypeError):
            s.join(byte_strings2)

    def test_str_join_staticmethod(self):
        """
        Issue #33
        """
        c = str.join('-', ['a', 'b'])
        self.assertEqual(c, 'a-b')
        self.assertEqual(type(c), str)

    def test_str_join_staticmethod_workaround_1(self):
        """
        Issue #33
        """
        c = str('-').join(['a', 'b'])
        self.assertEqual(c, 'a-b')
        self.assertEqual(type(c), str)

    def test_str_join_staticmethod_workaround_2(self):
        """
        Issue #33
        """
        c = str.join(str('-'), ['a', 'b'])
        self.assertEqual(c, 'a-b')
        self.assertEqual(type(c), str)

    def test_str_replace(self):
        s = str('ABCD')
        c = s.replace('A', 'F')
        self.assertEqual(c, 'FBCD')
        self.assertTrue(isinstance(c, str))

        with self.assertRaises(TypeError):
            s.replace(bytes(b'A'), u'F')
        with self.assertRaises(TypeError):
            s.replace(u'A', bytes(b'F'))

    def test_str_partition(self):
        s1 = str('ABCD')
        parts = s1.partition('B')
        self.assertEqual(parts, ('A', 'B', 'CD'))
        self.assertTrue(all([isinstance(p, str) for p in parts]))

        s2 = str('ABCDABCD')
        parts = s2.partition('B')
        self.assertEqual(parts, ('A', 'B', 'CDABCD'))

    def test_str_rpartition(self):
        s2 = str('ABCDABCD')
        parts = s2.rpartition('B')
        self.assertEqual(parts, ('ABCDA', 'B', 'CD'))
        self.assertTrue(all([isinstance(p, str) for p in parts]))

    def test_str_contains_something(self):
        s = str('ABCD')
        self.assertTrue('A' in s)
        if utils.PY2:
            self.assertTrue(b'A' in s)
        with self.assertRaises(TypeError):
            bytes(b'A') in s                  
        with self.assertRaises(TypeError):
            65 in s                                 # unlike bytes

        self.assertTrue('AB' in s)
        self.assertFalse(str([65, 66]) in s)        # unlike bytes
        self.assertFalse('AC' in s)
        self.assertFalse('Z' in s)

    def test_str_index(self):
        s = str('ABCD')
        self.assertEqual(s.index('B'), 1)
        with self.assertRaises(TypeError):
            s.index(67)
        with self.assertRaises(TypeError):
            s.index(bytes(b'C'))

    def test_startswith(self):
        s = str('abcd')
        self.assertTrue(s.startswith('a'))
        self.assertTrue(s.startswith(('a', 'd')))
        self.assertTrue(s.startswith(str('ab')))
        if utils.PY2:
            # We allow this, because e.g. Python 2 os.path.join concatenates
            # its arg with a byte-string '/' indiscriminately.
            self.assertFalse(s.startswith(b'A'))
            self.assertTrue(s.startswith(b'a'))
        with self.assertRaises(TypeError) as cm:
            self.assertFalse(s.startswith(bytes(b'A')))
        with self.assertRaises(TypeError) as cm:
            s.startswith((bytes(b'A'), bytes(b'B')))
        with self.assertRaises(TypeError) as cm:
            s.startswith(65)

    def test_join(self):
        sep = str('-')
        self.assertEqual(sep.join('abcd'), 'a-b-c-d')
        if utils.PY2:
            sep.join(b'abcd')
        with self.assertRaises(TypeError) as cm:
            sep.join(bytes(b'abcd'))

    def test_endswith(self):
        s = str('abcd')
        self.assertTrue(s.endswith('d'))
        self.assertTrue(s.endswith(('b', 'd')))
        self.assertTrue(s.endswith(str('cd')))
        self.assertFalse(s.endswith(('A', 'B')))
        if utils.PY2:
            self.assertFalse(s.endswith(b'D'))
            self.assertTrue(s.endswith((b'D', b'd')))
        with self.assertRaises(TypeError) as cm:
            s.endswith(65)
        with self.assertRaises(TypeError) as cm:
            s.endswith((bytes(b'D'),))

    def test_split(self):
        s = str('ABCD')
        self.assertEqual(s.split('B'), ['A', 'CD'])
        if utils.PY2:
            self.assertEqual(s.split(b'B'), ['A', 'CD'])
        with self.assertRaises(TypeError) as cm:
            s.split(bytes(b'B'))

    def test_rsplit(self):
        s = str('ABCD')
        self.assertEqual(s.rsplit('B'), ['A', 'CD'])
        if utils.PY2:
            self.assertEqual(s.rsplit(b'B'), ['A', 'CD'])
        with self.assertRaises(TypeError) as cm:
            s.rsplit(bytes(b'B'))

    def test_eq_bytes(self):
        s = str('ABCD')
        b = bytes(b'ABCD')
        self.assertNotEqual(s, b)
        self.assertNotEqual(str(''), bytes(b''))
        native_s = 'ABCD'
        native_b = b'ABCD'
        self.assertFalse(b == native_s)
        self.assertTrue(b != native_s)

        # Fails on Py2:
        # self.assertNotEqual(native_s, b)
        # with no obvious way to change this.

        # For backward compatibility with broken string-handling code in
        # Py2 libraries, we allow the following:

        if utils.PY2:
            self.assertTrue(native_b == s)
            self.assertFalse(s != native_b)

    def test_eq(self):
        s = str('ABCD')
        self.assertEqual('ABCD', s)
        self.assertEqual(s, 'ABCD')
        self.assertEqual(s, s)
        self.assertTrue(u'ABCD' == s)
        if utils.PY2:
            self.assertTrue(b'ABCD' == s)
        else:
            self.assertFalse(b'ABCD' == s)
        self.assertFalse(bytes(b'ABCD') == s)

    def test_ne(self):
        s = str('ABCD')
        self.assertNotEqual('A', s)
        self.assertNotEqual(s, 'A')
        self.assertNotEqual(s, 5)
        self.assertNotEqual(2.7, s)
        self.assertNotEqual(s, ['A', 'B', 'C', 'D'])
        if utils.PY2:
            self.assertFalse(b'ABCD' != s)
        else:
            self.assertTrue(b'ABCD' != s)
        self.assertTrue(bytes(b'ABCD') != s)

    def test_cmp(self):
        s = str(u'ABC')
        with self.assertRaises(TypeError):
            s > 3
        with self.assertRaises(TypeError):
            s < 1000
        with self.assertRaises(TypeError):
            s > b'XYZ'
        with self.assertRaises(TypeError):
            s < b'XYZ'
        with self.assertRaises(TypeError):
            s <= 3
        with self.assertRaises(TypeError):
            s >= int(3)
        with self.assertRaises(TypeError):
            s < 3.3
        with self.assertRaises(TypeError):
            s > (3.3 + 3j)
        with self.assertRaises(TypeError):
            s >= (1, 2)
        with self.assertRaises(TypeError):
            s <= [1, 2]

    def test_mul(self):
        s = str(u'ABC')
        c = s * 4
        self.assertTrue(isinstance(c, str))
        self.assertEqual(c, u'ABCABCABCABC')
        d = s * int(4)
        self.assertTrue(isinstance(d, str))
        self.assertEqual(d, u'ABCABCABCABC')
        if utils.PY2:
            e = s * long(4)
            self.assertTrue(isinstance(e, str))
            self.assertEqual(e, u'ABCABCABCABC')
        with self.assertRaises(TypeError):
            s * 3.3
        with self.assertRaises(TypeError):
            s * (3.3 + 3j)

    def test_rmul(self):
        s = str(u'XYZ')
        c = 3 * s
        self.assertTrue(isinstance(c, str))
        self.assertEqual(c, u'XYZXYZXYZ')
        d = s * int(3)
        self.assertTrue(isinstance(d, str))
        self.assertEqual(d, u'XYZXYZXYZ')
        if utils.PY2:
            e = long(3) * s
            self.assertTrue(isinstance(e, str))
            self.assertEqual(e, u'XYZXYZXYZ')
        with self.assertRaises(TypeError):
            3.3 * s
        with self.assertRaises(TypeError):
            (3.3 + 3j) * s

    @unittest.skip('Fails on Python <= 2.7.6 due to string subclass slicing bug')
    def test_slice(self):
        """
        Do slices return newstr objects?
        """
        s = str(u'abcd')
        self.assertEqual(s[:2], u'ab')
        self.assertEqual(type(s[:2]), str)
        self.assertEqual(s[-2:], u'cd')
        self.assertEqual(type(s[-2:]), str)

    @unittest.skip('Fails on Python <= 2.7.6 due to string subclass slicing bug')
    def test_subclassing(self):
        """
        Can newstr be subclassed and do str methods then return instances of
        the same class? (This is the Py3 behaviour).
        """
        class SubClass(str):
            pass
        s = SubClass(u'abcd')
        self.assertEqual(type(s), SubClass)
        self.assertEqual(type(s + s), str)
        self.assertEqual(type(s[0]), str)
        self.assertEqual(type(s[:2]), str)
        self.assertEqual(type(s.join([u'_', u'_', u'_'])), str)

    def test_subclassing_2(self):
        """
        Tests __new__ method in subclasses. Fails in versions <= 0.11.4
        """
        class SubClass(str):
            def __new__(cls, *args, **kwargs):
                self = str.__new__(cls, *args, **kwargs)
                assert type(self) == SubClass
                return self
        s = SubClass(u'abcd')
        self.assertTrue(True)

    # From Python 3.3: test_unicode.py
    def checkequalnofix(self, result, object, methodname, *args):
        method = getattr(object, methodname)
        realresult = method(*args)
        self.assertEqual(realresult, result)
        self.assertTrue(type(realresult) is type(result))

        # if the original is returned make sure that
        # this doesn't happen with subclasses
        if realresult is object:
            class usub(str):
                def __repr__(self):
                    return 'usub(%r)' % str.__repr__(self)
            object = usub(object)
            method = getattr(object, methodname)
            realresult = method(*args)
            self.assertEqual(realresult, result)
            self.assertTrue(object is not realresult)

    type2test = str

    def test_maketrans_translate(self):
        # these work with plain translate()
        self.checkequalnofix('bbbc', 'abababc', 'translate',
                             {ord('a'): None})
        self.checkequalnofix('iiic', 'abababc', 'translate',
                             {ord('a'): None, ord('b'): ord('i')})
        self.checkequalnofix('iiix', 'abababc', 'translate',
                             {ord('a'): None, ord('b'): ord('i'), ord('c'): 'x'})
        self.checkequalnofix('c', 'abababc', 'translate',
                             {ord('a'): None, ord('b'): ''})
        self.checkequalnofix('xyyx', 'xzx', 'translate',
                             {ord('z'): 'yy'})
        # this needs maketrans()
        self.checkequalnofix('abababc', 'abababc', 'translate',
                             {'b': '<i>'})
        tbl = self.type2test.maketrans({'a': None, 'b': '<i>'})
        self.checkequalnofix('<i><i><i>c', 'abababc', 'translate', tbl)
        # test alternative way of calling maketrans()
        tbl = self.type2test.maketrans('abc', 'xyz', 'd')
        self.checkequalnofix('xyzzy', 'abdcdcbdddd', 'translate', tbl)

        self.assertRaises(TypeError, self.type2test.maketrans)
        self.assertRaises(ValueError, self.type2test.maketrans, 'abc', 'defg')
        self.assertRaises(TypeError, self.type2test.maketrans, 2, 'def')
        self.assertRaises(TypeError, self.type2test.maketrans, 'abc', 2)
        self.assertRaises(TypeError, self.type2test.maketrans, 'abc', 'def', 2)
        self.assertRaises(ValueError, self.type2test.maketrans, {'xy': 2})
        self.assertRaises(TypeError, self.type2test.maketrans, {(1,): 2})

        self.assertRaises(TypeError, 'hello'.translate)
        self.assertRaises(TypeError, 'abababc'.translate, 'abc', 'xyz')

    @expectedFailurePY2
    def test_multiple_inheritance(self):
        """
        Issue #96 (for newstr instead of newobject)
        """
        import collections

        class Base(str):
            pass

        class Foo(Base, collections.Container):
            def __contains__(self, item):
                return False

    @expectedFailurePY2
    def test_with_metaclass_and_str(self):
        """
        Issue #91 (for newstr instead of newobject)
        """
        from future.utils import with_metaclass

        class MetaClass(type):
            pass

        class TestClass(with_metaclass(MetaClass, str)):
            pass

    def test_surrogateescape_encoding(self):
        """
        Tests whether surrogateescape encoding works correctly.
        """
        pairs = [(u'\udcc3', b'\xc3'),
                 (u'\udcff', b'\xff')]

        for (s, b) in pairs:
            encoded = str(s).encode('utf-8', 'surrogateescape')
            self.assertEqual(b, encoded)
            self.assertTrue(isinstance(encoded, bytes))
            self.assertEqual(s, encoded.decode('utf-8', 'surrogateescape'))


if __name__ == '__main__':
    unittest.main()

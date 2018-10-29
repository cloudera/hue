# -*- coding: utf-8 -*-
"""
Tests for the backported bytes object
"""

from __future__ import absolute_import, unicode_literals, print_function
from future.builtins import *
from future import utils

from numbers import Integral
from future.tests.base import unittest, expectedFailurePY2


TEST_UNICODE_STR = u'ℝεα∂@ßʟ℮ ☂ℯṧт υηḯ¢☺ḓ℮'
# Tk icon as a .gif:
TEST_BYTE_STR = b'GIF89a\x0e\x00\x0b\x00\x80\xff\x00\xff\x00\x00\xc0\xc0\xc0!\xf9\x04\x01\x00\x00\x01\x00,\x00\x00\x00\x00\x0e\x00\x0b\x00@\x02\x1f\x0c\x8e\x10\xbb\xcan\x90\x99\xaf&\xd8\x1a\xce\x9ar\x06F\xd7\xf1\x90\xa1c\x9e\xe8\x84\x99\x89\x97\xa2J\x01\x00;\x1a\x14\x00;;\xba\nD\x14\x00\x00;;'


class TestBytes(unittest.TestCase):
    def test_bytes_encoding_arg(self):
        """
        The bytes class has changed in Python 3 to accept an
        additional argument in the constructor: encoding.

        It would be nice to support this without breaking the
        isinstance(..., bytes) test below.
        """
        u = u'Unicode string: \u5b54\u5b50'
        b = bytes(u, encoding='utf-8')
        self.assertEqual(b, u.encode('utf-8'))

        nu = str(u)
        b = bytes(nu, encoding='utf-8')
        self.assertEqual(b, u.encode('utf-8'))

    def test_bytes_encoding_arg_issue_193(self):
        """
        This used to be True: bytes(str(u'abc'), 'utf8') == b"b'abc'"
        """
        u = u'abc'
        b = bytes(str(u), 'utf8')
        self.assertNotEqual(b, b"b'abc'")
        self.assertEqual(b, b'abc')
        self.assertEqual(b, bytes(b'abc'))

    def test_bytes_encoding_arg_non_kwarg(self):
        """
        As above, but with a positional argument
        """
        u = u'Unicode string: \u5b54\u5b50'
        b = bytes(u, 'utf-8')
        self.assertEqual(b, u.encode('utf-8'))

        nu = str(u)
        b = bytes(nu, 'utf-8')
        self.assertEqual(b, u.encode('utf-8'))

    def test_bytes_string_no_encoding(self):
        with self.assertRaises(TypeError):
            bytes(u'ABC')

    def test_bytes_int(self):
        """
        In Py3, bytes(int) -> bytes object of size given by the parameter initialized with null
        """
        self.assertEqual(bytes(5), b'\x00\x00\x00\x00\x00')
        # Test using newint:
        self.assertEqual(bytes(int(5)), b'\x00\x00\x00\x00\x00')
        self.assertTrue(isinstance(bytes(int(5)), bytes))

        # Negative counts are not allowed in Py3:
        with self.assertRaises(ValueError):
            bytes(-1)
        with self.assertRaises(ValueError):
            bytes(int(-1))

    @unittest.skipIf(utils.PY3, 'test not needed on Py3: all ints are long')
    def test_bytes_long(self):
        """
        As above, but explicitly feeding in a long on Py2. Note that
        checks like:
            isinstance(n, int)
        are fragile on Py2, because isinstance(10L, int) is False.
        """
        m = long(5)
        n = long(-1)
        self.assertEqual(bytes(m), b'\x00\x00\x00\x00\x00')
        # Negative counts are not allowed in Py3:
        with self.assertRaises(ValueError):
            bytes(n)

    def test_bytes_empty(self):
        """
        bytes() -> b''
        """
        self.assertEqual(bytes(), b'')

    def test_bytes_iterable_of_ints(self):
        self.assertEqual(bytes([65, 66, 67]), b'ABC')
        self.assertEqual(bytes([int(120), int(121), int(122)]), b'xyz')

    def test_bytes_bytes(self):
        self.assertEqual(bytes(b'ABC'), b'ABC')

    def test_bytes_is_bytes(self):
        b = bytes(b'ABC')
        self.assertTrue(bytes(b) is b)
        self.assertEqual(repr(bytes(b)), "b'ABC'")

    def test_bytes_fromhex(self):
        self.assertEqual(bytes.fromhex('bb 0f'), b'\xbb\x0f')
        self.assertEqual(bytes.fromhex('1234'), b'\x124')
        self.assertEqual(bytes.fromhex('12ffa0'), b'\x12\xff\xa0')
        b = b'My bytestring'
        self.assertEqual(bytes(b).fromhex('bb 0f'), b'\xbb\x0f')

    def test_isinstance_bytes(self):
        self.assertTrue(isinstance(bytes(b'blah'), bytes))

    def test_isinstance_bytes_subclass(self):
        """
        Issue #89
        """
        value = bytes(b'abc')
        class Magic(bytes):
            pass
        self.assertTrue(isinstance(value, bytes))
        self.assertFalse(isinstance(value, Magic))

    def test_isinstance_oldbytestrings_bytes(self):
        """
        Watch out for this. Byte-strings produced in various places in Py2
        are of type 'str'. With 'from future.builtins import bytes', 'bytes'
        is redefined to be a subclass of 'str', not just an alias for 'str'.
        """
        self.assertTrue(isinstance(b'blah', bytes))   # not with the redefined bytes obj
        self.assertTrue(isinstance(u'blah'.encode('utf-8'), bytes))   # not with the redefined bytes obj

    def test_bytes_getitem(self):
        b = bytes(b'ABCD')
        self.assertEqual(b[0], 65)
        self.assertEqual(b[-1], 68)
        self.assertEqual(b[0:1], b'A')
        self.assertEqual(b[:], b'ABCD')

    @expectedFailurePY2
    def test_b_literal_creates_newbytes_object(self):
        """
        It would nice if the b'' literal syntax could be coaxed into producing
        bytes objects somehow ... ;)
        """
        b = b'ABCD'
        self.assertTrue(isinstance(b, bytes))
        self.assertEqual(b[0], 65)
        self.assertTrue(repr(b).startswith('b'))

    def test_repr(self):
        b = bytes(b'ABCD')
        self.assertTrue(repr(b).startswith('b'))

    def test_str(self):
        b = bytes(b'ABCD')
        self.assertTrue(str(b), "b'ABCD'")

    def test_bytes_setitem(self):
        b = b'ABCD'
        with self.assertRaises(TypeError):
            b[0] = b'B'

    def test_bytes_iteration(self):
        b = bytes(b'ABCD')
        for item in b:
            self.assertTrue(isinstance(item, Integral))
        self.assertEqual(list(b), [65, 66, 67, 68])

    def test_bytes_plus_unicode_string(self):
        b = bytes(b'ABCD')
        u = u'EFGH'
        with self.assertRaises(TypeError):
            b + u

        with self.assertRaises(TypeError):
            u + b

    def test_bytes_plus_bytes(self):
        b1 = bytes(b'ABCD')
        b2 = b1 + b1
        self.assertEqual(b2, b'ABCDABCD')
        self.assertTrue(isinstance(b2, bytes))

        b3 = b1 + b'ZYXW'
        self.assertEqual(b3, b'ABCDZYXW')
        self.assertTrue(isinstance(b3, bytes))

        b4 = b'ZYXW' + b1
        self.assertEqual(b4, b'ZYXWABCD')
        self.assertTrue(isinstance(b4, bytes))

    def test_find_not_found(self):
        self.assertEqual(-1, bytes(b'ABCDE').find(b':'))

    def test_find_found(self):
        self.assertEqual(2, bytes(b'AB:CD:E').find(b':'))

    def test_rfind_not_found(self):
        self.assertEqual(-1, bytes(b'ABCDE').rfind(b':'))

    def test_rfind_found(self):
        self.assertEqual(5, bytes(b'AB:CD:E').rfind(b':'))

    def test_bytes_join_bytes(self):
        b = bytes(b' * ')
        strings = [b'AB', b'EFGH', b'IJKL']
        result = b.join(strings)
        self.assertEqual(result, b'AB * EFGH * IJKL')
        self.assertTrue(isinstance(result, bytes))

    def test_bytes_join_others(self):
        b = bytes(b' ')
        with self.assertRaises(TypeError):
            b.join([42])
        with self.assertRaises(TypeError):
            b.join(b'blah')
        with self.assertRaises(TypeError):
            b.join(bytes(b'blah'))

    def test_bytes_join_unicode_strings(self):
        b = bytes(b'ABCD')
        strings = [u'EFGH', u'IJKL']
        with self.assertRaises(TypeError):
            b.join(strings)

    def test_bytes_replace(self):
        b = bytes(b'ABCD')
        c = b.replace(b'A', b'F')
        self.assertEqual(c, b'FBCD')
        self.assertTrue(isinstance(c, bytes))

        with self.assertRaises(TypeError):
            b.replace(b'A', u'F')
        with self.assertRaises(TypeError):
            b.replace(u'A', b'F')

    def test_bytes_partition(self):
        b1 = bytes(b'ABCD')
        parts = b1.partition(b'B')
        self.assertEqual(parts, (b'A', b'B', b'CD'))
        self.assertTrue(all([isinstance(p, bytes) for p in parts]))

        b2 = bytes(b'ABCDABCD')
        parts = b2.partition(b'B')
        self.assertEqual(parts, (b'A', b'B', b'CDABCD'))

    def test_bytes_rpartition(self):
        b2 = bytes(b'ABCDABCD')
        parts = b2.rpartition(b'B')
        self.assertEqual(parts, (b'ABCDA', b'B', b'CD'))
        self.assertTrue(all([isinstance(p, bytes) for p in parts]))

    def test_bytes_contains_something(self):
        b = bytes(b'ABCD')
        self.assertTrue(b'A' in b)
        self.assertTrue(65 in b)

        self.assertTrue(b'AB' in b)
        self.assertTrue(bytes([65, 66]) in b)

        self.assertFalse(b'AC' in b)
        self.assertFalse(bytes([65, 67]) in b)

        self.assertFalse(b'Z' in b)
        self.assertFalse(99 in b)

        with self.assertRaises(TypeError):
            u'A' in b

    def test_bytes_index(self):
        b = bytes(b'ABCD')
        self.assertEqual(b.index(b'B'), 1)
        self.assertEqual(b.index(67), 2)

    def test_startswith(self):
        b = bytes(b'abcd')
        self.assertTrue(b.startswith(b'a'))
        self.assertTrue(b.startswith((b'a', b'b')))
        self.assertTrue(b.startswith(bytes(b'ab')))
        self.assertFalse(b.startswith((b'A', b'B')))

        with self.assertRaises(TypeError) as cm:
            b.startswith(65)
        with self.assertRaises(TypeError) as cm:
            b.startswith([b'A'])
        exc = str(cm.exception)
        # self.assertIn('bytes', exc)
        # self.assertIn('tuple', exc)

    def test_endswith(self):
        b = bytes(b'abcd')
        self.assertTrue(b.endswith(b'd'))
        self.assertTrue(b.endswith((b'c', b'd')))
        self.assertTrue(b.endswith(bytes(b'cd')))
        self.assertFalse(b.endswith((b'A', b'B')))

        with self.assertRaises(TypeError) as cm:
            b.endswith(65)
        with self.assertRaises(TypeError) as cm:
            b.endswith([b'D'])
        exc = str(cm.exception)
        # self.assertIn('bytes', exc)
        # self.assertIn('tuple', exc)

    def test_decode(self):
        b = bytes(b'abcd')
        s = b.decode('utf-8')
        self.assertEqual(s, 'abcd')
        self.assertTrue(isinstance(s, str))

    def test_encode(self):
        b = bytes(b'abcd')
        with self.assertRaises(AttributeError) as cm:
            b.encode('utf-8')

    def test_eq(self):
        """
        Equals: ==
        """
        b = bytes(b'ABCD')
        self.assertEqual(b, b'ABCD')
        self.assertTrue(b == b'ABCD')
        self.assertEqual(b'ABCD', b)
        self.assertEqual(b, b)
        self.assertFalse(b == b'ABC')
        self.assertFalse(b == bytes(b'ABC'))
        self.assertFalse(b == u'ABCD')
        self.assertFalse(b == str('ABCD'))
        # Fails:
        # self.assertFalse(u'ABCD' == b)
        self.assertFalse(str('ABCD') == b)

        self.assertFalse(b == list(b))
        self.assertFalse(b == str(b))
        self.assertFalse(b == u'ABC')
        self.assertFalse(bytes(b'Z') == 90)

    def test_ne(self):
        b = bytes(b'ABCD')
        self.assertFalse(b != b)
        self.assertFalse(b != b'ABCD')
        self.assertTrue(b != b'ABCDEFG')
        self.assertTrue(b != bytes(b'ABCDEFG'))
        self.assertTrue(b'ABCDEFG' != b)

        # self.assertTrue(b'ABCD' != u'ABCD')
        self.assertTrue(b != u'ABCD')
        self.assertTrue(b != u'ABCDE')
        self.assertTrue(bytes(b'') != str(u''))
        self.assertTrue(str(u'') != bytes(b''))

        self.assertTrue(b != list(b))
        self.assertTrue(b != str(b))

    def test_hash(self):
        d = {}
        b = bytes(b'ABCD')
        native_b = b'ABCD'
        s = str('ABCD')
        native_s = u'ABCD'
        d[b] = b
        d[s] = s
        self.assertEqual(len(d), 2)
        # This should overwrite d[s] but not d[b]:
        d[native_s] = native_s
        self.assertEqual(len(d), 2)
        # This should overwrite d[native_s] again:
        d[s] = s
        self.assertEqual(len(d), 2)
        self.assertEqual(set(d.keys()), set([s, b]))

    @unittest.expectedFailure
    def test_hash_with_native_types(self):
        # Warning: initializing the dict with native Py2 types throws the
        # hashing out:
        d = {u'ABCD': u'ABCD', b'ABCD': b'ABCD'}
        # On Py2: len(d) == 1
        b = bytes(b'ABCD')
        s = str('ABCD')
        d[s] = s
        d[b] = b
        # Fails:
        self.assertEqual(len(d) > 1)

    def test_add(self):
        b = bytes(b'ABC')
        c = bytes(b'XYZ')
        d = b + c
        self.assertTrue(isinstance(d, bytes))
        self.assertEqual(d, b'ABCXYZ')
        f = b + b'abc'
        self.assertTrue(isinstance(f, bytes))
        self.assertEqual(f, b'ABCabc')
        g = b'abc' + b
        self.assertTrue(isinstance(g, bytes))
        self.assertEqual(g, b'abcABC')

    def test_cmp(self):
        b = bytes(b'ABC')
        with self.assertRaises(TypeError):
            b > 3
        with self.assertRaises(TypeError):
            b > u'XYZ'
        with self.assertRaises(TypeError):
            b <= 3
        with self.assertRaises(TypeError):
            b >= int(3)
        with self.assertRaises(TypeError):
            b < 3.3
        with self.assertRaises(TypeError):
            b > (3.3 + 3j)
        with self.assertRaises(TypeError):
            b >= (1, 2)
        with self.assertRaises(TypeError):
            b <= [1, 2]

    def test_mul(self):
        b = bytes(b'ABC')
        c = b * 4
        self.assertTrue(isinstance(c, bytes))
        self.assertEqual(c, b'ABCABCABCABC')
        d = b * int(4)
        self.assertTrue(isinstance(d, bytes))
        self.assertEqual(d, b'ABCABCABCABC')
        if utils.PY2:
            e = b * long(4)
            self.assertTrue(isinstance(e, bytes))
            self.assertEqual(e, b'ABCABCABCABC')

    def test_rmul(self):
        b = bytes(b'XYZ')
        c = 3 * b
        self.assertTrue(isinstance(c, bytes))
        self.assertEqual(c, b'XYZXYZXYZ')
        d = b * int(3)
        self.assertTrue(isinstance(d, bytes))
        self.assertEqual(d, b'XYZXYZXYZ')
        if utils.PY2:
            e = long(3) * b
            self.assertTrue(isinstance(e, bytes))
            self.assertEqual(e, b'XYZXYZXYZ')

    def test_slice(self):
        b = bytes(b'ABCD')
        c1 = b[:]
        self.assertTrue(isinstance(c1, bytes))
        self.assertTrue(c1 == b)
        # The following is not true, whereas it is true normally on Py2 and
        # Py3. Does this matter?:
        # self.assertTrue(c1 is b)

        c2 = b[10:]
        self.assertTrue(isinstance(c2, bytes))
        self.assertTrue(c2 == bytes(b''))
        self.assertTrue(c2 == b'')

        c3 = b[:0]
        self.assertTrue(isinstance(c3, bytes))
        self.assertTrue(c3 == bytes(b''))
        self.assertTrue(c3 == b'')

        c4 = b[:1]
        self.assertTrue(isinstance(c4, bytes))
        self.assertTrue(c4 == bytes(b'A'))
        self.assertTrue(c4 == b'A')

        c5 = b[:-1]
        self.assertTrue(isinstance(c5, bytes))
        self.assertTrue(c5 == bytes(b'ABC'))
        self.assertTrue(c5 == b'ABC')

    def test_bytes_frozenset(self):
        _ALWAYS_SAFE = bytes(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                             b'abcdefghijklmnopqrstuvwxyz'
                             b'0123456789'
                             b'_.-')                   # from Py3.3's urllib.parse
        s = frozenset(_ALWAYS_SAFE)
        self.assertTrue(65 in s)
        self.assertFalse(64 in s)
        # Convert back to bytes
        b1 = bytes(s)
        self.assertTrue(65 in b1)
        self.assertEqual(set(b1), set(_ALWAYS_SAFE))

    def test_bytes_within_range(self):
        """
        Python 3 does this:
        >>> bytes([255, 254, 256])
        ValueError
          ...
        ValueError: bytes must be in range(0, 256)

        Ensure our bytes() constructor has the same behaviour
        """
        b1 = bytes([254, 255])
        self.assertEqual(b1, b'\xfe\xff')
        with self.assertRaises(ValueError):
            b2 = bytes([254, 255, 256])

    def test_bytes_hasattr_encode(self):
        """
        This test tests whether hasattr(b, 'encode') is False, like it is on Py3.
        """
        b = bytes(b'abcd')
        self.assertFalse(hasattr(b, 'encode'))
        self.assertTrue(hasattr(b, 'decode'))

    def test_quote_from_bytes(self):
        """
        This test was failing in the backported urllib.parse module in quote_from_bytes
        """
        empty = bytes([])
        self.assertEqual(empty, b'')
        self.assertTrue(type(empty), bytes)

        empty2 = bytes(())
        self.assertEqual(empty2, b'')
        self.assertTrue(type(empty2), bytes)

        safe = bytes(u'Philosopher guy: 孔子. More text here.'.encode('utf-8'))
        safe = bytes([c for c in safe if c < 128])
        self.assertEqual(safe, b'Philosopher guy: . More text here.')
        self.assertTrue(type(safe), bytes)

    def test_rstrip(self):
        b = bytes(b'abcd')
        c = b.rstrip(b'd')
        self.assertEqual(c, b'abc')
        self.assertEqual(type(c), type(b))

    def test_maketrans(self):
        """
        Issue #51.

        Test is from Py3.3.5.
        """
        transtable = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff'
        self.assertEqual(bytes.maketrans(b'', b''), transtable)

        transtable = b'\000\001\002\003\004\005\006\007\010\011\012\013\014\015\016\017\020\021\022\023\024\025\026\027\030\031\032\033\034\035\036\037 !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`xyzdefghijklmnopqrstuvwxyz{|}~\177\200\201\202\203\204\205\206\207\210\211\212\213\214\215\216\217\220\221\222\223\224\225\226\227\230\231\232\233\234\235\236\237\240\241\242\243\244\245\246\247\250\251\252\253\254\255\256\257\260\261\262\263\264\265\266\267\270\271\272\273\274\275\276\277\300\301\302\303\304\305\306\307\310\311\312\313\314\315\316\317\320\321\322\323\324\325\326\327\330\331\332\333\334\335\336\337\340\341\342\343\344\345\346\347\350\351\352\353\354\355\356\357\360\361\362\363\364\365\366\367\370\371\372\373\374\375\376\377'
        self.assertEqual(bytes.maketrans(b'abc', b'xyz'), transtable)

        transtable = b'\000\001\002\003\004\005\006\007\010\011\012\013\014\015\016\017\020\021\022\023\024\025\026\027\030\031\032\033\034\035\036\037 !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\177\200\201\202\203\204\205\206\207\210\211\212\213\214\215\216\217\220\221\222\223\224\225\226\227\230\231\232\233\234\235\236\237\240\241\242\243\244\245\246\247\250\251\252\253\254\255\256\257\260\261\262\263\264\265\266\267\270\271\272\273\274\275\276\277\300\301\302\303\304\305\306\307\310\311\312\313\314\315\316\317\320\321\322\323\324\325\326\327\330\331\332\333\334\335\336\337\340\341\342\343\344\345\346\347\350\351\352\353\354\355\356\357\360\361\362\363\364\365\366\367\370\371\372\373\374xyz'
        self.assertEqual(bytes.maketrans(b'\375\376\377', b'xyz'), transtable)
        self.assertRaises(ValueError, bytes.maketrans, b'abc', b'xyzq')
        self.assertRaises(TypeError, bytes.maketrans, 'abc', 'def')

    # def test_mod(self):
    #     """
    #     From Py3.5 test suite (post-PEP 461).
    #
    #     The bytes mod code is in _PyBytes_Format() in bytesobject.c in Py3.5.
    #     """
    #     b = b'hello, %b!'
    #     orig = b
    #     b = b % b'world'
    #     self.assertEqual(b, b'hello, world!')
    #     self.assertEqual(orig, b'hello, %b!')
    #     self.assertFalse(b is orig)
    #     b = b'%s / 100 = %d%%'
    #     a = b % (b'seventy-nine', 79)
    #     self.assertEqual(a, b'seventy-nine / 100 = 79%')

    # def test_imod(self):
    #     """
    #     From Py3.5 test suite (post-PEP 461)
    #     """
    #     # if (3, 0) <= sys.version_info[:2] < (3, 5):
    #     #     raise unittest.SkipTest('bytes % not yet implemented on Py3.0-3.4')
    #     b = bytes(b'hello, %b!')
    #     orig = b
    #     b %= b'world'
    #     self.assertEqual(b, b'hello, world!')
    #     self.assertEqual(orig, b'hello, %b!')
    #     self.assertFalse(b is orig)
    #     b = bytes(b'%s / 100 = %d%%')
    #     b %= (b'seventy-nine', 79)
    #     self.assertEqual(b, b'seventy-nine / 100 = 79%')

    # def test_mod_pep_461(self):
    #     """
    #     Test for the PEP 461 functionality (resurrection of %s formatting for
    #     bytes).
    #     """
    #     b1 = bytes(b'abc%b')
    #     b2 = b1 % b'def'
    #     self.assertEqual(b2, b'abcdef')
    #     self.assertTrue(isinstance(b2, bytes))
    #     self.assertEqual(type(b2), bytes)
    #     b3 = b1 % bytes(b'def')
    #     self.assertEqual(b3, b'abcdef')
    #     self.assertTrue(isinstance(b3, bytes))
    #     self.assertEqual(type(b3), bytes)
    #
    #     # %s is supported for backwards compatibility with Py2's str
    #     b4 = bytes(b'abc%s')
    #     b5 = b4 % b'def'
    #     self.assertEqual(b5, b'abcdef')
    #     self.assertTrue(isinstance(b5, bytes))
    #     self.assertEqual(type(b5), bytes)
    #     b6 = b4 % bytes(b'def')
    #     self.assertEqual(b6, b'abcdef')
    #     self.assertTrue(isinstance(b6, bytes))
    #     self.assertEqual(type(b6), bytes)
    #
    #     self.assertEqual(bytes(b'%c') % 48, b'0')
    #     self.assertEqual(bytes(b'%c') % b'a', b'a')
    #
    #     # For any numeric code %x, formatting of
    #     #     b"%x" % val
    #     # is supposed to be equivalent to
    #     #     ("%x" % val).encode("ascii")
    #     for code in b'xdiouxXeEfFgG':
    #         bytechar = bytes([code])
    #         pct_str = u"%" + bytechar.decode('ascii')
    #         for val in range(300):
    #             self.assertEqual(bytes(b"%" + bytechar) % val,
    #                              (pct_str % val).encode("ascii"))
    #
    #     with self.assertRaises(TypeError):
    #         bytes(b'%b') % 3.14
    #         # Traceback (most recent call last):
    #         # ...
    #         # TypeError: b'%b' does not accept 'float'
    #
    #     with self.assertRaises(TypeError):
    #         bytes(b'%b') % 'hello world!'
    #         # Traceback (most recent call last):
    #         # ...
    #         # TypeError: b'%b' does not accept 'str'
    #
    #     self.assertEqual(bytes(b'%a') % 3.14, b'3.14')
    #
    #     self.assertEqual(bytes(b'%a') % b'abc', b"b'abc'")
    #     self.assertEqual(bytes(b'%a') % bytes(b'abc'), b"b'abc'")
    #
    #     self.assertEqual(bytes(b'%a') % 'def', b"'def'")
    #
    #     # PEP 461 was updated after an Py3.5 alpha release to specify that %r is now supported
    #     # for compatibility: http://legacy.python.org/dev/peps/pep-0461/#id16
    #     assert bytes(b'%r' % b'abc') == bytes(b'%a' % b'abc')
    #
    #     # with self.assertRaises(TypeError):
    #     #     bytes(b'%r' % 'abc')

    @expectedFailurePY2
    def test_multiple_inheritance(self):
        """
        Issue #96 (for newbytes instead of newobject)
        """
        import collections

        class Base(bytes):
            pass

        class Foo(Base, collections.Container):
            def __contains__(self, item):
                return False

    @expectedFailurePY2
    def test_with_metaclass_and_bytes(self):
        """
        Issue #91 (for newdict instead of newobject)
        """
        from future.utils import with_metaclass

        class MetaClass(type):
            pass

        class TestClass(with_metaclass(MetaClass, bytes)):
            pass

    def test_surrogateescape_decoding(self):
        """
        Tests whether surrogateescape decoding works correctly.
        """
        pairs = [(u'\udcc3', b'\xc3'),
                 (u'\udcff', b'\xff')]

        for (s, b) in pairs:
            decoded = bytes(b).decode('utf-8', 'surrogateescape')
            self.assertEqual(s, decoded)
            self.assertTrue(isinstance(decoded, str))
            self.assertEqual(b, decoded.encode('utf-8', 'surrogateescape'))

    def test_issue_171_part_a(self):
        b1 = str(u'abc \u0123 do re mi').encode(u'utf_8')
        b2 = bytes(u'abc \u0123 do re mi', u'utf_8')
        b3 = bytes(str(u'abc \u0123 do re mi'), u'utf_8')

    @expectedFailurePY2
    def test_issue_171_part_b(self):
        """
        Tests whether:
        >>> nativebytes = bytes ; nativestr = str ; from builtins import *
        >>> nativebytes(bytes(b'asdf'))[0] == b'a' == b'asdf'
        """
        nativebytes = type(b'')
        nativestr = type('')
        b = nativebytes(bytes(b'asdf'))
        self.assertEqual(b, b'asdf')


if __name__ == '__main__':
    unittest.main()

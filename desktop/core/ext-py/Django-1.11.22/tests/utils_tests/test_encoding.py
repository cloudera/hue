# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import unittest

from django.utils import six
from django.utils.encoding import (
    escape_uri_path, filepath_to_uri, force_bytes, force_text, iri_to_uri,
    smart_text, uri_to_iri,
)
from django.utils.functional import SimpleLazyObject
from django.utils.http import urlquote_plus


class TestEncodingUtils(unittest.TestCase):
    def test_force_text_exception(self):
        """
        Broken __unicode__/__str__ actually raises an error.
        """
        class MyString(object):
            def __str__(self):
                return b'\xc3\xb6\xc3\xa4\xc3\xbc'

            __unicode__ = __str__

        # str(s) raises a TypeError on python 3 if the result is not a text type.
        # python 2 fails when it tries converting from str to unicode (via ASCII).
        exception = TypeError if six.PY3 else UnicodeError
        with self.assertRaises(exception):
            force_text(MyString())

    def test_force_text_lazy(self):
        s = SimpleLazyObject(lambda: 'x')
        self.assertTrue(issubclass(type(force_text(s)), six.text_type))

    def test_force_bytes_exception(self):
        """
        force_bytes knows how to convert to bytes an exception
        containing non-ASCII characters in its args.
        """
        error_msg = "This is an exception, voilà"
        exc = ValueError(error_msg)
        result = force_bytes(exc)
        self.assertEqual(result, error_msg.encode('utf-8'))

    def test_force_bytes_strings_only(self):
        today = datetime.date.today()
        self.assertEqual(force_bytes(today, strings_only=True), today)

    def test_smart_text(self):
        class Test:
            if six.PY3:
                def __str__(self):
                    return 'ŠĐĆŽćžšđ'
            else:
                def __str__(self):
                    return 'ŠĐĆŽćžšđ'.encode('utf-8')

        class TestU:
            if six.PY3:
                def __str__(self):
                    return 'ŠĐĆŽćžšđ'

                def __bytes__(self):
                    return b'Foo'
            else:
                def __str__(self):
                    return b'Foo'

                def __unicode__(self):
                    return '\u0160\u0110\u0106\u017d\u0107\u017e\u0161\u0111'

        self.assertEqual(smart_text(Test()), '\u0160\u0110\u0106\u017d\u0107\u017e\u0161\u0111')
        self.assertEqual(smart_text(TestU()), '\u0160\u0110\u0106\u017d\u0107\u017e\u0161\u0111')
        self.assertEqual(smart_text(1), '1')
        self.assertEqual(smart_text('foo'), 'foo')


class TestRFC3987IEncodingUtils(unittest.TestCase):

    def test_filepath_to_uri(self):
        self.assertEqual(filepath_to_uri('upload\\чубака.mp4'), 'upload/%D1%87%D1%83%D0%B1%D0%B0%D0%BA%D0%B0.mp4')
        self.assertEqual(
            filepath_to_uri('upload\\чубака.mp4'.encode('utf-8')),
            'upload/%D1%87%D1%83%D0%B1%D0%B0%D0%BA%D0%B0.mp4'
        )

    def test_iri_to_uri(self):
        cases = [
            # Valid UTF-8 sequences are encoded.
            ('red%09rosé#red', 'red%09ros%C3%A9#red'),
            ('/blog/for/Jürgen Münster/', '/blog/for/J%C3%BCrgen%20M%C3%BCnster/'),
            ('locations/%s' % urlquote_plus('Paris & Orléans'), 'locations/Paris+%26+Orl%C3%A9ans'),

            # Reserved chars remain unescaped.
            ('%&', '%&'),
            ('red&♥ros%#red', 'red&%E2%99%A5ros%#red'),
        ]

        for iri, uri in cases:
            self.assertEqual(iri_to_uri(iri), uri)

            # Test idempotency.
            self.assertEqual(iri_to_uri(iri_to_uri(iri)), uri)

    def test_uri_to_iri(self):
        cases = [
            # Valid UTF-8 sequences are decoded.
            ('/%E2%99%A5%E2%99%A5/', '/♥♥/'),
            ('/%E2%99%A5%E2%99%A5/?utf8=%E2%9C%93', '/♥♥/?utf8=✓'),

            # Broken UTF-8 sequences remain escaped.
            ('/%AAd%AAj%AAa%AAn%AAg%AAo%AA/', '/%AAd%AAj%AAa%AAn%AAg%AAo%AA/'),
            ('/%E2%99%A5%E2%E2%99%A5/', '/♥%E2♥/'),
            ('/%E2%99%A5%E2%99%E2%99%A5/', '/♥%E2%99♥/'),
            ('/%E2%E2%99%A5%E2%99%A5%99/', '/%E2♥♥%99/'),
            ('/%E2%99%A5%E2%99%A5/?utf8=%9C%93%E2%9C%93%9C%93', '/♥♥/?utf8=%9C%93✓%9C%93'),
        ]

        for uri, iri in cases:
            self.assertEqual(uri_to_iri(uri), iri)

            # Test idempotency.
            self.assertEqual(uri_to_iri(uri_to_iri(uri)), iri)

    def test_complementarity(self):
        cases = [
            ('/blog/for/J%C3%BCrgen%20M%C3%BCnster/', '/blog/for/J\xfcrgen M\xfcnster/'),
            ('%&', '%&'),
            ('red&%E2%99%A5ros%#red', 'red&♥ros%#red'),
            ('/%E2%99%A5%E2%99%A5/', '/♥♥/'),
            ('/%E2%99%A5%E2%99%A5/?utf8=%E2%9C%93', '/♥♥/?utf8=✓'),
            ('/%AAd%AAj%AAa%AAn%AAg%AAo%AA/', '/%AAd%AAj%AAa%AAn%AAg%AAo%AA/'),
            ('/%E2%99%A5%E2%E2%99%A5/', '/♥%E2♥/'),
            ('/%E2%99%A5%E2%99%E2%99%A5/', '/♥%E2%99♥/'),
            ('/%E2%E2%99%A5%E2%99%A5%99/', '/%E2♥♥%99/'),
            ('/%E2%99%A5%E2%99%A5/?utf8=%9C%93%E2%9C%93%9C%93', '/♥♥/?utf8=%9C%93✓%9C%93'),
        ]

        for uri, iri in cases:
            self.assertEqual(iri_to_uri(uri_to_iri(uri)), uri)
            self.assertEqual(uri_to_iri(iri_to_uri(iri)), iri)

    def test_escape_uri_path(self):
        self.assertEqual(
            escape_uri_path('/;some/=awful/?path/:with/@lots/&of/+awful/chars'),
            '/%3Bsome/%3Dawful/%3Fpath/:with/@lots/&of/+awful/chars'
        )
        self.assertEqual(escape_uri_path('/foo#bar'), '/foo%23bar')
        self.assertEqual(escape_uri_path('/foo?bar'), '/foo%3Fbar')

# -*- coding: utf-8 -*-
"""
Automatic tests for python-ldap's module ldap.filter

See https://www.python-ldap.org/ for details.
"""

import os
import unittest

# Switch off processing .ldaprc or ldap.conf before importing _ldap
os.environ['LDAPNOINIT'] = '1'

from ldap.filter import escape_filter_chars


class TestDN(unittest.TestCase):
    """
    test ldap.functions
    """

    def test_escape_filter_chars_mode0(self):
        """
        test function escape_filter_chars() with escape_mode=0
        """
        self.assertEqual(
            escape_filter_chars(r'foobar'),
            'foobar'
        )
        self.assertEqual(
            escape_filter_chars(r'foo\bar'),
            r'foo\5cbar'
        )
        self.assertEqual(
            escape_filter_chars(
                r'foo\bar',
                escape_mode=0
            ),
            r'foo\5cbar'
        )

    def test_escape_filter_chars_mode1(self):
        """
        test function escape_filter_chars() with escape_mode=1
        """
        self.assertEqual(
            escape_filter_chars(
                '\xc3\xa4\xc3\xb6\xc3\xbc\xc3\x84\xc3\x96\xc3\x9c\xc3\x9f',
                escape_mode=1
            ),
            r'\c3\a4\c3\b6\c3\bc\c3\84\c3\96\c3\9c\c3\9f'
        )

    def test_escape_filter_chars_mode2(self):
        """
        test function escape_filter_chars() with escape_mode=2
        """
        self.assertEqual(
            escape_filter_chars(
                'foobar',
                escape_mode=2
            ),
            r'\66\6f\6f\62\61\72'
        )


if __name__ == '__main__':
    unittest.main()

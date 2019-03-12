# -*- coding: utf-8 -*-
"""
Automatic tests for python-ldap's module ldif

See https://www.python-ldap.org/ for details.
"""

from __future__ import unicode_literals

import os
import textwrap
import unittest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

# Switch off processing .ldaprc or ldap.conf before importing _ldap
os.environ['LDAPNOINIT'] = '1'

import ldif


class TestLDIFParser(unittest.TestCase):
    """
    Various LDIF test cases
    """

    def _parse_records(
            self,
            ldif_string,
            ignored_attr_types=None,
            max_entries=0,
        ):
        """
        Parse LDIF data in `ldif_string' into list of records
        """
        ldif_file = StringIO(ldif_string)
        ldif_parser = ldif.LDIFRecordList(
            ldif_file,
            ignored_attr_types=ignored_attr_types,
            max_entries=max_entries,
        )
        parser_method = getattr(
            ldif_parser,
            'parse_%s_records' % self.record_type
        )
        parser_method()
        if self.record_type == 'entry':
            return ldif_parser.all_records
        elif self.record_type == 'change':
            return ldif_parser.all_modify_changes

    def _unparse_records(self, records):
        """
        Returns LDIF string with entry records from list `records'
        """
        ldif_file = StringIO()
        ldif_writer = ldif.LDIFWriter(ldif_file)
        if self.record_type == 'entry':
            for dn, entry in records:
                ldif_writer.unparse(dn, entry)
        elif self.record_type == 'change':
            for dn, modops, controls in records:
                ldif_writer.unparse(dn, modops)
        return ldif_file.getvalue()

    def check_records(
            self,
            ldif_string,
            records,
            ignored_attr_types=None,
            max_entries=0
    ):
        """
        Checks whether entry records in `ldif_string' gets correctly parsed
        and matches list of unparsed `records'.
        """
        ldif_string = textwrap.dedent(ldif_string).lstrip()
        parsed_records = self._parse_records(
            ldif_string,
            ignored_attr_types=ignored_attr_types,
            max_entries=max_entries,
        )
        generated_ldif = self._unparse_records(records)
        parsed_records2 = self._parse_records(
            generated_ldif,
            ignored_attr_types=ignored_attr_types,
            max_entries=max_entries,
        )
        self.assertEqual(records, parsed_records)
        self.assertEqual(records, parsed_records2)


class TestEntryRecords(TestLDIFParser):
    """
    Various LDIF test cases
    """
    record_type='entry'

    def test_empty(self):
        self.check_records(
            """
            version: 1

            """,
            []
        )

    def test_simple(self):
        self.check_records(
            """
            version: 1

            dn: cn=x,cn=y,cn=z
            attrib: value
            attrib: value2

            """,
            [
                (
                    'cn=x,cn=y,cn=z',
                    {
                        'attrib': [b'value', b'value2'],
                    },
                ),
            ]
        )

    def test_simple2(self):
        self.check_records(
            """
            dn:cn=x,cn=y,cn=z
            attrib:value
            attrib:value2

            """,
            [
                (
                    'cn=x,cn=y,cn=z',
                    {
                        'attrib': [b'value', b'value2'],
                    },
                ),
            ]
        )

    def test_multiple(self):
        self.check_records(
            """
            dn: cn=x,cn=y,cn=z
            a: v
            attrib: value
            attrib: value2

            dn: cn=a,cn=b,cn=c
            attrib: value2
            attrib: value3
            b: v

            """,
            [
                (
                    'cn=x,cn=y,cn=z',
                    {
                        'attrib': [b'value', b'value2'],
                        'a': [b'v'],
                    },
                ),
                (
                    'cn=a,cn=b,cn=c',
                    {
                        'attrib': [b'value2', b'value3'],
                        'b': [b'v'],
                    },
                ),
            ]
        )

    def test_folded(self):
        self.check_records(
            """
            dn: cn=x,cn=y,cn=z
            attrib: very\x20
             long
              line-folded\x20
             value
            attrib2: %s

            """ % ('asdf.'*20), [
                (
                    'cn=x,cn=y,cn=z',
                    {
                        'attrib': [b'very long line-folded value'],
                        'attrib2': [b'asdf.'*20],
                    }
                ),
            ]
        )

    def test_empty_attr_values(self):
        self.check_records(
            """
            dn: cn=x,cn=y,cn=z
            attrib1:
            attrib1: foo
            attrib2:
            attrib2: foo

            """,
            [
                (
                    'cn=x,cn=y,cn=z',
                    {
                        'attrib1': [b'', b'foo'],
                        'attrib2': [b'', b'foo'],
                    },
                ),
            ]
        )

    def test_binary(self):
        self.check_records(
            """
            dn: cn=x,cn=y,cn=z
            attrib:: CQAKOiVA

            """,
            [
                (
                    'cn=x,cn=y,cn=z',
                    {
                        'attrib': [b'\t\0\n:%@'],
                    },
                ),
            ]
        )

    def test_binary2(self):
        self.check_records(
            """
            dn: cn=x,cn=y,cn=z
            attrib::CQAKOiVA

            """,
            [
                (
                    'cn=x,cn=y,cn=z',
                    {'attrib': [b'\t\0\n:%@']},
                ),
            ]
        )

    def test_big_binary(self):
        self.check_records(
            """
            dn: cn=x,cn=y,cn=z
            attrib:: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
             AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
             AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
             AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
             AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
             AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
             AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
             AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
             AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
             =

            """,
            [
                (
                    'cn=x,cn=y,cn=z',
                    {'attrib': [500*b'\0']},
                ),
            ]
        )

    def test_unicode(self):
        # Encode "Ströder" as UTF-8+Base64
        # Putting "Ströder" in a single line would be an invalid LDIF file
        # per https://tools.ietf.org/html/rfc2849 (only safe ascii is allowed in a file)
        self.check_records(
            """
            dn: cn=Michael Stroeder,dc=stroeder,dc=com
            lastname:: U3Ryw7ZkZXI=

            """,
            [
                (
                    'cn=Michael Stroeder,dc=stroeder,dc=com',
                    {'lastname': [b'Str\303\266der']},
                ),
            ]
        )

    def test_unencoded_unicode(self):
        # Encode "Ströder" as UTF-8, without base64
        # This is an invalid LDIF file, but such files are often found in the wild.
        self.check_records(
            """
            dn: cn=Michael Stroeder,dc=stroeder,dc=com
            lastname: Ströder

            """,
            [
                (
                    'cn=Michael Stroeder,dc=stroeder,dc=com',
                    {'lastname': [b'Str\303\266der']},
                ),
            ]
        )

    def test_sorted(self):
        self.check_records(
            """
            dn: cn=x,cn=y,cn=z
            b: value_b
            c: value_c
            a: value_a

            """,
            [
                (
                    'cn=x,cn=y,cn=z',
                    {
                        'a': [b'value_a'],
                        'b': [b'value_b'],
                        'c': [b'value_c'],
                    }
                ),
            ]
        )

    def test_ignored_attr_types(self):
        self.check_records(
            """
            dn: cn=x,cn=y,cn=z
            a: value_a
            b: value_b
            c: value_c

            """,
            [
                (
                    'cn=x,cn=y,cn=z',
                    {
                        'a': [b'value_a'],
                        'c': [b'value_c'],
                    }
                ),
            ],
            ignored_attr_types=['b'],
        )

    def test_comments(self):
        self.check_records(
            """
            # comment #1
             with line-folding
            dn: cn=x1,cn=y1,cn=z1
            b1: value_b1
            c1: value_c1
            a1: value_a1

            # comment #2.1
            # comment #2.2
            dn: cn=x2,cn=y2,cn=z2
            b2: value_b2
            c2: value_c2
            a2: value_a2

            """,
            [
                (
                    'cn=x1,cn=y1,cn=z1',
                    {
                        'a1': [b'value_a1'],
                        'b1': [b'value_b1'],
                        'c1': [b'value_c1'],
                    }
                ),
                (
                    'cn=x2,cn=y2,cn=z2',
                    {
                        'a2': [b'value_a2'],
                        'b2': [b'value_b2'],
                        'c2': [b'value_c2'],
                    }
                ),
            ]
        )

    def test_max_entries(self):
        self.check_records(
            """
            dn: cn=x1,cn=y1,cn=z1
            b1: value_b1
            a1: value_a1

            dn: cn=x2,cn=y2,cn=z2
            b2: value_b2
            a2: value_a2

            dn: cn=x3,cn=y3,cn=z3
            b3: value_b3
            a3: value_a3

            dn: cn=x4,cn=y4,cn=z4
            b2: value_b4
            a2: value_a4

            """,
            [
                (
                    'cn=x1,cn=y1,cn=z1',
                    {
                        'a1': [b'value_a1'],
                        'b1': [b'value_b1'],
                    }
                ),
                (
                    'cn=x2,cn=y2,cn=z2',
                    {
                        'a2': [b'value_a2'],
                        'b2': [b'value_b2'],
                    }
                ),
            ],
            max_entries=2
        )

    def test_missing_trailing_line_separator(self):
        self.check_records(
            """
            dn: cn=x1,cn=y1,cn=z1
            first: value_a1
            middle: value_b1
            last: value_c1

            dn: cn=x2,cn=y2,cn=z2
            first: value_a2
            middle: value_b2
            last: value_c2""",
            [
                (
                    'cn=x1,cn=y1,cn=z1',
                    {
                        'first': [b'value_a1'],
                        'middle': [b'value_b1'],
                        'last': [b'value_c1'],
                    }
                ),
                (
                    'cn=x2,cn=y2,cn=z2',
                    {
                        'first': [b'value_a2'],
                        'middle': [b'value_b2'],
                        'last': [b'value_c2'],
                    }
                ),
            ],
        )

    def test_weird_empty_lines(self):
        self.check_records(
            """

            # comment before version

            version: 1


            dn: cn=x1,cn=y1,cn=z1
            first: value_a1
            middle: value_b1
            last: value_c1


            dn: cn=x2,cn=y2,cn=z2
            first: value_a2
            middle: value_b2
            last: value_c2""",
            [
                (
                    'cn=x1,cn=y1,cn=z1',
                    {
                        'first': [b'value_a1'],
                        'middle': [b'value_b1'],
                        'last': [b'value_c1'],
                    }
                ),
                (
                    'cn=x2,cn=y2,cn=z2',
                    {
                        'first': [b'value_a2'],
                        'middle': [b'value_b2'],
                        'last': [b'value_c2'],
                    }
                ),
            ],
        )

    def test_multiple_empty_lines(self):
        """
        test malformed LDIF with multiple empty lines
        """
        self.check_records(
            """
            # normal
            dn: uid=one,dc=tld
            uid: one



            # after extra empty line
            dn: uid=two,dc=tld
            uid: two

            """,
            [
                (
                    'uid=one,dc=tld',
                    {'uid': [b'one']}
                ),
                (
                    'uid=two,dc=tld',
                    {'uid': [b'two']}
                ),
            ],
        )


class TestChangeRecords(TestLDIFParser):
    """
    Various LDIF test cases
    """
    record_type='change'

    def test_empty(self):
        self.check_records(
            """
            version: 1
            """,
            [],
        )

    def test_simple(self):
        self.check_records(
            """
            version: 1

            dn: cn=x,cn=y,cn=z
            changetype: modify
            replace: attrib
            attrib: value
            attrib: value2
            -
            add: attrib2
            attrib2: value
            attrib2: value2
            -
            delete: attrib3
            attrib3: value
            -
            delete: attrib4
            -

            """,
            [
                (
                    'cn=x,cn=y,cn=z',
                    [
                        (ldif.MOD_OP_INTEGER['replace'], 'attrib', [b'value', b'value2']),
                        (ldif.MOD_OP_INTEGER['add'], 'attrib2', [b'value', b'value2']),
                        (ldif.MOD_OP_INTEGER['delete'], 'attrib3', [b'value']),
                        (ldif.MOD_OP_INTEGER['delete'], 'attrib4', None),
                    ],
                    None,
                ),
            ],
        )

    def test_weird_empty_lines(self):
        self.check_records(
            """

            # comment before version

            version: 1


            dn: cn=x,cn=y,cn=z
            changetype: modify
            replace: attrib
            attrib: value
            attrib: value2
            -
            add: attrib2
            attrib2: value
            attrib2: value2
            -
            delete: attrib3
            attrib3: value
            -
            delete: attrib4
            -


            dn: cn=foo,cn=bar
            changetype: modify
            replace: attrib
            attrib: value
            attrib: value2
            -
            add: attrib2
            attrib2: value
            attrib2: value2
            -
            delete: attrib3
            attrib3: value
            -
            delete: attrib4""",
            [
                (
                    'cn=x,cn=y,cn=z',
                    [
                        (ldif.MOD_OP_INTEGER['replace'], 'attrib', [b'value', b'value2']),
                        (ldif.MOD_OP_INTEGER['add'], 'attrib2', [b'value', b'value2']),
                        (ldif.MOD_OP_INTEGER['delete'], 'attrib3', [b'value']),
                        (ldif.MOD_OP_INTEGER['delete'], 'attrib4', None),
                    ],
                    None,
                ),
                (
                    'cn=foo,cn=bar',
                    [
                        (ldif.MOD_OP_INTEGER['replace'], 'attrib', [b'value', b'value2']),
                        (ldif.MOD_OP_INTEGER['add'], 'attrib2', [b'value', b'value2']),
                        (ldif.MOD_OP_INTEGER['delete'], 'attrib3', [b'value']),
                        (ldif.MOD_OP_INTEGER['delete'], 'attrib4', None),
                    ],
                    None,
                ),
            ],
        )

    def test_missing_trailing_dash_separator(self):
        self.check_records(
            """
            version: 1

            dn: cn=x,cn=y,cn=z
            changetype: modify
            replace: attrib
            attrib: value
            attrib: value2
            -
            add: attrib2
            attrib2: value
            attrib2: value2

            """,
            [
                (
                    'cn=x,cn=y,cn=z',
                    [
                        (ldif.MOD_OP_INTEGER['replace'], 'attrib', [b'value', b'value2']),
                        (ldif.MOD_OP_INTEGER['add'], 'attrib2', [b'value', b'value2']),
                    ],
                    None,
                ),
            ],
        )

    def test_bad_change_records(self):
        for bad_ldif_string in (
            """
            changetype: modify
            replace: attrib
            attrib: value
            attrib: value2

            """,
        ):
            ldif_string = textwrap.dedent(bad_ldif_string).lstrip() + '\n'
            try:
                res = self._parse_records(ldif_string)
            except ValueError as value_error:
                pass
            else:
                self.fail("should have raised ValueError: %r" % bad_ldif_string)

    def test_mod_increment(self):
        self.check_records(
            """
            version: 1

            dn: cn=x,cn=y,cn=z
            changetype: modify
            increment: gidNumber
            gidNumber: 1
            -

            """,
            [
                (
                    'cn=x,cn=y,cn=z',
                    [
                        (ldif.MOD_OP_INTEGER['increment'], 'gidNumber', [b'1']),
                    ],
                    None,
                ),
            ],
        )


if __name__ == '__main__':
    unittest.main()

# -*- coding: utf-8 -*-
"""
Automatic tests for python-ldap's module ldap.modlist

See https://www.python-ldap.org/ for details.
"""

import os
import unittest

# Switch off processing .ldaprc or ldap.conf before importing _ldap
os.environ['LDAPNOINIT'] = '1'

import ldap
from ldap.modlist import addModlist,modifyModlist


class TestModlist(unittest.TestCase):

    addModlist_tests = [
        (
            {
                'objectClass': [b'person',b'pilotPerson'],
                'cn':[b'Michael Str\303\266der',b'Michael Stroeder'],
                'sn':[b'Str\303\266der'],
                'dummy1':[],
                'dummy2':[b'2'],
                'dummy3':[b''],
            },
            [
                ('objectClass',[b'person',b'pilotPerson']),
                ('cn',[b'Michael Str\303\266der',b'Michael Stroeder']),
                ('sn',[b'Str\303\266der']),
                ('dummy2',[b'2']),
                ('dummy3',[b'']),
            ]
        ),
    ]

    def test_addModlist(self):
        for entry,test_modlist in self.addModlist_tests:
            test_modlist.sort()
            result_modlist = addModlist(entry)
            result_modlist.sort()
            self.assertEqual(
                test_modlist, result_modlist,
                'addModlist(%s) returns\n%s\ninstead of\n%s.' % (
                    repr(entry),repr(result_modlist),repr(test_modlist)
                )
            )

    modifyModlist_tests = [
        (
            {
                'objectClass':[b'person',b'pilotPerson'],
                'cn':[b'Michael Str\303\266der',b'Michael Stroeder'],
                'sn':[b'Str\303\266der'],
                'enum':[b'a',b'b',b'c'],
                'c':[b'DE'],
            },
            {
                'objectClass':[b'person',b'inetOrgPerson'],
                'cn':[b'Michael Str\303\266der',b'Michael Stroeder'],
                'sn':[],
                'enum':[b'a',b'b',b'd'],
                'mail':[b'michael@stroeder.com'],
            },
            [],
            [
                (ldap.MOD_DELETE,'objectClass',None),
                (ldap.MOD_ADD,'objectClass',[b'person',b'inetOrgPerson']),
                (ldap.MOD_DELETE,'c',None),
                (ldap.MOD_DELETE,'sn',None),
                (ldap.MOD_ADD,'mail',[b'michael@stroeder.com']),
                (ldap.MOD_DELETE,'enum',None),
                (ldap.MOD_ADD,'enum',[b'a',b'b',b'd']),
            ]
        ),

        (
            {
                'c':[b'DE'],
            },
            {
                'c':[b'FR'],
            },
            [],
            [
                (ldap.MOD_DELETE,'c',None),
                (ldap.MOD_ADD,'c',[b'FR']),
            ]
        ),

        # Now a weird test-case for catching all possibilities
        # of removing an attribute with MOD_DELETE,attr_type,None
        (
            {
                'objectClass':[b'person'],
                'cn':[None],
                'sn':[b''],
                'c':[b'DE'],
            },
            {
                'objectClass':[],
                'cn':[],
                'sn':[None],
            },
            [],
            [
                (ldap.MOD_DELETE,'c',None),
                (ldap.MOD_DELETE,'objectClass',None),
                (ldap.MOD_DELETE,'sn',None),
            ]
        ),

        (
            {
                'objectClass':[b'person'],
                'cn':[b'Michael Str\303\266der',b'Michael Stroeder'],
                'sn':[b'Str\303\266der'],
                'enum':[b'a',b'b',b'C'],
            },
            {
                'objectClass':[b'Person'],
                'cn':[b'Michael Str\303\266der',b'Michael Stroeder'],
                'sn':[],
                'enum':[b'a',b'b',b'c'],
            },
            ['objectClass'],
            [
                (ldap.MOD_DELETE,'sn',None),
                (ldap.MOD_DELETE,'enum',None),
                (ldap.MOD_ADD,'enum',[b'a',b'b',b'c']),
            ]
        ),

    ]

    def test_modifyModlist(self):
        for old_entry, new_entry, case_ignore_attr_types, test_modlist in self.modifyModlist_tests:
            test_modlist.sort()
            result_modlist = modifyModlist(
                old_entry, new_entry,
                case_ignore_attr_types=case_ignore_attr_types)
            result_modlist.sort()

            self.assertEqual(
                test_modlist, result_modlist,
                'modifyModlist(%s,%s) returns\n%s\ninstead of\n%s.' % (
                    repr(old_entry),
                    repr(new_entry),
                    repr(result_modlist),
                    repr(test_modlist),
                )
            )


if __name__ == '__main__':
    unittest.main()

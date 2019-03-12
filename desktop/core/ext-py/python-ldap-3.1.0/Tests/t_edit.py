from __future__ import unicode_literals

import sys

if sys.version_info[0] <= 2:
    PY2 = True
    text_type = unicode
else:
    PY2 = False
    text_type = str

import os
import unittest

# Switch off processing .ldaprc or ldap.conf before importing _ldap
os.environ['LDAPNOINIT'] = '1'

import ldap
from ldap.ldapobject import LDAPObject
from slapdtest import SlapdTestCase


class EditionTests(SlapdTestCase):

    @classmethod
    def setUpClass(cls):
        super(EditionTests, cls).setUpClass()
        base = cls.server.suffix
        suffix_dc = base.split(',')[0][3:]

        # insert some Foo* objects via ldapadd
        cls.server.ldapadd("\n".join([
            'dn: '+cls.server.suffix,
            'objectClass: dcObject',
            'objectClass: organization',
            'dc: '+suffix_dc,
            'o: '+suffix_dc,
            '',
            'dn: '+cls.server.root_dn,
            'objectClass: applicationProcess',
            'cn: '+cls.server.root_cn,
            '',
            "dn: cn=Foo1,"+base,
            "objectClass: organizationalRole",
            "cn: Foo1",
            "",
            "dn: cn=Foo2,"+base,
            "objectClass: organizationalRole",
            "cn: Foo2",
            "",
            "dn: cn=Foo3,"+base,
            "objectClass: organizationalRole",
            "cn: Foo3",
            "",
            "dn: ou=Container,"+base,
            "objectClass: organizationalUnit",
            "ou: Container",
            "",
            "dn: cn=Foo4,ou=Container,"+base,
            "objectClass: organizationalRole",
            "cn: Foo4",
            "",
        ])+"\n")

    def setUp(self):
        self.ldap = LDAPObject(self.server.ldap_uri, bytes_mode=False)
        self.ldap.protocol_version = 3
        self.ldap.set_option(ldap.OPT_REFERRALS, 0)
        self.ldap.simple_bind_s(
            self.server.root_dn,
            self.server.root_pw
        )

    def tearDown(self):
        self.ldap.unbind()

    def test_add_object(self):
        base = self.server.suffix
        dn = "cn=Added,ou=Container," + base
        self.ldap.add_ext_s(dn, [
            ("objectClass", [b'organizationalRole']),
            ("cn", [b'Added']),
        ])

        # Lookup the object
        result = self.ldap.search_s(base, ldap.SCOPE_SUBTREE, '(cn=Added)', ['*'])
        self.assertEqual(result, [
            ("cn=Added,ou=Container," + base,
                {'cn': [b'Added'], 'objectClass': [b'organizationalRole']}),
        ])
        # Delete object
        self.ldap.delete_s(dn)
        result = self.ldap.search_s(
            base, ldap.SCOPE_SUBTREE, '(cn=Added)', ['*']
        )
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()

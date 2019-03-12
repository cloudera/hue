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


class TestBinds(SlapdTestCase):
    unicode_val = "abc\U0001f498def"
    unicode_val_bytes = unicode_val.encode('utf-8')
    dn_unicode = "CN=" + unicode_val
    dn_bytes = dn_unicode.encode('utf-8')

    def _get_ldapobject(self, bytes_mode=None):
        l = LDAPObject(self.server.ldap_uri, bytes_mode=bytes_mode)
        l.protocol_version = 3
        l.set_option(ldap.OPT_REFERRALS,0)
        return l

    def test_simple_bind(self):
        l = self._get_ldapobject(False)
        with self.assertRaises(ldap.INVALID_CREDENTIALS):
            l.simple_bind_s(self.dn_unicode, self.unicode_val)

    def test_unicode_bind(self):
        l = self._get_ldapobject(False)
        l.simple_bind(self.dn_unicode, "ascii")

        l = self._get_ldapobject(False)
        l.simple_bind("CN=user", self.unicode_val)

    @unittest.skipUnless(PY2, "no bytes_mode under Py3")
    def test_unicode_bind_bytesmode(self):
        l = self._get_ldapobject(True)
        with self.assertRaises(TypeError):
            l.simple_bind_s(self.dn_unicode, self.unicode_val_bytes)

        with self.assertRaises(TypeError):
            l.simple_bind_s(self.dn_bytes, self.unicode_val)

        # Works when encoded to UTF-8
        with self.assertRaises(ldap.INVALID_CREDENTIALS):
            l.simple_bind_s(self.dn_bytes, self.unicode_val_bytes)

    def test_unicode_bind_no_bytesmode(self):
        l = self._get_ldapobject(False)
        with self.assertRaises(TypeError):
            l.simple_bind_s(self.dn_bytes, self.unicode_val)

        # Works fine in Python 3 because 'cred' (the password) is read in
        # using the "s#" format which, unlike "s", accepts either a str
        # (unicode) *or* bytes.
        #
        # with self.assertRaises(TypeError):
        #     l.simple_bind_s(self.dn_unicode, self.unicode_val_bytes)

        with self.assertRaises(ldap.INVALID_CREDENTIALS):
            l.simple_bind_s(self.dn_unicode, self.unicode_val)


if __name__ == '__main__':
    unittest.main()

import os
import unittest

# Switch off processing .ldaprc or ldap.conf before importing _ldap
os.environ['LDAPNOINIT'] = '1'

from ldap.controls import pagedresults
from ldap.controls import libldap


PRC_BER = b'0\x0b\x02\x01\x05\x04\x06cookie'
SIZE = 5
COOKIE = b'cookie'


class TestLibldapControls(unittest.TestCase):
    def test_pagedresults_encode(self):
        pr = pagedresults.SimplePagedResultsControl(
            size=SIZE, cookie=COOKIE
        )
        lib = libldap.SimplePagedResultsControl(
            size=SIZE, cookie=COOKIE
        )
        self.assertEqual(pr.encodeControlValue(), lib.encodeControlValue())
        self.assertEqual(pr.encodeControlValue(), PRC_BER)

    def test_pagedresults_decode(self):
        pr = pagedresults.SimplePagedResultsControl()
        pr.decodeControlValue(PRC_BER)
        self.assertEqual(pr.size, SIZE)
        # LDAPString (OCTET STRING)
        self.assertIsInstance(pr.cookie, bytes)
        self.assertEqual(pr.cookie, COOKIE)

        lib = libldap.SimplePagedResultsControl()
        lib.decodeControlValue(PRC_BER)
        self.assertEqual(lib.size, SIZE)
        self.assertIsInstance(lib.cookie, bytes)
        self.assertEqual(lib.cookie, COOKIE)

    def test_matchedvalues(self):
        mvc = libldap.MatchedValuesControl()
        # unverified
        self.assertEqual(mvc.encodeControlValue(), b'0\r\x87\x0bobjectClass')

    def test_assertioncontrol(self):
        ac = libldap.AssertionControl()
        # unverified
        self.assertEqual(ac.encodeControlValue(), b'\x87\x0bobjectClass')


if __name__ == '__main__':
    unittest.main()

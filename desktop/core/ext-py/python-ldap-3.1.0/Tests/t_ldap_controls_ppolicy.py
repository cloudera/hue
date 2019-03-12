import os
import unittest

# Switch off processing .ldaprc or ldap.conf before importing _ldap
os.environ['LDAPNOINIT'] = '1'

from ldap.controls import ppolicy


PP_GRACEAUTH = b'0\x84\x00\x00\x00\t\xa0\x84\x00\x00\x00\x03\x81\x01\x02'
PP_TIMEBEFORE = b'0\x84\x00\x00\x00\t\xa0\x84\x00\x00\x00\x03\x80\x012'


class TestControlsPPolicy(unittest.TestCase):
    def assertPPolicy(self, pp, timeBeforeExpiration=None,
                      graceAuthNsRemaining=None, error=None):
        self.assertEqual(pp.timeBeforeExpiration, timeBeforeExpiration)
        self.assertEqual(pp.graceAuthNsRemaining, graceAuthNsRemaining)
        self.assertEqual(pp.error, error)

    def test_ppolicy_graceauth(self):
        pp = ppolicy.PasswordPolicyControl()
        pp.decodeControlValue(PP_GRACEAUTH)
        self.assertPPolicy(pp, graceAuthNsRemaining=2)

    def test_ppolicy_timebefore(self):
        pp = ppolicy.PasswordPolicyControl()
        pp.decodeControlValue(PP_TIMEBEFORE)
        self.assertPPolicy(pp, timeBeforeExpiration=50)


if __name__ == '__main__':
    unittest.main()

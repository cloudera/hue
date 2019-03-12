import os
import unittest

# Switch off processing .ldaprc or ldap.conf before importing _ldap
os.environ['LDAPNOINIT'] = '1'

from slapdtest import SlapdTestCase, requires_tls

import ldap
from ldap.controls import RequestControlTuples
from ldap.controls.pagedresults import SimplePagedResultsControl
from ldap.controls.openldap import SearchNoOpControl
from ldap.ldapobject import SimpleLDAPObject


SENTINEL = object()

TEST_CTRL = RequestControlTuples([
    # with BER data
    SimplePagedResultsControl(criticality=0, size=5, cookie=b'cookie'),
    # value-less
    SearchNoOpControl(criticality=1),
])
TEST_CTRL_EXPECTED = [
    TEST_CTRL[0],
    # get_option returns empty bytes
    (TEST_CTRL[1][0], TEST_CTRL[1][1], b''),
]


class BaseTestOptions(object):
    """Common tests for getting/setting options

    Used in subclasses below
    """

    def get_option(self, option):
        raise NotImplementedError()

    def set_option(self, option, value):
        raise NotImplementedError()

    def _check_option(self, option, value, expected=SENTINEL):
        old = self.get_option(option)
        try:
            self.set_option(option, value)
            new = self.get_option(option)
            if expected is SENTINEL:
                self.assertEqual(new, value)
            else:
                self.assertEqual(new, expected)
        finally:
            self.set_option(option, old)
            self.assertEqual(self.get_option(option), old)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            self.get_option(-1)
        with self.assertRaises(ValueError):
            self.set_option(-1, '')

    def _test_timeout(self, option):
        self._check_option(option, 10.5)
        self._check_option(option, 0)
        with self.assertRaises(ValueError):
            self._check_option(option, -5)
        with self.assertRaises(TypeError):
            self.set_option(option, object)
        with self.assertRaises(OverflowError):
            self._check_option(option, 10**1000)
        old = self.get_option(option)
        try:
            self.set_option(option, None)
            self.assertIsNone(self.get_option(option))
            self.set_option(option, -1)
            self.assertIsNone(self.get_option(option))
        finally:
            self.set_option(option, old)

    def test_timeout(self):
        self._test_timeout(ldap.OPT_TIMEOUT)

    def test_network_timeout(self):
        self._test_timeout(ldap.OPT_NETWORK_TIMEOUT)

    def _test_controls(self, option):
        self._check_option(option, [])
        self._check_option(option, TEST_CTRL, TEST_CTRL_EXPECTED)
        self._check_option(option, tuple(TEST_CTRL), TEST_CTRL_EXPECTED)
        with self.assertRaises(TypeError):
            self.set_option(option, object)

        with self.assertRaises(TypeError):
            # must contain a tuple
            self.set_option(option, [list(TEST_CTRL[0])])
        with self.assertRaises(TypeError):
            # data must be bytes or None
            self.set_option(
                option,
                [TEST_CTRL[0][0], TEST_CTRL[0][1], u'data']
            )

    def test_client_controls(self):
        self._test_controls(ldap.OPT_CLIENT_CONTROLS)

    def test_server_controls(self):
        self._test_controls(ldap.OPT_SERVER_CONTROLS)

    def test_uri(self):
        self._check_option(ldap.OPT_URI, "ldapi:///path/to/socket")
        with self.assertRaises(TypeError):
            self.set_option(ldap.OPT_URI, object)

    @requires_tls()
    def test_cafile(self):
        # None or a distribution or OS-specific path
        self.get_option(ldap.OPT_X_TLS_CACERTFILE)

    def test_readonly(self):
        value = self.get_option(ldap.OPT_API_INFO)
        self.assertIsInstance(value, dict)
        with self.assertRaises(ValueError) as e:
            self.set_option(ldap.OPT_API_INFO, value)
        self.assertIn('read-only', str(e.exception))


class TestGlobalOptions(BaseTestOptions, unittest.TestCase):
    """Test setting/getting options globally
    """

    def get_option(self, option):
        return ldap.get_option(option)

    def set_option(self, option, value):
        return ldap.set_option(option, value)


class TestLDAPObjectOptions(BaseTestOptions, SlapdTestCase):
    """Test setting/getting connection-specific options
    """

    ldap_object_class = SimpleLDAPObject

    def setUp(self):
        self.conn = self._open_ldap_conn(
            who=self.server.root_dn,
            cred=self.server.root_pw
        )

    def tearDown(self):
        self.conn.unbind_s()
        self.conn = None

    def get_option(self, option):
        return self.conn.get_option(option)

    def set_option(self, option, value):
        return self.conn.set_option(option, value)

    def test_network_timeout_attribute(self):
        option = ldap.OPT_NETWORK_TIMEOUT
        old = self.get_option(option)
        try:
            self.assertEqual(self.conn.network_timeout, old)

            self.conn.network_timeout = 5
            self.assertEqual(self.conn.network_timeout, 5)
            self.assertEqual(self.get_option(option), 5)

            self.conn.network_timeout = -1
            self.assertIsNone(self.conn.network_timeout)
            self.assertIsNone(self.get_option(option))

            self.conn.network_timeout = 10.5
            self.assertEqual(self.conn.network_timeout, 10.5)
            self.assertEqual(self.get_option(option), 10.5)

            self.conn.network_timeout = None
            self.assertIsNone(self.conn.network_timeout)
            self.assertIsNone(self.get_option(option))
        finally:
            self.set_option(option, old)

    # test is failing with:
    # pyasn1.error.SubstrateUnderrunError: Short octet stream on tag decoding
    @unittest.expectedFailure
    def test_client_controls(self):
        self._test_controls(ldap.OPT_CLIENT_CONTROLS)

    @unittest.expectedFailure
    def test_server_controls(self):
        self._test_controls(ldap.OPT_SERVER_CONTROLS)


if __name__ == '__main__':
    unittest.main()

import importlib
import os
import unittest
import warnings

# Switch off processing .ldaprc or ldap.conf before importing _ldap
os.environ['LDAPNOINIT'] = '1'

import ldap.asyncsearch


class TestLdapAsyncSearch(unittest.TestCase):
    def test_deprecated(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.resetwarnings()
            warnings.simplefilter('once', DeprecationWarning)
            old = importlib.import_module('ldap.async')
        self.assertEqual(len(w), 1)
        diff = set(dir(ldap.asyncsearch)).difference(dir(old))
        self.assertEqual(diff, set())


if __name__ == '__main__':
    unittest.main()

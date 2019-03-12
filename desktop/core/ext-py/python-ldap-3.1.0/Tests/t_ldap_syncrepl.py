# -*- coding: utf-8 -*-
"""
Automatic tests for python-ldap's module ldap.syncrepl

See https://www.python-ldap.org/ for details.
"""


import os
import shelve
import sys
import unittest

if sys.version_info[0] <= 2:
    PY2 = True
else:
    PY2 = False

# Switch off processing .ldaprc or ldap.conf before importing _ldap
os.environ['LDAPNOINIT'] = '1'

import ldap
from ldap.ldapobject import SimpleLDAPObject
from ldap.syncrepl import SyncreplConsumer

from slapdtest import SlapdObject, SlapdTestCase

# a template string for generating simple slapd.conf file
SLAPD_CONF_PROVIDER_TEMPLATE = r"""
serverID %(serverid)s
moduleload back_%(database)s
moduleload syncprov
include "%(schema_prefix)s/core.schema"
loglevel %(loglevel)s
allow bind_v2

authz-regexp
  "gidnumber=%(root_gid)s\\+uidnumber=%(root_uid)s,cn=peercred,cn=external,cn=auth"
  "%(rootdn)s"

database %(database)s
directory "%(directory)s"
suffix "%(suffix)s"
rootdn "%(rootdn)s"
rootpw "%(rootpw)s"
overlay syncprov
syncprov-checkpoint 100 10
syncprov-sessionlog 100
index objectclass,entryCSN,entryUUID eq
"""

# Define initial data load, both as an LDIF and as a dictionary.
LDIF_TEMPLATE = """dn: %(suffix)s
objectClass: dcObject
objectClass: organization
dc: %(dc)s
o: %(dc)s

dn: %(rootdn)s
objectClass: applicationProcess
objectClass: simpleSecurityObject
cn: %(rootcn)s
userPassword: %(rootpw)s

dn: cn=Foo1,%(suffix)s
objectClass: organizationalRole
cn: Foo1

dn: cn=Foo2,%(suffix)s
objectClass: organizationalRole
cn: Foo2

dn: cn=Foo3,%(suffix)s
objectClass: organizationalRole
cn: Foo3

dn: ou=Container,%(suffix)s
objectClass: organizationalUnit
ou: Container

dn: cn=Foo4,ou=Container,%(suffix)s
objectClass: organizationalRole
cn: Foo4

"""

# NOTE: For the dict, it needs to be kept up-to-date as we make changes!
LDAP_ENTRIES = {
    'ou=Container,dc=slapd-test,dc=python-ldap,dc=org': {
        'objectClass': [b'organizationalUnit'],
        'ou': [b'Container']
    },
    'cn=Foo2,dc=slapd-test,dc=python-ldap,dc=org': {
        'objectClass': [b'organizationalRole'],
        'cn': [b'Foo2']
    },
    'cn=Foo4,ou=Container,dc=slapd-test,dc=python-ldap,dc=org': {
        'objectClass': [b'organizationalRole'],
        'cn': [b'Foo4']
    },
    'cn=Manager,dc=slapd-test,dc=python-ldap,dc=org': {
        'objectClass': [b'applicationProcess', b'simpleSecurityObject'],
        'userPassword': [b'password'],
        'cn': [b'Manager']
    },
    'cn=Foo3,dc=slapd-test,dc=python-ldap,dc=org': {
        'objectClass': [b'organizationalRole'],
        'cn': [b'Foo3']
    },
    'cn=Foo1,dc=slapd-test,dc=python-ldap,dc=org': {
        'objectClass': [b'organizationalRole'],
        'cn': [b'Foo1']
    },
    'dc=slapd-test,dc=python-ldap,dc=org': {
        'objectClass': [b'dcObject', b'organization'],
        'dc': [b'slapd-test'],
        'o': [b'slapd-test']
    }
}


class SyncreplProvider(SlapdObject):
    slapd_conf_template = SLAPD_CONF_PROVIDER_TEMPLATE


class SyncreplClient(SimpleLDAPObject, SyncreplConsumer):
    """
    This is a very simple class to start up the syncrepl search
    and handle callbacks that come in.

    Needs to be separate, because once an LDAP client starts a syncrepl
    search, it can't be used for anything else.
    """

    def __init__(self, uri, dn, password, storage=None, **kwargs):
        """
        Set up our object by creating a search client, connecting, and binding.
        """

        if storage is not None:
            self.data = shelve.open(storage)
            self.uuid_dn = shelve.open(storage + 'uuid_dn')
            self.dn_attrs = shelve.open(storage + 'dn_attrs')
            self.using_shelve = True
        else:
            self.data = {}
            self.uuid_dn = {}
            self.dn_attrs = {}
            self.using_shelve = False

        self.data['cookie'] = None
        self.present = []
        self.refresh_done = False

        SimpleLDAPObject.__init__(self, uri, **kwargs)
        self.simple_bind_s(dn, password)

    def unbind_s(self):
        """
        In addition to unbinding from LDAP, we need to close the shelf.
        """
        if self.using_shelve is True:
            self.data.close()
            self.uuid_dn.close()
            self.dn_attrs.close()
        SimpleLDAPObject.unbind_s(self)

    def search(self, search_base, search_mode):
        """
        Start a syncrepl search operation, given a base DN and search mode.
        """
        self.search_id = self.syncrepl_search(
            search_base,
            ldap.SCOPE_SUBTREE,
            mode=search_mode,
        )

    def cancel(self):
        """
        A simple wrapper to call parent class with syncrepl search ID.
        """
        SimpleLDAPObject.cancel(self, self.search_id)

    def poll(self, timeout=None, all=0):
        """
        Take the params, add the syncrepl search ID, and call the proper poll.
        """
        return self.syncrepl_poll(
            self.search_id,
            timeout=timeout,
            all=all
        )

    def syncrepl_get_cookie(self):
        """
        Pull cookie from storage, if one exists.
        """
        return self.data['cookie']

    def syncrepl_set_cookie(self, cookie):
        """
        Update stored cookie.
        """
        self.data['cookie'] = cookie

    def syncrepl_refreshdone(self):
        """
        Just update a variable.
        """
        self.refresh_done = True

    def syncrepl_delete(self, uuids):
        """
        Delete the given items from both maps.
        """
        for uuid in uuids:
            del self.dn_attrs[self.uuid_dn[uuid]]
            del self.uuid_dn[uuid]

    def syncrepl_entry(self, dn, attrs, uuid):
        """
        Handles adds and changes (including DN changes).
        """
        if uuid in self.uuid_dn:
            # Catch changing DNs.
            if dn != self.uuid_dn[uuid]:
                # Delete data associated with old DN.
                del self.dn_attrs[self.uuid_dn[uuid]]

        # Update both maps.
        self.uuid_dn[uuid] = dn
        self.dn_attrs[dn] = attrs

    def syncrepl_present(self, uuids, refreshDeletes=False):
        """
        The 'present' message from the LDAP server is the most complicated
        part of the refresh phase.  Suggest looking here for more info:
        https://syncrepl-client.readthedocs.io/en/latest/client.html
        """
        if (uuids is not None) and (refreshDeletes is False):
            self.present.extend(uuids)

        elif (uuids is None) and (refreshDeletes is False):
            deleted_uuids = []
            for uuid in self.uuid_dn.keys():
                if uuid not in self.present:
                    deleted_uuids.append(uuid)

            if len(deleted_uuids) > 0:
                self.syncrepl_delete(deleted_uuids)

        elif (uuids is not None) and (refreshDeletes is True):
            self.syncrepl_delete(uuids)

        elif (uuids is None) and (refreshDeletes is True):
            pass


class BaseSyncreplTests(object):
    """
    This is a test of all the basic Syncrepl operations.  It covers starting a
    search (both types of search), doing the refresh part of the search,
    and checking that we got everything that we expected.  We also test that
    timeouts and cancellation are working properly.
    """

    server_class = SyncreplProvider
    ldap_object_class = SimpleLDAPObject

    @classmethod
    def setUpClass(cls):
        super(BaseSyncreplTests, cls).setUpClass()
        # insert some Foo* objects via ldapadd
        cls.server.ldapadd(
            LDIF_TEMPLATE % {
                'suffix':cls.server.suffix,
                'rootdn':cls.server.root_dn,
                'rootcn':cls.server.root_cn,
                'rootpw':cls.server.root_pw,
                'dc': cls.server.suffix.split(',')[0][3:],
            }
        )

    def setUp(self):
        super(BaseSyncreplTests, self).setUp()
        self.tester = None
        self.suffix = None

    def tearDown(self):
        self.tester.unbind_s()
        super(BaseSyncreplTests, self).tearDown()

    def create_client(self):
        raise NotImplementedError

    def test_refreshOnly_search(self):
        '''
        Test to see if we can initialize a syncrepl search.
        '''
        self.tester.search(
            self.suffix,
            'refreshOnly'
        )

    def test_refreshAndPersist_search(self):
        self.tester.search(
            self.suffix,
            'refreshAndPersist'
        )

    def test_refreshOnly_poll_full(self):
        """
        Test doing a full refresh cycle, and check what we got.
        """
        self.tester.search(
            self.suffix,
            'refreshOnly'
        )
        poll_result = self.tester.poll(
            all=1,
            timeout=None
        )
        self.assertFalse(poll_result)
        self.assertEqual(self.tester.dn_attrs, LDAP_ENTRIES)

    def test_refreshAndPersist_poll_only(self):
        """
        Test the refresh part of refresh-and-persist, and check what we got.
        """
        self.tester.search(
            self.suffix,
            'refreshAndPersist'
        )

        # Make sure to stop the test before going into persist mode.
        while self.tester.refresh_done is not True:
            poll_result = self.tester.poll(
                all=0,
                timeout=None
            )
            self.assertTrue(poll_result)

        self.assertEqual(self.tester.dn_attrs, LDAP_ENTRIES)

    def test_refreshAndPersist_timeout(self):
        """
        Make sure refreshAndPersist can handle a search with timeouts.
        """
        self.tester.search(
            self.suffix,
            'refreshAndPersist'
        )

        # Run a quick refresh, that shouldn't have any changes.
        while self.tester.refresh_done is not True:
            poll_result = self.tester.poll(
                all=0,
                timeout=None
            )
            self.assertTrue(poll_result)

        # Again, server data should not have changed.
        self.assertEqual(self.tester.dn_attrs, LDAP_ENTRIES)

        # Run a search with timeout.
        # Nothing is changing the server, so it shoud timeout.
        self.assertRaises(
            ldap.TIMEOUT,
            self.tester.poll,
            all=0,
            timeout=1
        )

    def test_refreshAndPersist_cancelled(self):
        """
        Make sure refreshAndPersist can handle cancelling a syncrepl search.
        """
        self.tester.search(
            self.suffix,
            'refreshAndPersist'
        )

        # Run a quick refresh, that shouldn't have any changes.
        while self.tester.refresh_done is not True:
            poll_result = self.tester.poll(
                all=0,
                timeout=None
            )
            self.assertTrue(poll_result)

        # Again, server data should not have changed.
        self.assertEqual(self.tester.dn_attrs, LDAP_ENTRIES)

        # Request cancellation.
        self.tester.cancel()

        # Run another poll, without timeout, but which should cancel out.
        self.assertRaises(
            ldap.CANCELLED,
            self.tester.poll,
            all=1,
            timeout=None
        )

        # Server data should still be intact.
        self.assertEqual(self.tester.dn_attrs, LDAP_ENTRIES)


    # TODO:
    # * Make a new client, with a data store, and close.  Then, load a new
    # client with the same datastore, and see if the data store loads OK.
    # * Make a new client, with a data store, and close.  Then, load a new
    # client with the same datastore.  Delete an entry, and the cookie.
    # Start the sync, and everything should sync up OK.
    # * Load the refreshOnly client, using existing data.  Make a change
    # on the server, and the client should pick it up in the refresh phase.
    # * Load the refreshAndPersist client, using existing data.  Make a change
    # on the server, and the client should pick it up in the refresh phase.
    # * Load the refreshAndPersist client, using existing data.  Let the
    # refresh phase complete.  Make a change on the server, and the client
    # should pick it up during the persist phase.


class TestSyncrepl(BaseSyncreplTests, SlapdTestCase):
    def setUp(self):
        super(TestSyncrepl, self).setUp()
        self.tester = SyncreplClient(
            self.server.ldap_uri,
            self.server.root_dn,
            self.server.root_pw,
            bytes_mode=False
        )
        self.suffix = self.server.suffix


@unittest.skipUnless(PY2, "no bytes_mode under Py3")
class TestSyncreplBytesMode(BaseSyncreplTests, SlapdTestCase):
    def setUp(self):
        super(TestSyncreplBytesMode, self).setUp()
        self.tester = SyncreplClient(
            self.server.ldap_uri,
            self.server.root_dn.encode('utf-8'),
            self.server.root_pw.encode('utf-8'),
            bytes_mode=True
        )
        self.suffix = self.server.suffix.encode('utf-8')


if __name__ == '__main__':
    unittest.main()

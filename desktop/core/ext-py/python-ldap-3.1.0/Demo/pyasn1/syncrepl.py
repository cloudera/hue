#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script implements a syncrepl consumer which syncs data from an OpenLDAP
server to a local (shelve) database.

Notes:

The bound user needs read access to the attributes entryDN and entryCSN.
"""
from __future__ import print_function

# Import modules from Python standard lib
import logging
import shelve
import signal
import sys
import time

# Import the python-ldap modules
import ldap
import ldapurl
# Import specific classes from python-ldap
from ldap.ldapobject import ReconnectLDAPObject
from ldap.syncrepl import SyncreplConsumer

logger = logging.getLogger('syncrepl')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

# Global state
watcher_running = True
ldap_connection = False


class SyncReplClient(ReconnectLDAPObject, SyncreplConsumer):
    """
    Syncrepl Consumer Client
    """

    def __init__(self, db_path, *args, **kwargs):
        # Initialise the LDAP Connection first
        ldap.ldapobject.ReconnectLDAPObject.__init__(self, *args, **kwargs)
        # Now prepare the data store
        if db_path:
            self.__data = shelve.open(db_path, 'c')
        else:
            self.__data = {}
        # We need this for later internal use
        self.__presentUUIDs = {}

    def close_db(self):
        # Close the data store properly to avoid corruption
        self.__data.close()

    def syncrepl_get_cookie(self):
        if 'cookie' in self.__data:
            return self.__data['cookie']

    def syncrepl_set_cookie(self,cookie):
        self.__data['cookie'] = cookie

    def syncrepl_entry(self, dn, attributes, uuid):
        logger.debug('dn=%r attributes=%r uuid=%r', dn, attributes, uuid)
        # First we determine the type of change we have here
        # (and store away the previous data for later if needed)
        previous_attributes = {}
        if uuid in self.__data:
            change_type = 'modify'
            previous_attributes = self.__data[uuid]
        else:
            change_type = 'add'
        # Now we store our knowledge of the existence of this entry
        # (including the DN as an attribute for convenience)
        attributes['dn'] = dn
        self.__data[uuid] = attributes
        # Debugging
        logger.debug('Detected %s of entry %r', change_type, dn)
        # If we have a cookie then this is not our first time being run,
        # so it must be a change
        if 'ldap_cookie' in self.__data:
            self.perform_application_sync(dn, attributes, previous_attributes)

    def syncrepl_delete(self,uuids):
        # Make sure we know about the UUID being deleted, just in case...
        uuids = [uuid for uuid in uuids if uuid in self.__data]
        # Delete all the UUID values we know of
        for uuid in uuids:
            logger.debug('Detected deletion of entry %r', self.__data[uuid]['dn'])
            del self.__data[uuid]

    def syncrepl_present(self,uuids,refreshDeletes=False):
        # If we have not been given any UUID values,
        # then we have recieved all the present controls...
        if uuids is None:
            # We only do things if refreshDeletes is false as the syncrepl
            # extension will call syncrepl_delete instead when it detects a
            # delete notice
            if refreshDeletes is False:
                deletedEntries = [
                    uuid
                    for uuid in self.__data.keys()
                    if uuid not in self.__presentUUIDs and uuid != 'ldap_cookie'
                ]
                self.syncrepl_delete( deletedEntries )
            # Phase is now completed, reset the list
            self.__presentUUIDs = {}
        else:
            # Note down all the UUIDs we have been sent
            for uuid in uuids:
                    self.__presentUUIDs[uuid] = True

    def syncrepl_refreshdone(self):
        logger.info('Initial synchronization is now done, persist phase begins')

    def perform_application_sync(self,dn,attributes,previous_attributes):
        logger.info('Performing application sync for %r', dn)
        return True


# Shutdown handler
def commenceShutdown(signum, stack):
    # Declare the needed global variables
    global watcher_running, ldap_connection
    logger.warn('Shutting down!')

    # We are no longer running
    watcher_running = False

    # Tear down the server connection
    if ldap_connection:
        ldap_connection.close_db()
        ldap_connection.unbind_s()
        del ldap_connection

    # Shutdown
    sys.exit(0)

# Time to actually begin execution
# Install our signal handlers
signal.signal(signal.SIGTERM, commenceShutdown)
signal.signal(signal.SIGINT, commenceShutdown)


try:
    ldap_url = ldapurl.LDAPUrl(sys.argv[1])
    database_path = sys.argv[2]
except IndexError,e:
    print (
        'Usage:\n'
        '{script_name} <LDAP URL> <pathname of database>\n'
        '{script_name} "ldap://127.0.0.1/cn=users,dc=test'
         '?*'
         '?sub'
         '?(objectClass=*)'
         '?bindname=uid=admin%2ccn=users%2cdc=test,'
         'X-BINDPW=password" db.shelve'
    ).format(script_name=sys.argv[0])
    sys.exit(1)
except ValueError as e:
    print('Error parsing command-line arguments:',str(e))
    sys.exit(1)

while watcher_running:
    logger.info('Connecting to %s now...', ldap_url.initializeUrl())
    # Prepare the LDAP server connection (triggers the connection as well)
    ldap_connection = SyncReplClient(database_path, ldap_url.initializeUrl())

    # Now we login to the LDAP server
    try:
        ldap_connection.simple_bind_s(ldap_url.who, ldap_url.cred)
    except ldap.INVALID_CREDENTIALS as err:
        logger.error('Login to LDAP server failed: %s', err)
        sys.exit(1)
    except ldap.SERVER_DOWN:
        logger.warn('LDAP server is down, going to retry.')
        time.sleep(5)
        continue

    # Commence the syncing
    logger.debug('Commencing sync process')
    ldap_search = ldap_connection.syncrepl_search(
        ldap_url.dn or '',
        ldap_url.scope or ldap.SCOPE_SUBTREE,
        mode = 'refreshAndPersist',
        attrlist=ldap_url.attrs,
        filterstr = ldap_url.filterstr or '(objectClass=*)'
    )

    try:
        while ldap_connection.syncrepl_poll( all = 1, msgid = ldap_search):
            pass
    except KeyboardInterrupt:
        # User asked to exit
        commenceShutdown(None, None)
    except Exception as err:
        # Handle any exception
        if watcher_running:
            logger.exception('Unhandled exception, going to retry: %s', err)
            logger.info('Going to retry after 5 secs')
            time.sleep(5)

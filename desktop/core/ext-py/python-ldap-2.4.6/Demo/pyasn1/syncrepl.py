#!/usr/bin/python

import sys,anydbm,getpass
import ldap,ldapurl,ldap.syncrepl


class DNSync(ldap.ldapobject.LDAPObject,ldap.syncrepl.SyncreplConsumer):

    def __init__(self, filename, *args, **kwargs):
        ldap.ldapobject.LDAPObject.__init__(self, *args, **kwargs)
        self.__db = anydbm.open(filename, 'c', 0640)
        self.__presentUUIDs = {}

    def syncrepl_set_cookie(self,cookie):
        self.__db['cookie'] = cookie

    def syncrepl_get_cookie(self):
        if 'cookie' in self.__db:
            return self.__db['cookie']

    def syncrepl_delete(self, uuids):
        for uuid in uuids:
            dn = self.__db[uuid]
            print "delete %s" % dn
            del self.__db[uuid]

    def syncrepl_present(self, uuids, refreshDeletes=False):
        if uuids is None:
            if refreshDeletes is False:
                nonpresent = []
                for uuid in self.__db.keys():
                    if uuid == 'cookie': continue
                    if uuid in self.__presentUUIDs: continue
                    nonpresent.append(uuid)
                self.syncrepl_delete(nonpresent)
            self.__presentUUIDs = {}
        else:
            for uuid in uuids:
                self.__presentUUIDs[uuid] = True

    def syncrepl_entry(self, dn, attrs, uuid):
        if uuid in self.__db:
            odn = self.__db[uuid]
            if odn != dn:
                print "moddn %s -> %s" % ( odn, dn )
            else:
                print "modify %s" % self.__db[uuid]
        else:
            print "add %s" % dn
        self.__db[uuid] = dn


try:
  ldap_url = ldapurl.LDAPUrl(sys.argv[1])
  db_filename = sys.argv[2]
except IndexError,ValueError:
  print 'Usage: syncrepl.py <LDAP URL> <DB filename>'
  sys.exit(1)

# Set debugging level
#ldap.set_option(ldap.OPT_DEBUG_LEVEL,255)
ldapmodule_trace_level = 2
ldapmodule_trace_file = sys.stderr

ldap_sync_conn = DNSync(
  db_filename,
  ldap_url.initializeUrl(),
  trace_level=ldapmodule_trace_level,
  trace_file=ldapmodule_trace_file
)

if ldap_url.who and ldap_url.cred is None:
  print 'Password for %s:' % (repr(ldap_url.who))
  ldap_url.cred = getpass.getpass()

try:
  ldap_sync_conn.simple_bind_s(ldap_url.who or '',ldap_url.cred or '')

except ldap.INVALID_CREDENTIALS,e:
  print 'Simple bind failed:',str(e)
  sys.exit(1)

msgid = ldap_sync_conn.syncrepl_search(
  ldap_url.dn,
  ldap_url.scope,
  mode='refreshAndPersist',
  filterstr=ldap_url.filterstr
)
try:
    while ldap_sync_conn.syncrepl_poll(all=1, msgid=msgid):
        pass
except KeyboardInterrupt:
    pass

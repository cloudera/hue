#!/usr/bin/python

import sys,ldap

from ldap.ldapobject import LDAPObject
from ldapurl import LDAPUrl

try:
  ldap_url = LDAPUrl(sys.argv[1])
except (IndexError,ValueError):
  print 'Usage: pref_test.py <LDAP URL>'
  sys.exit(1)

try:
  l = LDAPObject(ldap_url.initializeUrl(),trace_level=2)
  l.protocol_version = 3
  l.simple_bind_s(ldap_url.who or '',ldap_url.cred or '')
  searchmsgid = l.search(
    ldap_url.dn,
    ldap_url.scope or ldap.SCOPE_BASE,
    ldap_url.filterstr or '(objectClass=*)',
    ldap_url.attrs or ['*']
  )
  l.cancel_s(searchmsgid)
  l.unbind_s()
except ldap.LDAPError,e:
  print 'An error occured:',repr(e),str(e)

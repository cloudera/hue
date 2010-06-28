#!/usr/bin/python

import sys,os,time,ldap

from ldap.ldapobject import LDAPObject
from ldapurl import LDAPUrl

try:
  ldap_url = LDAPUrl(sys.argv[1])
  num_tests = int(sys.argv[2])
except IndexError:
  print 'Usage: pref_test.py <LDAP URL> <number of tests>'
  sys.exit(1)

iter = num_tests
start_time = time.time()

l = LDAPObject(ldap_url.initializeUrl(),trace_level=0)
l.protocol_version = 3
l.simple_bind_s(ldap_url.who or '',ldap_url.cred or '')

while iter:

  l.search_s(
    ldap_url.dn,
    ldap_url.scope or ldap.SCOPE_BASE,
    ldap_url.filterstr or '(objectClass=*)',
    ldap_url.attrs or ['*']
  )

  iter -= 1

end_time = time.time()
l.unbind_s()
del l
print 'Reusing connection:',end_time-start_time

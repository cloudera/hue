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

while iter:

  l = LDAPObject(ldap_url.initializeUrl(),trace_level=0)
  l.protocol_version = 3
  l.simple_bind_s(ldap_url.who or '',ldap_url.cred or '')
  l.search_s(
    ldap_url.dn,
    ldap_url.scope or ldap.SCOPE_BASE,
    ldap_url.filterstr or '(objectClass=*)',
    ldap_url.attrs or ['*']
  )
  l.unbind_s()
  del l

  iter -= 1

end_time = time.time()
print 'Opening connection each time:',end_time-start_time


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


iter = num_tests
start_time = time.time()

while iter:

  os.system('ldapsearch -x -H "%s" -b "%s" -s %s "%s" %s > /dev/null' % (
    ldap_url.initializeUrl(),
    ldap_url.dn,
    {0:'base',1:'one',2:'sub'}[ldap_url.scope or ldap.SCOPE_BASE],
    ldap_url.filterstr or '(objectClass=*)',
    ' '.join(ldap_url.attrs or [])
  ))

  iter -= 1

end_time = time.time()
print 'Using ldapsearch:',end_time-start_time

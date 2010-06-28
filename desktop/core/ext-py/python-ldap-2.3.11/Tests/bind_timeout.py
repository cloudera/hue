#!/usr/bin/python

import sys,os,time,ldap

from ldap.ldapobject import LDAPObject
from ldapurl import LDAPUrl

try:
  ldap_url = LDAPUrl(sys.argv[1])
  num_tests = int(sys.argv[2])
  wait_period = float(sys.argv[3])
except (IndexError,ValueError):
  print 'Usage: pref_test.py <LDAP URL> <number of tests> <pause [sec]>'
  sys.exit(1)

iter = num_tests

while iter:

  start_time = time.time()

  try:
    l = LDAPObject(ldap_url.initializeUrl(),trace_level=2)
    l.protocol_version = 3
    l.network_timeout = 2.5
    l.simple_bind_s(ldap_url.who or '',ldap_url.cred or '')

    l.search_s(
      ldap_url.dn,
      ldap_url.scope or ldap.SCOPE_BASE,
      ldap_url.filterstr or '(objectClass=*)',
      ldap_url.attrs or ['*']
    )
    l.unbind_s()
    del l
  except ldap.LDAPError,e:
    print repr(e),str(e)

  end_time = time.time()
  print 'Timeout:',end_time-start_time

  time.sleep(wait_period)

  iter -= 1


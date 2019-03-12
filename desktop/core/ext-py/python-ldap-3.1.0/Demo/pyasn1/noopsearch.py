# -*- coding: utf-8 -*-
"""
Demo script for counting searching with OpenLDAP's no-op control

See https://www.python-ldap.org/ for project details.
This needs the following software:
Python
pyasn1
pyasn1-modules
python-ldap 2.4+
"""
from __future__ import print_function

import sys,ldap,ldapurl,getpass

from ldap.controls.openldap import SearchNoOpControl

SEARCH_TIMEOUT=30.0

try:
  ldap_url = ldapurl.LDAPUrl(sys.argv[1])
except IndexError:
  print('Usage: noopsearch.py <LDAP URL>')
  sys.exit(1)

# Set debugging level
#ldap.set_option(ldap.OPT_DEBUG_LEVEL,255)
ldapmodule_trace_level = 2
ldapmodule_trace_file = sys.stderr

ldap_conn = ldap.ldapobject.LDAPObject(
  ldap_url.initializeUrl(),
  trace_level=ldapmodule_trace_level,
  trace_file=ldapmodule_trace_file
)

if ldap_url.who and ldap_url.cred is None:
  print('Password for %s:' % (repr(ldap_url.who)))
  ldap_url.cred = getpass.getpass()

try:
  ldap_conn.simple_bind_s(ldap_url.who or '',ldap_url.cred or '')

except ldap.INVALID_CREDENTIALS as e:
  print('Simple bind failed:',str(e))
  sys.exit(1)

try:
  msg_id = ldap_conn.search_ext(
    ldap_url.dn,
    ldap_url.scope,
    filterstr=ldap_url.filterstr or '(objectClass=*)',
    attrlist=['1.1'],
    timeout=SEARCH_TIMEOUT,
    serverctrls=[SearchNoOpControl(criticality=True)],
  )
  _,_,_,search_response_ctrls = ldap_conn.result3(msg_id,all=1,timeout=SEARCH_TIMEOUT)
except (
  ldap.TIMEOUT,
  ldap.TIMELIMIT_EXCEEDED,
  ldap.SIZELIMIT_EXCEEDED,
  ldap.ADMINLIMIT_EXCEEDED) as e:
  ldap_conn.abandon(msg_id)
  sys.exit(1)


noop_srch_ctrl = [
  c
  for c in search_response_ctrls
  if c.controlType==SearchNoOpControl.controlType
][0]

print('Number of search results: %d' % noop_srch_ctrl.numSearchResults)
print('Number of search continuations: %d' % noop_srch_ctrl.numSearchContinuations)

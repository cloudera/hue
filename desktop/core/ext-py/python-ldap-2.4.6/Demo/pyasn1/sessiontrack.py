#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
demo_track_ldap_session.py

Client-seitige Demo-Implementierung von Session Tracking Control

http://tools.ietf.org/html/draft-wahl-ldap-session-03
"""

__version__ = '0.1'

import sys,getpass,ldap,ldapurl

from ldap.controls.sessiontrack import SessionTrackingControl,SESSION_TRACKING_FORMAT_OID_USERNAME

try:
  ldap_url = ldapurl.LDAPUrl(sys.argv[1])
except IndexError,ValueError:
  print 'Usage: %s <LDAP URL>' % (sys.argv[0])
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
  print 'Password for %s:' % (repr(ldap_url.who))
  ldap_url.cred = getpass.getpass()

try:
  ldap_conn.simple_bind_s(ldap_url.who or '',ldap_url.cred or '')

except ldap.INVALID_CREDENTIALS,e:
  print 'Simple bind failed:',str(e)
  sys.exit(1)

st_ctrl = SessionTrackingControl(
  '192.0.2.1',
  'app.example.com',
  SESSION_TRACKING_FORMAT_OID_USERNAME,
  'bloggs'
)

ldap_conn.search_ext_s(
  ldap_url.dn or '',
  ldap_url.scope or ldap.SCOPE_SUBTREE,
  ldap_url.filterstr or '(objectClass=*)',
  ldap_url.attrs or ['*'],
  serverctrls=[st_ctrl]
)


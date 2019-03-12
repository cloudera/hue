# -*- coding: utf-8 -*-
"""
Demo script for Persistent Search Control
(see https://tools.ietf.org/html/draft-ietf-ldapext-psearch)

See https://www.python-ldap.org/ for project details.
This needs the following software:
Python
pyasn1
pyasn1-modules
python-ldap 2.4+
"""
from __future__ import print_function

import sys,ldap,ldapurl,getpass

from ldap.controls.psearch import PersistentSearchControl,EntryChangeNotificationControl,CHANGE_TYPES_STR

try:
  ldap_url = ldapurl.LDAPUrl(sys.argv[1])
except IndexError:
  print('Usage: psearch.py <LDAP URL>')
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

if ldap_url.cred is None:
  print('Password for %s:' % (repr(ldap_url.who)))
  ldap_url.cred = getpass.getpass()

try:
  ldap_conn.simple_bind_s(ldap_url.who,ldap_url.cred)

except ldap.INVALID_CREDENTIALS as e:
  print('Simple bind failed:',str(e))
  sys.exit(1)

psc = PersistentSearchControl()

msg_id = ldap_conn.search_ext(
  ldap_url.dn,
  ldap_url.scope,
  ldap_url.filterstr,
  attrlist = ldap_url.attrs or ['*','+'],
  serverctrls=[psc],
)

while True:
  try:
    res_type,res_data,res_msgid,_,_,_ = ldap_conn.result4(
      msg_id,
      all=0,
      timeout=10.0,
      add_ctrls=1,
      add_intermediates=1,
      resp_ctrl_classes={EntryChangeNotificationControl.controlType:EntryChangeNotificationControl},
    )
  except ldap.TIMEOUT:
    print('Timeout waiting for results...')
  else:
    for dn,entry,srv_ctrls in res_data:
      ecn_ctrls = [
        c
        for c in srv_ctrls
        if c.controlType == EntryChangeNotificationControl.controlType
      ]

      if ecn_ctrls:
        changeType,previousDN,changeNumber = ecn_ctrls[0].changeType,ecn_ctrls[0].previousDN,ecn_ctrls[0].changeNumber
        change_type_desc = CHANGE_TYPES_STR[changeType]
        print('changeType: %s (%d), changeNumber: %s, previousDN: %s' % (change_type_desc,changeType,changeNumber,repr(previousDN)))

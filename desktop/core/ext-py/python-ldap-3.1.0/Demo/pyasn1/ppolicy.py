# -*- coding: utf-8 -*-
"""
Demo script for Password Policy Controls
(see https://tools.ietf.org/html/draft-behera-ldap-password-policy)

This needs the following software:
Python
pyasn1
pyasn1-modules
python-ldap 2.4+
"""
from __future__ import print_function

import sys,ldap,ldapurl,getpass

from ldap.controls.ppolicy import PasswordPolicyError,PasswordPolicyControl

try:
  ldap_url = ldapurl.LDAPUrl(sys.argv[1])
except (IndexError,ValueError):
  print('Usage: ppolicy.py <LDAP URL>')
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
  msgid = ldap_conn.simple_bind(ldap_url.who,ldap_url.cred,serverctrls=[PasswordPolicyControl()])
  res_type,res_data,res_msgid,res_ctrls = ldap_conn.result3(msgid)
except ldap.INVALID_CREDENTIALS as e:
  print('Simple bind failed:',str(e))
  sys.exit(1)
else:
  if res_ctrls[0].controlType==PasswordPolicyControl.controlType:
    ppolicy_ctrl = res_ctrls[0]
    print('PasswordPolicyControl')
    print('error',repr(ppolicy_ctrl.error),(ppolicy_ctrl.error!=None)*repr(PasswordPolicyError(ppolicy_ctrl.error)))
    print('timeBeforeExpiration',repr(ppolicy_ctrl.timeBeforeExpiration))
    print('graceAuthNsRemaining',repr(ppolicy_ctrl.graceAuthNsRemaining))

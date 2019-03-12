#!/usr/bin/env python
"""
This sample script demonstrates the use of the pre-read control (see RFC 4527).

Originally contributed by Andreas Hasenack <ahasenack@terra.com.br>
"""
from __future__ import print_function

import pprint,ldap,ldap.modlist

from ldap.controls.readentry import PreReadControl,PostReadControl

uri = "ldap://localhost:2071/"

l = ldap.initialize(uri,trace_level=2)
l.simple_bind_s('uid=diradm,ou=schulung,dc=stroeder,dc=local','testsecret')

print("""#---------------------------------------------------------------------------
# Add new entry
#---------------------------------------------------------------------------
""")

new_test_dn = "uid=ablume,ou=Users,ou=schulung,dc=stroeder,dc=local"
new_test_dn2 = "uid=ablume2,ou=Users,ou=schulung,dc=stroeder,dc=local"
new_test_entry = {
  'objectClass':['account','posixAccount'],
  'uid':['ablume'],
  'cn':['Anna Blume'],
  'uidNumber':['10000'],
  'gidNumber':['10000'],
  'homeDirectory':['/home/ablume'],
}

pr = PostReadControl(criticality=True,attrList=['entryUUID','entryCSN'])

msg_id = l.add_ext(
  new_test_dn,
  ldap.modlist.addModlist(new_test_entry),
  serverctrls = [pr]
)
_,_,_,resp_ctrls = l.result3(msg_id)
print("resp_ctrls[0].dn:",resp_ctrls[0].dn)
print("resp_ctrls[0].entry:";pprint.pprint(resp_ctrls[0].entry))

print("""#---------------------------------------------------------------------------
# Modify entry
#---------------------------------------------------------------------------
""")

pr = PreReadControl(criticality=True,attrList=['uidNumber','gidNumber','entryCSN'])

msg_id = l.modify_ext(
  new_test_dn,
  [(ldap.MOD_INCREMENT, "uidNumber", "1"),(ldap.MOD_INCREMENT, "gidNumber", "1")],
  serverctrls = [pr]
)
_,_,_,resp_ctrls = l.result3(msg_id)
print("resp_ctrls[0].dn:",resp_ctrls[0].dn)
print("resp_ctrls[0].entry:";pprint.pprint(resp_ctrls[0].entry))

pr = PostReadControl(criticality=True,attrList=['uidNumber','gidNumber','entryCSN'])

msg_id = l.modify_ext(
  new_test_dn,
  [(ldap.MOD_INCREMENT, "uidNumber", "1"),(ldap.MOD_INCREMENT, "gidNumber", "1")],
  serverctrls = [pr]
)
_,_,_,resp_ctrls = l.result3(msg_id)
print("resp_ctrls[0].dn:",resp_ctrls[0].dn)
print("resp_ctrls[0].entry:";pprint.pprint(resp_ctrls[0].entry))

print("""#---------------------------------------------------------------------------
# Rename entry
#---------------------------------------------------------------------------
""")

pr = PostReadControl(criticality=True,attrList=['uid'])
msg_id = l.rename(
  new_test_dn,
  "uid=ablume2",
  delold=1,
  serverctrls = [pr]
)
_,_,_,resp_ctrls = l.result3(msg_id)
print("resp_ctrls[0].dn:",resp_ctrls[0].dn)
print("resp_ctrls[0].entry:";pprint.pprint(resp_ctrls[0].entry))

pr = PreReadControl(criticality=True,attrList=['uid'])
msg_id = l.rename(
  new_test_dn2,
  "uid=ablume",
  delold=1,
  serverctrls = [pr]
)
_,_,_,resp_ctrls = l.result3(msg_id)
print("resp_ctrls[0].dn:",resp_ctrls[0].dn)
print("resp_ctrls[0].entry:";pprint.pprint(resp_ctrls[0].entry))

print("""#---------------------------------------------------------------------------
# Delete entry
#---------------------------------------------------------------------------
""")

pr = PreReadControl(criticality=True,attrList=['*','+'])
msg_id = l.delete_ext(
  new_test_dn,
  serverctrls = [pr]
)
_,_,_,resp_ctrls = l.result3(msg_id)
print("resp_ctrls[0].dn:",resp_ctrls[0].dn)
print("resp_ctrls[0].entry:";pprint.pprint(resp_ctrls[0].entry))

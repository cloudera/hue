#!/usr/bin/env python
"""
This sample script demonstrates the use of the pre-read control (see RFC 4527).

Originally contributed by Andreas Hasenack <ahasenack@terra.com.br>

Requires module pyasn1 (see http://pyasn1.sourceforge.net/)
"""

import ldap
from pyasn1.type import univ
from pyasn1.codec.der import encoder
from ldap.controls import LDAPControl

class LDAPString(univ.OctetString): pass

class AttributeSelection(univ.SequenceOf):
    componentType = LDAPString("")

class PreReadControl(LDAPControl):
  """
  Pre-Read LDAP Control

  see RFC 4527
  """

  controlType = ldap.LDAP_CONTROL_PRE_READ

  def __init__(self, criticality, controlValue=None,encodedControlValue=None):
    LDAPControl.__init__(self, self.controlType, criticality, controlValue, encodedControlValue)

  def encodeControlValue(self, value):
    attributeSelection = AttributeSelection()
    for i in range(len(value)):
      attributeSelection.setComponentByPosition(i, value[i])
    res = encoder.encode(attributeSelection)
    return res

  def decodeControlValue(self, value):
    # XXX
    return repr(value)


uri = "ldap://localhost:389"
base = "dc=example,dc=com"
scope = ldap.SCOPE_SUBTREE
filter = "(objectClass=sambaUnixIdPool)"

ld = ldap.initialize(uri)
ld.protocol_version = ldap.VERSION3
ld.bind_s("uid=LDAP Admin,ou=System Accounts,dc=example,dc=com", "ldapadmin")

pr = PreReadControl(criticality=True, controlValue=['uidNumber','gidNumber'])
modlist = [(ldap.MOD_INCREMENT, "uidNumber", "1"),(ldap.MOD_INCREMENT, "gidNumber", "1")]
msg = ld.modify_ext("cn=unixIdPool,dc=example,dc=com", modlist, serverctrls = [pr])

res = ld.result3(msgid = msg, timeout = -1)
print "res:", res

# -*- coding: utf-8 -*-
"""
ldap.controls.ppolicy - classes for Password Policy controls
(see http://tools.ietf.org/html/draft-behera-ldap-password-policy)

See http://www.python-ldap.org/ for project details.

$Id: ppolicy.py,v 1.3 2011/11/27 15:26:06 stroeder Exp $
"""

__all__ = [
  'PasswordPolicyControl'
]

# Imports from python-ldap 2.4+
import ldap.controls
from ldap.controls import RequestControl,ResponseControl,ValueLessRequestControl,KNOWN_RESPONSE_CONTROLS

# Imports from pyasn1
from pyasn1.type import tag,namedtype,namedval,univ,constraint
from pyasn1.codec.ber import encoder,decoder
from pyasn1_modules.rfc2251 import LDAPDN


class PasswordPolicyWarning(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.NamedType('timeBeforeExpiration',univ.Integer().subtype(
      implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,0)
    )),
    namedtype.NamedType('graceAuthNsRemaining',univ.Integer().subtype(
      implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,1)
    )),
  )


class PasswordPolicyError(univ.Enumerated):
  namedValues = namedval.NamedValues(
    ('passwordExpired',0),
    ('accountLocked',1),
    ('changeAfterReset',2),
    ('passwordModNotAllowed',3),
    ('mustSupplyOldPassword',4),
    ('insufficientPasswordQuality',5),
    ('passwordTooShort',6),
    ('passwordTooYoung',7),
    ('passwordInHistory',8)
  )
  subtypeSpec = univ.Enumerated.subtypeSpec + constraint.SingleValueConstraint(0,1,2,3,4,5,6,7,8)


class PasswordPolicyResponseValue(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType(
      'warning',
      PasswordPolicyWarning().subtype(
        implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,0)
      ),
    ),
    namedtype.OptionalNamedType(
      'error',PasswordPolicyError().subtype(
        implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,1)
      )
    ),
  )


class PasswordPolicyControl(ValueLessRequestControl,ResponseControl):
  controlType = '1.3.6.1.4.1.42.2.27.8.5.1'

  def __init__(self,criticality=False):
    self.criticality = criticality

  def decodeControlValue(self,encodedControlValue):
    ppolicyValue,_ = decoder.decode(encodedControlValue,asn1Spec=PasswordPolicyResponseValue())
    warning = ppolicyValue.getComponentByName('warning')
    if warning is None:
      self.timeBeforeExpiration,self.graceAuthNsRemaining = None,None
    else:
      timeBeforeExpiration = warning.getComponentByName('timeBeforeExpiration')
      if timeBeforeExpiration!=None:
        self.timeBeforeExpiration = int(timeBeforeExpiration)
      else:
        self.timeBeforeExpiration = None
      graceAuthNsRemaining = warning.getComponentByName('graceAuthNsRemaining')
      if graceAuthNsRemaining!=None:
        self.graceAuthNsRemaining = int(graceAuthNsRemaining)
      else:
        self.graceAuthNsRemaining = None
    error = ppolicyValue.getComponentByName('error')
    if error is None:
      self.error = None
    else:
      self.error = int(error)
      

KNOWN_RESPONSE_CONTROLS[PasswordPolicyControl.controlType] = PasswordPolicyControl

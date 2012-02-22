"""
controls.py - support classes for LDAP controls

See http://www.python-ldap.org/ for details.

\$Id: controls.py,v 1.7 2009/07/26 11:09:58 stroeder Exp $

Description:
The ldap.controls module provides LDAPControl classes.
Each class provides support for a certain control.
"""

from ldap import __version__

__all__ = [
  'LDAPControl',
]


from types import ClassType

import _ldap,ldap


class LDAPControl:
  """
  Base class for all LDAP controls
  """

  def __init__(self,controlType,criticality,controlValue=None,encodedControlValue=None):
    self.controlType = controlType
    self.criticality = criticality
    self.controlValue = controlValue or self.decodeControlValue(encodedControlValue)

  def __repr__(self):
    return '%s(%s,%s,%s)' % (self.__class__.__name__,self.controlType,self.criticality,self.controlValue)

  def encodeControlValue(self,value):
    return value

  def decodeControlValue(self,encodedValue):
    return encodedValue

  def getEncodedTuple(self):
    return (self.controlType,self.criticality,self.encodeControlValue(self.controlValue))


class BooleanControl(LDAPControl):
  """
  Base class for simple controls with booelan control value

  In this base class controlValue has to be passed as
  boolean type (True/False or 1/0).
  """
  boolean2ber = { 1:'\x01\x01\xFF', 0:'\x01\x01\x00' }
  ber2boolean = { '\x01\x01\xFF':1, '\x01\x01\x00':0 }

  def encodeControlValue(self,value):
    return self.boolean2ber[int(value)]

  def decodeControlValue(self,encodedValue):
    return self.ber2boolean[encodedValue]


class SimplePagedResultsControl(LDAPControl):
  """
  LDAP Control Extension for Simple Paged Results Manipulation

  see RFC 2696
  """
  controlType = ldap.LDAP_CONTROL_PAGE_OID

  def __init__(self,controlType,criticality,controlValue=None,encodedControlValue=None):
    LDAPControl.__init__(self,ldap.LDAP_CONTROL_PAGE_OID,criticality,controlValue,encodedControlValue)

  def encodeControlValue(self,value):
    size,cookie = value
    return _ldap.encode_page_control(size,cookie)

  def decodeControlValue(self,encodedValue):
    size,cookie = _ldap.decode_page_control(encodedValue)
    return size,cookie


class MatchedValuesControl(LDAPControl):
  """
  LDAP Matched Values control, as defined in RFC 3876

  from ldap.controls import MatchedValuesControl
  control = MatchedValuesControl(criticality, filter)
  """
  
  controlType = ldap.LDAP_CONTROL_VALUESRETURNFILTER
  
  def __init__(self, criticality, controlValue=None):
    LDAPControl.__init__(self, self.controlType, criticality, controlValue, None) 

  def encodeControlValue(self, value):
    return _ldap.encode_valuesreturnfilter_control(value)


def EncodeControlTuples(ldapControls):
  """
  Return list of readily encoded 3-tuples which can be directly
  passed to C module _ldap
  """
  if ldapControls is None:
    return None
  else:
    result = [
      c.getEncodedTuple()
      for c in ldapControls
    ]
    return result


def DecodeControlTuples(ldapControlTuples):
  """
  Return list of readily encoded 3-tuples which can be directly
  passed to C module _ldap
  """
  return [
    knownLDAPControls.get(controlType,LDAPControl)
      (controlType,criticality,encodedControlValue=encodedControlValue)
    for controlType,criticality,encodedControlValue in ldapControlTuples or []
  ]

# Build a dictionary of known LDAPControls
knownLDAPControls = {}
for symbol_name in dir():
  c = eval(symbol_name)
  if type(c) is ClassType and hasattr(c,'controlType'):
    knownLDAPControls[c.controlType] = c

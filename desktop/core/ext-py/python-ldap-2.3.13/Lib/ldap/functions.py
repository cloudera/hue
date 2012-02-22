"""
functions.py - wraps functions of module _ldap

See http://www.python-ldap.org/ for details.

\$Id: functions.py,v 1.26 2010/06/03 12:26:39 stroeder Exp $

Compability:
- Tested with Python 2.0+ but should work with Python 1.5.x
- functions should behave exactly the same like in _ldap

Usage:
Directly imported by ldap/__init__.py. The symbols of _ldap are
overridden.

Thread-lock:
Basically calls into the LDAP lib are serialized by the module-wide
lock _ldapmodule_lock.
"""

from ldap import __version__

__all__ = [
  'open','initialize','init',
  'explode_dn','explode_rdn',
  'get_option','set_option',
]

import sys,_ldap,ldap

from ldap import LDAPError

from ldap.dn import explode_dn,explode_rdn

from ldap.ldapobject import LDAPObject

if __debug__:
  # Tracing is only supported in debugging mode
  import traceback


def _ldap_function_call(lock,func,*args,**kwargs):
  """
  Wrapper function which locks and logs calls to function

  lock
      Instance of threading.Lock or compatible
  func
      Function to call with arguments passed in via *args and **kwargs
  """
  if lock:
    lock.acquire()
  if __debug__:
    if ldap._trace_level>=1:
      ldap._trace_file.write('*** %s.%s (%s,%s)\n' % (
        '_ldap',repr(func),
        repr(args),repr(kwargs)
      ))
      if ldap._trace_level>=3:
        traceback.print_stack(limit=ldap._trace_stack_limit,file=ldap._trace_file)
  try:
    try:
      result = func(*args,**kwargs)
    finally:
      if lock:
        ldap._ldap_module_lock.release()
  except LDAPError,e:
    if __debug__ and ldap._trace_level>=2:
      ldap._trace_file.write('=> LDAPError: %s\n' % (str(e)))
    raise
  if __debug__ and ldap._trace_level>=2:
    if result!=None and result!=(None,None):
      ldap._trace_file.write('=> result: %s\n' % (repr(result)))
  return result


def initialize(uri,trace_level=0,trace_file=sys.stdout,trace_stack_limit=None):
  """
  Return LDAPObject instance by opening LDAP connection to
  LDAP host specified by LDAP URL

  Parameters:
  uri
        LDAP URL containing at least connection scheme and hostport,
        e.g. ldap://localhost:389
  trace_level
        If non-zero a trace output of LDAP calls is generated.
  trace_file
        File object where to write the trace output to.
        Default is to use stdout.
  """
  return LDAPObject(uri,trace_level,trace_file,trace_stack_limit)


def open(host,port=389,trace_level=0,trace_file=sys.stdout,trace_stack_limit=None):
  """
  Return LDAPObject instance by opening LDAP connection to
  specified LDAP host

  Parameters:
  host
        LDAP host and port, e.g. localhost
  port
        integer specifying the port number to use, e.g. 389
  trace_level
        If non-zero a trace output of LDAP calls is generated.
  trace_file
        File object where to write the trace output to.
        Default is to use stdout.
  """
  import warnings
  warnings.warn('ldap.open() is deprecated! Use ldap.initialize() instead.', DeprecationWarning,2)
  return initialize('ldap://%s:%d' % (host,port),trace_level,trace_file,trace_stack_limit)

init = open


def get_option(option):
  """
  get_option(name) -> value

  Get the value of an LDAP global option.
  """
  return _ldap_function_call(None,_ldap.get_option,option)


def set_option(option,invalue):
  """
  set_option(name, value)

  Set the value of an LDAP global option.
  """
  return _ldap_function_call(None,_ldap.set_option,option,invalue)

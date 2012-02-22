"""
ldap - base module

See http://www.python-ldap.org/ for details.

$Id: __init__.py,v 1.70 2011/02/19 14:36:53 stroeder Exp $
"""

# This is also the overall release version number

__version__ = '2.3.13'

import sys

if __debug__:
  # Tracing is only supported in debugging mode
  import traceback
  _trace_level = 0
  _trace_file = sys.stderr
  _trace_stack_limit = None

from _ldap import *

class DummyLock:
  """Define dummy class with methods compatible to threading.Lock"""
  def __init__(self):
    pass
  def acquire(self):
    pass
  def release(self):
    pass

try:
  # Check if Python installation was build with thread support
  import thread
except ImportError:
  LDAPLockBaseClass = DummyLock
else:
  import threading
  LDAPLockBaseClass = threading.Lock


class LDAPLock:
  """
  Mainly a wrapper class to log all locking events.
  Note that this cumbersome approach with _lock attribute was taken
  since threading.Lock is not suitable for sub-classing.
  """
  _min_trace_level = 2

  def __init__(self,lock_class=None,desc=''):
    """
    lock_class
        Class compatible to threading.Lock
    desc
        Description shown in debug log messages
    """
    self._desc = desc
    self._lock = (lock_class or LDAPLockBaseClass)()

  def acquire(self):
    if __debug__:
      if _trace_level>=self._min_trace_level:
        _trace_file.write('***%s %s.acquire()\n' % (self._desc,self.__class__.__name__))
    return self._lock.acquire()

  def release(self):
    if __debug__:
      if _trace_level>=self._min_trace_level:
        _trace_file.write('***%s %s.release()\n' % (self._desc,self.__class__.__name__))
    return self._lock.release()


# Create module-wide lock for serializing all calls into underlying LDAP lib
_ldap_module_lock = LDAPLock(desc='Module wide')

from functions import open,initialize,init,get_option,set_option

from ldap.dn import explode_dn,explode_rdn,str2dn,dn2str
del str2dn
del dn2str

# More constants

# For compability of 2.3 and 2.4 OpenLDAP API
OPT_DIAGNOSTIC_MESSAGE = OPT_ERROR_STRING

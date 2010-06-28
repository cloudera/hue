"""
ldap - base module

See http://www.python-ldap.org/ for details.

$Id: __init__.py,v 1.67 2009/12/03 22:11:26 stroeder Exp $
"""

# This is also the overall release version number

__version__ = '2.3.11'

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
  LDAPLock = DummyLock
else:
  import threading
  LDAPLock = threading.Lock

# Create module-wide lock for serializing all calls
# into underlying LDAP lib
_ldap_module_lock = LDAPLock()

from functions import open,initialize,init,get_option,set_option

from ldap.dn import explode_dn,explode_rdn,str2dn,dn2str
del str2dn
del dn2str

# More constants

# For compability of 2.3 and 2.4 OpenLDAP API
OPT_DIAGNOSTIC_MESSAGE = OPT_ERROR_STRING

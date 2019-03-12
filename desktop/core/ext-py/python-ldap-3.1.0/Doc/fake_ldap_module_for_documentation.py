"""
A module that mocks `_ldap` for the purposes of generating documentation

This module provides placeholders for the contents of `_ldap`, making it
possible to generate documentation even _ldap is not compiled.
It should also make the documentation independent of which features are
available in the system OpenLDAP library.

The overly long module name will show up in AttributeError messages,
hinting that this is not the actual _ldap.

See https://www.python-ldap.org/ for details.
"""

import sys

# Cause `import _ldap` to import this module instead of the actual `_ldap`.
sys.modules['_ldap'] = sys.modules[__name__]

from constants import CONSTANTS
from pkginfo import __version__

for constant in CONSTANTS:
    globals()[constant.name] = constant

def get_option(num):
    pass

class LDAPError:
    pass

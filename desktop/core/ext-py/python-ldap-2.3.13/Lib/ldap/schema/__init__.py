"""
ldap.schema -  LDAPv3 schema handling

See http://www.python-ldap.org/ for details.

\$Id: __init__.py,v 1.7 2009/07/26 11:09:58 stroeder Exp $
"""

from ldap import __version__

from ldap.schema.subentry import SubSchema,SCHEMA_ATTRS,SCHEMA_CLASS_MAPPING,SCHEMA_ATTR_MAPPING,urlfetch
from ldap.schema.models import *

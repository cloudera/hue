from __future__ import print_function
import ldap
from getpass import getpass

# Create LDAPObject instance
l = ldap.initialize('ldap://localhost:1389',trace_level=1)

print('Password:')
cred = getpass()

try:

  # Set LDAP protocol version used
  l.set_option(ldap.OPT_PROTOCOL_VERSION,3)

  # Try a bind to provoke failure if protocol version is not supported
  l.bind_s('cn=root,dc=stroeder,dc=com',cred,ldap.AUTH_SIMPLE)

  print('Using rename_s():')

  l.rename_s(
    'uid=fred,ou=Unstructured testing tree,dc=stroeder,dc=com',
    'cn=Fred Feuerstein',
    'dc=stroeder,dc=com',
    0
  )

  l.rename_s(
    'cn=Fred Feuerstein,dc=stroeder,dc=com',
    'uid=fred',
    'ou=Unstructured testing tree,dc=stroeder,dc=com',
    0
  )

  m = l.rename(
    'uid=fred,ou=Unstructured testing tree,dc=stroeder,dc=com',
    'cn=Fred Feuerstein',
    'dc=stroeder,dc=com',
    0
  )
  r = l.result(m,1)

  m = l.rename(
    'cn=Fred Feuerstein,dc=stroeder,dc=com',
    'uid=fred',
    'ou=Unstructured testing tree,dc=stroeder,dc=com',
    0
  )
  r = l.result(m,1)

finally:

  l.unbind_s()

import sys,ldap,ldap.async

l = ldap.initialize('ldap://localhost:1390',trace_level=2)

s = ldap.async.LDIFWriter(l,sys.stdout)

s.startSearch(
  'dc=stroeder,dc=de',
  ldap.SCOPE_SUBTREE,
  '(objectClass=*)',['objectClass']
)

s.processResults()

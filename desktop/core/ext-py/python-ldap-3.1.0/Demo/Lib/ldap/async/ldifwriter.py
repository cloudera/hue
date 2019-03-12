"""
ldifwriter - using ldap.async module for output of LDIF stream
             of LDAP search results

Written by Michael Stroeder <michael@stroeder.com>

This example translates the naming context of data read from
input, sanitizes some attributes, maps/removes object classes,
maps/removes attributes., etc. It's far from being complete though.
"""

import sys,ldap,ldap.async

s = ldap.async.LDIFWriter(
  ldap.initialize('ldap://localhost:1390'),
  sys.stdout
)

s.startSearch(
  'dc=stroeder,dc=de',
  ldap.SCOPE_SUBTREE,
  '(objectClass=*)',
)

try:
  partial = s.processResults()
except ldap.SIZELIMIT_EXCEEDED:
  sys.stderr.write('Warning: Server-side size limit exceeded.\n')
else:
  if partial:
    sys.stderr.write('Warning: Only partial results received.\n')

sys.stderr.write(
  '%d results received.\n' % (
    s.endResultBreak-s.beginResultsDropped
  )
)

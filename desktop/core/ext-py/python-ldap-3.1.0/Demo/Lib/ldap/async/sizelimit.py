"""
ldifwriter - using ldap.async module for retrieving partial results
             in a list even though the exception ldap.SIZELIMIT_EXCEEDED
             was raised.output of LDIF stream

Written by Michael Stroeder <michael@stroeder.com>

This example translates the naming context of data read from
input, sanitizes some attributes, maps/removes object classes,
maps/removes attributes., etc. It's far from being complete though.
"""

import sys,ldap,ldap.async

s = ldap.async.List(
  ldap.initialize('ldap://localhost:1390'),
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
    len(s.allResults)
  )
)

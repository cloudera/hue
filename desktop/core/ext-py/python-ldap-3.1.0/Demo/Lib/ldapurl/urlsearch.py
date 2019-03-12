"""
Do a search with the LDAP URL specified at command-line.

No output of LDAP data is produced except trace output.
"""
from __future__ import print_function
import sys,getpass,ldap,ldapurl

try:
  ldapUrl = ldapurl.LDAPUrl(ldapUrl=sys.argv[1])
except IndexError:
  print('Usage: %s [LDAP URL]' % (sys.argv[0]))
  sys.exit(1)

for a in [
  'urlscheme','hostport','dn','attrs','scope',
  'filterstr','extensions','who','cred'
]:
  print(a,repr(getattr(ldapUrl,a)))

l = ldap.initialize(ldapUrl.initializeUrl(),trace_level=1)
if ldapUrl.who!=None:
  if ldapUrl.cred!=None:
    cred=ldapUrl.cred
  else:
    print('Enter password for simple bind with',repr(ldapUrl.who))
    cred=getpass.getpass()
  l.simple_bind_s(ldapUrl.who,cred)

res = l.search_s(ldapUrl.dn,ldapUrl.scope,ldapUrl.filterstr,ldapUrl.attrs)

print(len(res),'search results')

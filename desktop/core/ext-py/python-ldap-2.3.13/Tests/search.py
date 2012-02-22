import sys,pprint,ldap

from ldap.ldapobject import LDAPObject
from ldapurl import LDAPUrl

class MyLDAPUrl(LDAPUrl):
  attr2extype = {
    'who':'bindname',
    'cred':'X-BINDPW',
    'start_tls':'startTLS',
    'trace_level':'trace',
  }


ldap_url = MyLDAPUrl(sys.argv[1])
trace_level = int(ldap_url.trace_level or '0')

print '***trace_level',trace_level

ldap.trace_level = trace_level

l = LDAPObject(
  ldap_url.initializeUrl(),
  trace_level=trace_level,
)

l.protocol_version = 3
l.set_option(ldap.OPT_REFERRALS,0)
l.simple_bind_s((ldap_url.who or ''),(ldap_url.cred or ''))

result = l.search_s(
  ldap_url.dn,
  ldap_url.scope or ldap.SCOPE_SUBTREE,
  ldap_url.filterstr or '(objectClass=*)',
  ldap_url.attrs or ['*']
)

pprint.pprint(result)

print '***DIAGNOSTIC_MESSAGE',repr(l.get_option(ldap.OPT_DIAGNOSTIC_MESSAGE))

l.unbind_s()

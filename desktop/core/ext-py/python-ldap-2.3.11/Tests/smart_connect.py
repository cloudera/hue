import sys,ldap

from ldap.ldapobject import SmartLDAPObject
from ldapurl import LDAPUrl

class MyLDAPUrl(LDAPUrl):
  attr2extype = {
    'who':'bindname',
    'cred':'X-BINDPW',
    'start_tls':'startTLS',
    'trace_level':'trace',
  }

ldap_url = MyLDAPUrl(sys.argv[1])
ldap.trace_level = int(ldap_url.start_tls or '1')

l = SmartLDAPObject(
  ldap_url.initializeUrl(),
  trace_level=int(ldap_url.trace_level or '0'),
  who=(ldap_url.who or ''),
  cred=(ldap_url.cred or ''),
  start_tls=int(ldap_url.start_tls or '1'),
)

print 'LDAPv%d connection' % (l.protocol_version)
print 'StartTLS %s' % ({0:'not used',1:'used'}[l.started_tls])

import sys,pprint,ldap,time

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

msgid = l.search(
  ldap_url.dn,
  ldap_url.scope or ldap.SCOPE_SUBTREE,
  ldap_url.filterstr or '(objectClass=*)',
  ldap_url.attrs or ['*']
)

print "msgid=",msgid
count = 0

result = l.result(msgid, True, 0)

while(result[0] != ldap.RES_SEARCH_RESULT):
  count += 1
  try:
    result = l.result(msgid,True,0.25)
  except ldap.TIMEOUT:
    continue
  else:
    if result[0]!=None:
      print '***len(result[1])',len(result[1])
#        pprint.pprint(result)
    else:
      print 'no result'
#    time.sleep(0.01)

l.unbind_s()

print 'count:',count


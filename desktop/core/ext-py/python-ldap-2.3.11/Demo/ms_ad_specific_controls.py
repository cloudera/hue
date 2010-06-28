import ldap,pprint

from ldap.controls import BooleanControl

ldap_uri = "ldap://172.16.15.10"
dn = "CN=Anna Blume,CN=Users,DC=dom2,DC=adtest,DC=local"
password = 'testsecret'
trace_level = 2
LDAP_SERVER_DOMAIN_SCOPE_OID='1.2.840.113556.1.4.1339'

l = ldap.initialize(ldap_uri,trace_level=trace_level)

# Switch off chasing referrals within OpenLDAP's libldap
l.set_option(ldap.OPT_REFERRALS, 0)

# Simple bind with user's DN and password
l.simple_bind_s(dn,password)

# Search without any controls
pprint.pprint(l.search_ext_s(
  'DC=dom2,DC=adtest,DC=local',
  ldap.SCOPE_ONELEVEL,
  '(objectClass=subentry)',
  ['*'],
  serverctrls = [],
))

# Search with LDAP_SERVER_DOMAIN_SCOPE_OID control (which has boolean value)
pprint.pprint(l.search_ext_s(
  'DC=dom2,DC=adtest,DC=local',
  ldap.SCOPE_ONELEVEL,
  '(objectClass=subentry)',
  ['*'],
  serverctrls = [
    BooleanControl(LDAP_SERVER_DOMAIN_SCOPE_OID,criticality=0,controlValue=1)
  ],
))

print 60*'#'

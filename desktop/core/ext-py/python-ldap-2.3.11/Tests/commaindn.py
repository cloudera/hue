import ldap,ldap.filter
conn = ldap.initialize('ldap://localhost:1390')
conn.set_option(ldap.VERSION, ldap.VERSION3)
MEMBER = 'cn=Jens\, Vagelpohl,cn=Users,dc=as,dc=zope,dc=com'
res = conn.search_s('dc=stroeder,dc=com', ldap.SCOPE_SUBTREE,
  ldap.filter.filter_format('(member=%s)',(MEMBER,))
)
conn.unbind_s()


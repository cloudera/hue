import ldap

l=ldap.initialize('ldap://localhost:1390')

print l.search_s('',0)

l.search_s('dc=stroeder,dc=com',1)


try:
  l.search_s('ou=not existent,dc=stroeder,dc=com',1)
except ldap.NO_SUCH_OBJECT,e:
  print str(e)

try:
  l.search_s('dc=stroeder,dc=com',2,'(objectclass')
except ldap.FILTER_ERROR,e:
  print str(e)



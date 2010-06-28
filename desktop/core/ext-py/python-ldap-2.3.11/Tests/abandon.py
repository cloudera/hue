import ldap

l=ldap.initialize('ldap://localhost:1390',trace_level=2)

m = l.search('dc=stroeder,dc=de',2)

r = l.result(m,0,0.1)
print r

l.abandon(m)


import ldap

l = ldap.initialize('ldap://172.16.44.1:1390')
l.protocol_version = 3

#l.simple_bind_s('','')

print l.search_s('',0,'(objectClass=*)',['*','+'])

print l.search_s('dc=stroeder,dc=de',2,'(cn=*michael*)',['cn'])


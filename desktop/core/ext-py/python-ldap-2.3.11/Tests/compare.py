import ldap

l=ldap.initialize('ldap://localhost:1390',trace_level=2)

l.protocol_version=3

l.bind_s('cn=Fred Feuerstein,ou=Testing,dc=stroeder,dc=de','secret')

l.compare_s('ou=Testing,dc=stroeder,dc=de','ou','Testing')


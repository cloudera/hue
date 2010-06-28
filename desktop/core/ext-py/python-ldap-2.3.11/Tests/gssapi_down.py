import ldap, ldap.sasl
l = ldap.initialize('ldap://d0017127.vmtestnetz.dpag.de')
l.sasl_interactive_bind_s('', ldap.sasl.gssapi())

# Here's the real work. The use of multiple search bases is key
for i in range(2000):
  try:
    for ou in ['Users','Computers','System']:
      dn = 'CN=%s,DC=VMTESTNETZ,DC=DPAG,DC=DE' % ou
      res = l.search_s(dn, ldap.SCOPE_ONELEVEL, '(objectClass=*)')
  except ldap.SERVER_DOWN:
    print 'Aborted after %d searches' % i
    break

import os,ldap,pickle

temp_file_name = os.path.join(os.environ.get('TMP','/tmp'),'pickle_ldap-%d' % (os.getpid()))

l1 = ldap.ldapobject.ReconnectLDAPObject('ldap://localhost:1390',trace_level=1)
l1.protocol_version = 3
l1.search_s('',ldap.SCOPE_BASE,'(objectClass=*)')

pickle.dump(l1,open(temp_file_name,'wb'))

l2 = pickle.load(open(temp_file_name,'rb'))
l2.search_s('',ldap.SCOPE_BASE,'(objectClass=*)')

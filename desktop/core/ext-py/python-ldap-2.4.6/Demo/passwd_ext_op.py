"""
Example showing the use of the password extended operation.
"""

import sys,ldap,ldapurl,getpass

# Set debugging level
ldap.set_option(ldap.OPT_DEBUG_LEVEL,255)
ldapmodule_trace_level = 2
ldapmodule_trace_file = sys.stderr

lu = ldapurl.LDAPUrl(sys.argv[1])

print 'Old password'
oldpw = getpass.getpass()
print 'New password'
newpw = getpass.getpass()

# Set path name of file containing all CA certificates
# needed to validate server certificates
ldap.set_option(ldap.OPT_X_TLS_CACERTFILE,'/etc/httpd/ssl.crt/myCA-cacerts.pem')

# Create LDAPObject instance
l = ldap.initialize(lu.initializeUrl(),trace_level=ldapmodule_trace_level,trace_file=ldapmodule_trace_file)

l.protocol_version=ldap.VERSION3

l.simple_bind_s(lu.dn,oldpw)

l.passwd(lu.dn,oldpw,newpw)

l.unbind_s()

"""
Various examples how to connect to a LDAP host with the new
factory function ldap.initialize() introduced in OpenLDAP 2 API.

Assuming you have LDAP servers running on
ldap://localhost:1390 (LDAP with StartTLS)
ldaps://localhost:1391 (LDAP over SSL)
ldapi://%2ftmp%2fopenldap2 (domain socket /tmp/openldap2)
"""

import sys,ldap

# Set debugging level
ldap.set_option(ldap.OPT_DEBUG_LEVEL,0)
ldapmodule_trace_level = 1
ldapmodule_trace_file = sys.stderr

# Complete path name of the file containing all trusted CA certs
CACERTFILE='/etc/apache2/ssl.crt/ca-bundle.crt'

# TLS-related options have to be set globally since the TLS context is only initialized once

# Force cert validation
ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT,ldap.OPT_X_TLS_DEMAND)
# Set path name of file containing all trusted CA certificates
ldap.set_option(ldap.OPT_X_TLS_CACERTFILE,CACERTFILE)


print """##################################################################
# LDAPv3 connection with StartTLS
##################################################################
"""

# Create LDAPObject instance
l = ldap.initialize('ldap://localhost:1390',trace_level=ldapmodule_trace_level,trace_file=ldapmodule_trace_file)

# Set LDAP protocol version used
l.protocol_version=ldap.VERSION3
# Force libldap to create a new SSL context
#l.set_option(ldap.OPT_X_TLS_NEWCTX,ldap.OPT_X_TLS_DEMAND)
# Force cert validation
#l.set_option(ldap.OPT_X_TLS_REQUIRE_CERT,ldap.OPT_X_TLS_DEMAND)
# Set path name of file containing all trusted CA certificates
#l.set_option(ldap.OPT_X_TLS_CACERTFILE,CACERTFILE)

# Now try StartTLS extended operation
l.start_tls_s()

# Try a bind to provoke failure if protocol version is not supported
l.simple_bind_s('','')

# Close connection
l.unbind_s()

print """##################################################################
# LDAPv3 connection over SSL
##################################################################
"""

# Create LDAPObject instance
l = ldap.initialize('ldaps://localhost:1391',trace_level=ldapmodule_trace_level,trace_file=ldapmodule_trace_file)

# Set LDAP protocol version used
l.protocol_version=ldap.VERSION3
# Force libldap to create a new SSL context
#l.set_option(ldap.OPT_X_TLS_NEWCTX,ldap.OPT_X_TLS_DEMAND)
# Force cert validation
#l.set_option(ldap.OPT_X_TLS_REQUIRE_CERT,ldap.OPT_X_TLS_DEMAND)
# Set path name of file containing all trusted CA certificates
#l.set_option(ldap.OPT_X_TLS_CACERTFILE,CACERTFILE)

# Try a bind to provoke failure if protocol version is not supported
l.simple_bind_s('','')

# Close connection
l.unbind_s()

print """##################################################################
# LDAPv3 connection over Unix domain socket
##################################################################
"""

# Create LDAPObject instance
l = ldap.initialize('ldapi://%2ftmp%2fopenldap-socket',trace_level=ldapmodule_trace_level,trace_file=ldapmodule_trace_file)
# Set LDAP protocol version used
l.protocol_version=ldap.VERSION3
# Try a bind to provoke failure if protocol version is not supported
l.bind_s('','',ldap.AUTH_SIMPLE)
# Close connection
l.unbind_s()


import ldap

ldap.set_option(ldap.OPT_DEREF,0)
print ldap.get_option(ldap.OPT_DEREF)
ldap.set_option(ldap.OPT_DEREF,1)
print ldap.get_option(ldap.OPT_DEREF)
ldap.set_option(ldap.OPT_DEREF,2)
print ldap.get_option(ldap.OPT_DEREF)

print ldap.get_option(ldap.OPT_TIMEOUT)
print ldap.get_option(ldap.OPT_NETWORK_TIMEOUT)
ldap.set_option(ldap.OPT_TIMEOUT,0.0)
print ldap.get_option(ldap.OPT_TIMEOUT)
ldap.set_option(ldap.OPT_NETWORK_TIMEOUT,0.0)
print ldap.get_option(ldap.OPT_NETWORK_TIMEOUT)
ldap.set_option(ldap.OPT_TIMEOUT,30.0)
print ldap.get_option(ldap.OPT_TIMEOUT)
ldap.set_option(ldap.OPT_NETWORK_TIMEOUT,30.0)
print ldap.get_option(ldap.OPT_NETWORK_TIMEOUT)

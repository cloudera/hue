Performance
===========

:class:`~django_auth_ldap.backend.LDAPBackend` is carefully designed not to
require a connection to the LDAP service for every request. Of course, this
depends heavily on how it is configured. If LDAP traffic or latency is a concern
for your deployment, this section has a few tips on minimizing it, in decreasing
order of impact.

#. **Cache groups**. If :setting:`AUTH_LDAP_FIND_GROUP_PERMS` is ``True``, the
   default behavior is to reload a user's group memberships on every request.
   This is the safest behavior, as any membership change takes effect
   immediately, but it is expensive. If possible, set
   :setting:`AUTH_LDAP_CACHE_GROUPS` to ``True`` to remove most of this traffic.

#. **Don't access user.ldap_user.***. Except for ``ldap_user.dn``, these
   properties are only cached on a per-request basis. If you can propagate LDAP
   attributes to a :class:`~django.contrib.auth.models.User`, they will only be
   updated at login. ``user.ldap_user.attrs`` triggers an LDAP connection for
   every request in which it's accessed.

#. **Use simpler group types**. Some grouping mechanisms are more expensive than
   others. This will often be outside your control, but it's important to note
   that the extra functionality of more complex group types like
   :class:`~django_auth_ldap.config.NestedGroupOfNamesType` is not free and will
   generally require a greater number and complexity of LDAP queries.

#. **Use direct binding**. Binding with :setting:`AUTH_LDAP_USER_DN_TEMPLATE` is
   a little bit more efficient than relying on :setting:`AUTH_LDAP_USER_SEARCH`.
   Specifically, it saves two LDAP operations (one bind and one search) per
   login.

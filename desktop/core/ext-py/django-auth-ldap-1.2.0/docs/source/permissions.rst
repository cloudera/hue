Permissions
===========

Groups are useful for more than just populating the user's ``is_*`` fields.
:class:`~django_auth_ldap.backend.LDAPBackend` would not be complete without
some way to turn a user's LDAP group memberships into Django model permissions.
In fact, there are two ways to do this.

Ultimately, both mechanisms need some way to map LDAP groups to Django groups.
Implementations of :class:`~django_auth_ldap.config.LDAPGroupType` will have an
algorithm for deriving the Django group name from the LDAP group. Clients that
need to modify this behavior can subclass the
:class:`~django_auth_ldap.config.LDAPGroupType` class. All of the built-in
implementations take a ``name_attr`` argument to ``__init__``, which
specifies the LDAP attribute from which to take the Django group name. By
default, the ``cn`` attribute is used.


Using Groups Directly
---------------------

The least invasive way to map group permissions is to set
:setting:`AUTH_LDAP_FIND_GROUP_PERMS` to ``True``.
:class:`~django_auth_ldap.backend.LDAPBackend` will then find all of the LDAP
groups that a user belongs to, map them to Django groups, and load the
permissions for those groups. You will need to create the Django groups and
associate permissions yourself, generally through the admin interface.

To minimize traffic to the LDAP server,
:class:`~django_auth_ldap.backend.LDAPBackend` can make use of Django's cache
framework to keep a copy of a user's LDAP group memberships. To enable this
feature, set :setting:`AUTH_LDAP_CACHE_GROUPS` to ``True``. You can also set
:setting:`AUTH_LDAP_GROUP_CACHE_TIMEOUT` to override the timeout of cache
entries (in seconds).

.. code-block:: python

    AUTH_LDAP_CACHE_GROUPS = True
    AUTH_LDAP_GROUP_CACHE_TIMEOUT = 300


Group Mirroring
---------------

The second way to turn LDAP group memberships into permissions is to mirror the
groups themselves. If :setting:`AUTH_LDAP_MIRROR_GROUPS` is ``True``, then every
time a user logs in, :class:`~django_auth_ldap.backend.LDAPBackend` will update
the database with the user's LDAP groups. Any group that doesn't exist will be
created and the user's Django group membership will be updated to exactly match
his LDAP group membership. Note that if the LDAP server has nested groups, the
Django database will end up with a flattened representation. For group mirroring
to have any effect, you of course need
:class:`~django.contrib.auth.backends.ModelBackend` installed as an
authentication backend.

The main difference between this approach and
:setting:`AUTH_LDAP_FIND_GROUP_PERMS` is that
:setting:`AUTH_LDAP_FIND_GROUP_PERMS` will query for LDAP group membership
either for every request or according to the cache timeout. With group
mirroring, membership will be updated when the user authenticates. This may not
be appropriate for sites with long session timeouts.


Non-LDAP Users
--------------

:class:`~django_auth_ldap.backend.LDAPBackend` has one more feature pertaining
to permissions, which is the ability to handle authorization for users that it
did not authenticate. For example, you might be using
:class:`~django.contrib.auth.backends.RemoteUserBackend`
to map externally authenticated users to Django users. By setting
:setting:`AUTH_LDAP_AUTHORIZE_ALL_USERS`,
:class:`~django_auth_ldap.backend.LDAPBackend` will map these users to LDAP
users in the normal way in order to provide authorization information. Note that
this does *not* work with :setting:`AUTH_LDAP_MIRROR_GROUPS`; group mirroring is
a feature of authentication, not authorization.

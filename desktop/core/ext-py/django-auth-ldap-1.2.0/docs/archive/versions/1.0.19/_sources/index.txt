================================
Django authentication using LDAP
================================

This authentication backend enables a Django project to authenticate against any
LDAP server. To use it, add :class:`django_auth_ldap.backend.LDAPBackend` to
AUTHENTICATION_BACKENDS. It is not necessary to add `django_auth_ldap` to
INSTALLED_APPLICATIONS unless you would like to run the unit tests. LDAP
configuration can be as simple as a single distinguished name template, but
there are many rich options for working with
:class:`~django.contrib.auth.models.User` objects, groups, and permissions. This
backend depends on the `python-ldap <http://www.python-ldap.org/>`_ module.

.. note::

    :class:`~django_auth_ldap.backend.LDAPBackend` does not inherit from
    :class:`~django.contrib.auth.backends.ModelBackend`. It is possible to use
    :class:`~django_auth_ldap.backend.LDAPBackend` exclusively by configuring it
    to draw group membership from the LDAP server. However, if you would like to
    assign permissions to individual users or add users to groups within Django,
    you'll need to have both backends installed:

    .. code-block:: python

        AUTHENTICATION_BACKENDS = (
            'django_auth_ldap.backend.LDAPBackend',
            'django.contrib.auth.backends.ModelBackend',
        )


Configuring basic authentication
================================

If your LDAP server isn't running locally on the default port, you'll want to
start by setting :ref:`AUTH_LDAP_SERVER_URI` to point to your server.

.. code-block:: python

    AUTH_LDAP_SERVER_URI = "ldap://ldap.example.com"

That done, the first step is to authenticate a username and password against the
LDAP service. There are two ways to do this, called search/bind and simply bind.
The first one involves connecting to the LDAP server either anonymously or with
a fixed account and searching for the distinguished name of the authenticating
user. Then we can attempt to bind again with the user's password. The second
method is to derive the user's DN from his username and attempt to bind as the
user directly.

Because LDAP searches appear elsewhere in the configuration, the
:class:`~django_auth_ldap.config.LDAPSearch` class is provided to encapsulate
search information. In this case, the filter parameter should contain the
placeholder ``%(user)s``. A simple configuration for the search/bind approach
looks like this (some defaults included for completeness)::

    import ldap
    from django_auth_ldap.config import LDAPSearch

    AUTH_LDAP_BIND_DN = ""
    AUTH_LDAP_BIND_PASSWORD = ""
    AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=users,dc=example,dc=com",
        ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

This will perform an anonymous bind, search under
``"ou=users,dc=example,dc=com"`` for an object with a uid matching the user's
name, and try to bind using that DN and the user's password. The search must
return exactly one result or authentication will fail. If you can't search
anonymously, you can set :ref:`AUTH_LDAP_BIND_DN` to the distinguished name of
an authorized user and :ref:`AUTH_LDAP_BIND_PASSWORD` to the password.

To skip the search phase, set :ref:`AUTH_LDAP_USER_DN_TEMPLATE` to a template
that will produce the authenticating user's DN directly. This template should
have one placeholder, ``%(user)s``. If the previous example had used
``ldap.SCOPE_ONELEVEL``, the following would be a more straightforward (and
efficient) equivalent::

    AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=users,dc=example,dc=com"

LDAP is fairly flexible when it comes to matching DNs.
:class:`~django_auth_ldap.backend.LDAPBackend` make an effort to accommodate
this by forcing usernames to lower case when creating Django users and trimming
whitespace when authenticating.

By default, all LDAP operations are performed with the :ref:`AUTH_LDAP_BIND_DN`
and :ref:`AUTH_LDAP_BIND_PASSWORD` credentials, not with the user's. Otherwise,
the LDAP connection would be bound as the authenticating user during login
requests and as the default credentials during other requests, so you would see
inconsistent LDAP attributes depending on the nature of the Django view. If
you're willing to accept the inconsistency in order to retrieve attributes
while bound as the authenticating user. see
:ref:`AUTH_LDAP_BIND_AS_AUTHENTICATING_USER`.

By default, LDAP connections are unencrypted and make no attempt to protect
sensitive information, such as passwords. When communicating with an LDAP server
on localhost or on a local network, this might be fine. If you need a secure
connection to the LDAP server, you can either use an ``ldaps://`` URL or enable
the StartTLS extension. The latter is generally the preferred mechanism. To
enable StartTLS, set :ref:`AUTH_LDAP_START_TLS` to ``True``::

    AUTH_LDAP_START_TLS = True


Working with groups
===================

Working with groups in LDAP can be a tricky business, mostly because there are
so many different kinds. This module includes an extensible API for working with
any kind of group and includes implementations for the most common ones.
:class:`~django_auth_ldap.config.LDAPGroupType` is a base class whose concrete
subclasses can determine group membership for particular grouping mechanisms.
Three built-in subclasses cover most grouping mechanisms:

    * :class:`~django_auth_ldap.config.PosixGroupType`
    * :class:`~django_auth_ldap.config.MemberDNGroupType`
    * :class:`~django_auth_ldap.config.NestedMemberDNGroupType`

posixGroup objects are somewhat specialized, so they get their own class. The
other two cover mechanisms whereby a group object stores a list of its members
as distinguished names. This includes groupOfNames, groupOfUniqueNames, and
Active Directory groups, among others. The nested variant allows groups to
contain other groups, to as many levels as you like. For convenience and
readability, several trivial subclasses of the above are provided:

    * :class:`~django_auth_ldap.config.GroupOfNamesType`
    * :class:`~django_auth_ldap.config.NestedGroupOfNamesType`
    * :class:`~django_auth_ldap.config.GroupOfUniqueNamesType`
    * :class:`~django_auth_ldap.config.NestedGroupOfUniqueNamesType`
    * :class:`~django_auth_ldap.config.ActiveDirectoryGroupType`
    * :class:`~django_auth_ldap.config.NestedActiveDirectoryGroupType`

To get started, you'll need to provide some basic information about your LDAP
groups. :ref:`AUTH_LDAP_GROUP_SEARCH` is an
:class:`~django_auth_ldap.config.LDAPSearch` object that identifies the set of
relevant group objects. That is, all groups that users might belong to as well
as any others that we might need to know about (in the case of nested groups,
for example). :ref:`AUTH_LDAP_GROUP_TYPE` is an instance of the class
corresponding to the type of group that will be returned by
:ref:`AUTH_LDAP_GROUP_SEARCH`. All groups referenced elsewhere in the
configuration must be of this type and part of the search results.

.. code-block:: python

    import ldap
    from django_auth_ldap.config import LDAPSearch, GroupOfNamesType

    AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=groups,dc=example,dc=com",
        ldap.SCOPE_SUBTREE, "(objectClass=groupOfNames)"
    )
    AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()

The simplest use of groups is to limit the users who are allowed to log in. If
:ref:`AUTH_LDAP_REQUIRE_GROUP` is set, then only users who are members of that
group will successfully authenticate. :ref:`AUTH_LDAP_DENY_GROUP` is the
reverse: if given, members of this group will be rejected.

.. code-block:: python

    AUTH_LDAP_REQUIRE_GROUP = "cn=enabled,ou=groups,dc=example,dc=com"
    AUTH_LDAP_DENY_GROUP = "cn=disabled,ou=groups,dc=example,dc=com"

More advanced uses of groups are covered in the next two sections.


User objects
============

Authenticating against an external source is swell, but Django's auth module is
tightly bound to the :class:`django.contrib.auth.models.User` model. Thus, when
a user logs in, we have to create a :class:`~django.contrib.auth.models.User`
object to represent him in the database. Because the LDAP search is
case-insenstive, the default implementation also searches for existing Django
users with an iexact query and new users are created with lowercase usernames.
See :meth:`~django_auth_ldap.backend.LDAPBackend.get_or_create_user` if you'd
like to override this behavior.

The only required field for a user is the username, which we obviously have. The
:class:`~django.contrib.auth.models.User` model is picky about the characters
allowed in usernames, so :class:`~django_auth_ldap.backend.LDAPBackend` includes
a pair of hooks,
:meth:`~django_auth_ldap.backend.LDAPBackend.ldap_to_django_username` and
:meth:`~django_auth_ldap.backend.LDAPBackend.django_to_ldap_username`, to
translate between LDAP usernames and Django usernames. You'll need this, for
example, if your LDAP names have periods in them. You can subclass
:class:`~django_auth_ldap.backend.LDAPBackend` to implement these hooks; by
default the username is not modified. :class:`~django.contrib.auth.models.User`
objects that are authenticated by :class:`~django_auth_ldap.backend.LDAPBackend`
will have an :attr:`~django.contrib.auth.models.User.ldap_username` attribute
with the original (LDAP) username.
:attr:`~django.contrib.auth.models.User.username` will, of course, be the Django
username.

LDAP directories tend to contain much more information about users that you may
wish to propagate. A pair of settings, :ref:`AUTH_LDAP_USER_ATTR_MAP` and
:ref:`AUTH_LDAP_PROFILE_ATTR_MAP`, serve to copy directory information into
:class:`~django.contrib.auth.models.User` and profile objects. These are
dictionaries that map user and profile model keys, respectively, to
(case-insensitive) LDAP attribute names::

    AUTH_LDAP_USER_ATTR_MAP = {"first_name": "givenName", "last_name": "sn"}
    AUTH_LDAP_PROFILE_ATTR_MAP = {"home_directory": "homeDirectory"}

Only string fields can be mapped to attributes. Boolean fields can be defined by
group membership::

    AUTH_LDAP_USER_FLAGS_BY_GROUP = {
        "is_active": "cn=active,ou=groups,dc=example,dc=com",
        "is_staff": "cn=staff,ou=groups,dc=example,dc=com",
        "is_superuser": "cn=superuser,ou=groups,dc=example,dc=com"
    }

    AUTH_LDAP_PROFILE_FLAGS_BY_GROUP = {
        "is_awesome": "cn=awesome,ou=django,ou=groups,dc=example,dc=com"
    }

By default, all mapped user fields will be updated each time the user logs in.
To disable this, set :ref:`AUTH_LDAP_ALWAYS_UPDATE_USER` to ``False``. If you
need to populate a user outside of the authentication process—for example, to
create associated model objects before the user logs in for the first time—you
can call :meth:`django_auth_ldap.backend.LDAPBackend.populate_user`. You'll
need an instance of :class:`~django_auth_ldap.backend.LDAPBackend`, which you
should feel free to create yourself.
:meth:`~django_auth_ldap.backend.LDAPBackend.populate_user` returns the new
:class:`~django.contrib.auth.models.User` or `None` if the user could not be
found in LDAP.

If you need to access multi-value attributes or there is some other reason that
the above is inadequate, you can also access the user's raw LDAP attributes.
``user.ldap_user`` is an object with four public properties. The group
properties are, of course, only valid if groups are configured.

    * ``dn``: The user's distinguished name.
    * ``attrs``: The user's LDAP attributes as a dictionary of lists of string
      values. The dictionaries are modified to use case-insensitive keys.
    * ``group_dns``: The set of groups that this user belongs to, as DNs.
    * ``group_names``: The set of groups that this user belongs to, as simple
      names. These are the names that will be used if
      :ref:`AUTH_LDAP_MIRROR_GROUPS` is used.

Python-ldap returns all attribute values as utf8-encoded strings. For
convenience, this module will try to decode all values into Unicode strings. Any
string that can not be successfully decoded will be left as-is; this may apply
to binary values such as Active Directory's objectSid.

If you would like to perform any additional population of user or profile
objects, django_auth_ldap exposes two custom signals to help:
:data:`~django_auth_ldap.backend.populate_user` and
:data:`~django_auth_ldap.backend.populate_user_profile`. These are sent after
the backend has finished populating the respective objects and before they are
saved to the database. You can use this to propagate additional information from
the LDAP directory to the user and profile objects any way you like.

.. note::

    Users created by :class:`~django_auth_ldap.backend.LDAPBackend` will have an
    unusable password set. This will only happen when the user is created, so if
    you set a valid password in Django, the user will be able to log in through
    :class:`~django.contrib.auth.backends.ModelBackend` (if configured) even if
    he is rejected by LDAP. This is not generally recommended, but could be
    useful as a fail-safe for selected users in case the LDAP server is
    unavailable.


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

The least invasive way to map group permissions is to set
:ref:`AUTH_LDAP_FIND_GROUP_PERMS` to ``True``.
:class:`~django_auth_ldap.backend.LDAPBackend` will then find all of the LDAP
groups that a user belongs to, map them to Django groups, and load the
permissions for those groups. You will need to create the Django groups
yourself, generally through the admin interface.

To minimize traffic to the LDAP server,
:class:`~django_auth_ldap.backend.LDAPBackend` can make use of Django's cache
framework to keep a copy of a user's LDAP group memberships. To enable this
feature, set :ref:`AUTH_LDAP_CACHE_GROUPS` to ``True``. You can also set
:ref:`AUTH_LDAP_GROUP_CACHE_TIMEOUT` to override the timeout of cache entries
(in seconds).

.. code-block:: python

    AUTH_LDAP_CACHE_GROUPS = True
    AUTH_LDAP_GROUP_CACHE_TIMEOUT = 300

The second way to turn LDAP group memberships into permissions is to mirror the
groups themselves. If :ref:`AUTH_LDAP_MIRROR_GROUPS` is ``True``, then every
time a user logs in, :class:`~django_auth_ldap.backend.LDAPBackend` will update
the database with the user's LDAP groups. Any group that doesn't exist will be
created and the user's Django group membership will be updated to exactly match
his LDAP group membership. Note that if the LDAP server has nested groups, the
Django database will end up with a flattened representation.

This approach has two main differences from :ref:`AUTH_LDAP_FIND_GROUP_PERMS`.
First, :ref:`AUTH_LDAP_FIND_GROUP_PERMS` will query for LDAP group membership
either for every request or according to the cache timeout. With group
mirroring, membership will be updated when the user authenticates. This may not
be appropriate for sites with long session timeouts. The second difference is
that with :ref:`AUTH_LDAP_FIND_GROUP_PERMS`, there is no way for clients to
determine a user's group memberships, only their permissions. If you want to
make decisions based directly on group membership, you'll have to mirror the
groups.

:class:`~django_auth_ldap.backend.LDAPBackend` has one more feature pertaining
to permissions, which is the ability to handle authorization for users that it
did not authenticate. For example, you might be using Django's RemoteUserBackend
to map externally authenticated users to Django users. By setting
:ref:`AUTH_LDAP_AUTHORIZE_ALL_USERS`,
:class:`~django_auth_ldap.backend.LDAPBackend` will map these users to LDAP
users in the normal way in order to provide authorization information. Note that
this does *not* work with :ref:`AUTH_LDAP_MIRROR_GROUPS`; group mirroring is a
feature of authentication, not authorization.


Logging
=======

:class:`~django_auth_ldap.backend.LDAPBackend` uses the standard logging module
to log debug and warning messages to the logger named ``'django_auth_ldap'``. If
you need debug messages to help with configuration issues, you should add a
handler to this logger. Note that this logger is initialized with a level of
NOTSET, so you may need to change the level of the logger in order to get debug
messages.

.. code-block:: python

    import logging

    logger = logging.getLogger('django_auth_ldap')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

More options
============

Miscellaneous settings for :class:`~django_auth_ldap.backend.LDAPBackend`:

    * :ref:`AUTH_LDAP_GLOBAL_OPTIONS`: A dictionary of options to pass to
      python-ldap via ``ldap.set_option()``.
    * :ref:`AUTH_LDAP_CONNECTION_OPTIONS`: A dictionary of options to pass to
      each LDAPObject instance via ``LDAPObject.set_option()``.


Performance
===========

:class:`~django_auth_ldap.backend.LDAPBackend` is carefully designed not to
require a connection to the LDAP service for every request. Of course, this
depends heavily on how it is configured. If LDAP traffic or latency is a concern
for your deployment, this section has a few tips on minimizing it, in decreasing
order of impact.

    #. **Cache groups**. If :ref:`AUTH_LDAP_FIND_GROUP_PERMS` is ``True``, the
       default behavior is to reload a user's group memberships on every
       request. This is the safest behavior, as any membership change takes
       effect immediately, but it is expensive. If possible, set
       :ref:`AUTH_LDAP_CACHE_GROUPS` to ``True`` to remove most of this traffic.
       Alternatively, you might consider using :ref:`AUTH_LDAP_MIRROR_GROUPS`
       and relying on :class:`~django.contrib.auth.backends.ModelBackend` to
       supply group permissions.
    #. **Don't access user.ldap_user.***. These properties are only cached
       on a per-request basis. If you can propagate LDAP attributes to a
       :class:`~django.contrib.auth.models.User` or profile object, they will
       only be updated at login. ``user.ldap_user.attrs`` triggers an LDAP
       connection for every request in which it's accessed. If you're not using
       :ref:`AUTH_LDAP_USER_DN_TEMPLATE`, then accessing ``user.ldap_user.dn``
       will also trigger an LDAP connection.
    #. **Use simpler group types**. Some grouping mechanisms are more expensive
       than others. This will often be outside your control, but it's important
       to note that the extra functionality of more complex group types like
       :class:`~django_auth_ldap.config.NestedGroupOfNamesType` is not free and
       will generally require a greater number and complexity of LDAP queries.
    #. **Use direct binding**. Binding with
       :ref:`AUTH_LDAP_USER_DN_TEMPLATE` is a little bit more efficient than
       relying on :ref:`AUTH_LDAP_USER_SEARCH`. Specifically, it saves two LDAP
       operations (one bind and one search) per login.


Example configuration
=====================

Here is a complete example configuration from :file:`settings.py` that exercises
nearly all of the features. In this example, we're authenticating against a
global pool of users in the directory, but we have a special area set aside for
Django groups (ou=django,ou=groups,dc=example,dc=com). Remember that most of
this is optional if you just need simple authentication. Some default settings
and arguments are included for completeness.

.. code-block:: python

    import ldap
    from django_auth_ldap.config import LDAPSearch, GroupOfNamesType


    # Baseline configuration.
    AUTH_LDAP_SERVER_URI = "ldap://ldap.example.com"

    AUTH_LDAP_BIND_DN = "cn=django-agent,dc=example,dc=com"
    AUTH_LDAP_BIND_PASSWORD = "phlebotinum"
    AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=users,dc=example,dc=com",
        ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
    # or perhaps:
    # AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=users,dc=example,dc=com"

    # Set up the basic group parameters.
    AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=django,ou=groups,dc=example,dc=com",
        ldap.SCOPE_SUBTREE, "(objectClass=groupOfNames)"
    )
    AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="cn")

    # Simple group restrictions
    AUTH_LDAP_REQUIRE_GROUP = "cn=enabled,ou=django,ou=groups,dc=example,dc=com"
    AUTH_LDAP_DENY_GROUP = "cn=disabled,ou=django,ou=groups,dc=example,dc=com"

    # Populate the Django user from the LDAP directory.
    AUTH_LDAP_USER_ATTR_MAP = {
        "first_name": "givenName",
        "last_name": "sn",
        "email": "mail"
    }

    AUTH_LDAP_PROFILE_ATTR_MAP = {
        "employee_number": "employeeNumber"
    }

    AUTH_LDAP_USER_FLAGS_BY_GROUP = {
        "is_active": "cn=active,ou=django,ou=groups,dc=example,dc=com",
        "is_staff": "cn=staff,ou=django,ou=groups,dc=example,dc=com",
        "is_superuser": "cn=superuser,ou=django,ou=groups,dc=example,dc=com"
    }

    AUTH_LDAP_PROFILE_FLAGS_BY_GROUP = {
        "is_awesome": "cn=awesome,ou=django,ou=groups,dc=example,dc=com",
    }

    # This is the default, but I like to be explicit.
    AUTH_LDAP_ALWAYS_UPDATE_USER = True

    # Use LDAP group membership to calculate group permissions.
    AUTH_LDAP_FIND_GROUP_PERMS = True

    # Cache group memberships for an hour to minimize LDAP traffic
    AUTH_LDAP_CACHE_GROUPS = True
    AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600


    # Keep ModelBackend around for per-user permissions and maybe a local
    # superuser.
    AUTHENTICATION_BACKENDS = (
        'django_auth_ldap.backend.LDAPBackend',
        'django.contrib.auth.backends.ModelBackend',
    )


Reference
=========

Settings
--------

.. _AUTH_LDAP_ALWAYS_UPDATE_USER:

AUTH_LDAP_ALWAYS_UPDATE_USER
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``True``

If ``True``, the fields of a :class:`~django.contrib.auth.models.User` object
will be updated with the latest values from the LDAP directory every time the
user logs in. Otherwise the :class:`~django.contrib.auth.models.User` object
will only be populated when it is automatically created.


.. _AUTH_LDAP_AUTHORIZE_ALL_USERS:

AUTH_LDAP_AUTHORIZE_ALL_USERS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``False``

If ``True``, :class:`~django_auth_ldap.backend.LDAPBackend` will be able furnish
permissions for any Django user, regardless of which backend authenticated it.


.. _AUTH_LDAP_BIND_AS_AUTHENTICATING_USER:

AUTH_LDAP_BIND_AS_AUTHENTICATING_USER
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``False``

If ``True``, authentication will leave the LDAP connection bound as the
authenticating user, rather than forcing it to re-bind with the default
credentials after authentication succeeds. This may be desirable if you do not
have global credentials that are able to access the user's attributes.
django-auth-ldap never stores the user's password, so this only applies to
requests where the user is authenticated. Thus, the downside to this setting is
that LDAP results may vary based on whether the user was authenticated earlier
in the Django view, which could be surprising to code not directly concerned
with authentication.


.. _AUTH_LDAP_BIND_DN:

AUTH_LDAP_BIND_DN
~~~~~~~~~~~~~~~~~

Default: ``''`` (Empty string)

The distinguished name to use when binding to the LDAP server (with
:ref:`AUTH_LDAP_BIND_PASSWORD`). Use the empty string (the default) for an
anonymous bind. To authenticate a user, we will bind with that user's DN and
password, but for all other LDAP operations, we will be bound as the DN in this
setting. For example, if :ref:`AUTH_LDAP_USER_DN_TEMPLATE` is not set, we'll use
this to search for the user. If :ref:`AUTH_LDAP_FIND_GROUP_PERMS` is ``True``,
we'll also use it to determine group membership.


.. _AUTH_LDAP_BIND_PASSWORD:

AUTH_LDAP_BIND_PASSWORD
~~~~~~~~~~~~~~~~~~~~~~~

Default: ``''`` (Empty string)

The password to use with :ref:`AUTH_LDAP_BIND_DN`.


.. _AUTH_LDAP_CACHE_GROUPS:

AUTH_LDAP_CACHE_GROUPS
~~~~~~~~~~~~~~~~~~~~~~

Default: ``False``

If ``True``, LDAP group membership will be cached using Django's cache
framework. The cache timeout can be customized with
:ref:`AUTH_LDAP_GROUP_CACHE_TIMEOUT`.


.. _AUTH_LDAP_CONNECTION_OPTIONS:

AUTH_LDAP_CONNECTION_OPTIONS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``{}``

A dictionary of options to pass to each connection to the LDAP server via
``LDAPObject.set_option()``. Keys are ``ldap.OPT_*`` constants.


.. _AUTH_LDAP_DENY_GROUP:

AUTH_LDAP_DENY_GROUP
~~~~~~~~~~~~~~~~~~~~~~~

Default: ``None``

The distinguished name of a group; authentication will fail for any user
that belongs to this group.


.. _AUTH_LDAP_FIND_GROUP_PERMS:

AUTH_LDAP_FIND_GROUP_PERMS
~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``False``

If ``True``, :class:`~django_auth_ldap.backend.LDAPBackend` will furnish group
permissions based on the LDAP groups the authenticated user belongs to.
:ref:`AUTH_LDAP_GROUP_SEARCH` and :ref:`AUTH_LDAP_GROUP_TYPE` must also be set.


.. _AUTH_LDAP_GLOBAL_OPTIONS:

AUTH_LDAP_GLOBAL_OPTIONS
~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``{}``

A dictionary of options to pass to ``ldap.set_option()``. Keys are
``ldap.OPT_*`` constants.


.. _AUTH_LDAP_GROUP_CACHE_TIMEOUT:

AUTH_LDAP_GROUP_CACHE_TIMEOUT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``None``

If :ref:`AUTH_LDAP_CACHE_GROUPS` is ``True``, this is the cache timeout for
group memberships. If ``None``, the global cache timeout will be used.


.. _AUTH_LDAP_GROUP_SEARCH:

AUTH_LDAP_GROUP_SEARCH
~~~~~~~~~~~~~~~~~~~~~~

Default: ``None``

An :class:`~django_auth_ldap.config.LDAPSearch` object that finds all LDAP
groups that users might belong to. If your configuration makes any references to
LDAP groups, this and :ref:`AUTH_LDAP_GROUP_TYPE` must be set.


.. _AUTH_LDAP_GROUP_TYPE:

AUTH_LDAP_GROUP_TYPE
~~~~~~~~~~~~~~~~~~~~

Default: ``None``

An :class:`~django_auth_ldap.config.LDAPGroupType` instance describing the type
of group returned by :ref:`AUTH_LDAP_GROUP_SEARCH`.


.. _AUTH_LDAP_MIRROR_GROUPS:

AUTH_LDAP_MIRROR_GROUPS
~~~~~~~~~~~~~~~~~~~~~~~

Default: ``False``

If ``True``, :class:`~django_auth_ldap.backend.LDAPBackend` will mirror a user's
LDAP group membership in the Django database. Any time a user authenticates, we
will create all of his LDAP groups as Django groups and update his Django group
membership to exactly match his LDAP group membership. If the LDAP server has
nested groups, the Django database will end up with a flattened representation.


.. _AUTH_LDAP_PROFILE_ATTR_MAP:

AUTH_LDAP_PROFILE_ATTR_MAP
~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``{}``

A mapping from user profile field names to LDAP attribute names. A user's
profile will be populated from his LDAP attributes at login.


.. _AUTH_LDAP_PROFILE_FLAGS_BY_GROUP:

AUTH_LDAP_PROFILE_FLAGS_BY_GROUP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``{}``

A mapping from boolean profile field names to distinguished names of LDAP
groups. The corresponding field in a user's profile is set to ``True`` or
``False`` according to whether the user is a member of the group.


.. _AUTH_LDAP_REQUIRE_GROUP:

AUTH_LDAP_REQUIRE_GROUP
~~~~~~~~~~~~~~~~~~~~~~~

Default: ``None``

The distinguished name of a group; authentication will fail for any user that
does not belong to this group.


.. _AUTH_LDAP_SERVER_URI:

AUTH_LDAP_SERVER_URI
~~~~~~~~~~~~~~~~~~~~

Default: ``ldap://localhost``

The URI of the LDAP server. This can be any URI that is supported by your
underlying LDAP libraries.


.. _AUTH_LDAP_START_TLS:

AUTH_LDAP_START_TLS
~~~~~~~~~~~~~~~~~~~

Default: ``False``

If ``True``, each connection to the LDAP server will call start_tls to enable
TLS encryption over the standard LDAP port. There are a number of configuration
options that can be given to :ref:`AUTH_LDAP_GLOBAL_OPTIONS` that affect the
TLS connection. For example, ``ldap.OPT_X_TLS_REQUIRE_CERT`` can be set to
``ldap.OPT_X_TLS_NEVER`` to disable certificate verification, perhaps to allow
self-signed certificates.


.. _AUTH_LDAP_USER_ATTR_MAP:

AUTH_LDAP_USER_ATTR_MAP
~~~~~~~~~~~~~~~~~~~~~~~

Default: ``{}``

A mapping from :class:`~django.contrib.auth.models.User` field names to LDAP
attribute names. A users's :class:`~django.contrib.auth.models.User` object will
be populated from his LDAP attributes at login.


.. _AUTH_LDAP_USER_DN_TEMPLATE:

AUTH_LDAP_USER_DN_TEMPLATE
~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``None``

A string template that describes any user's distinguished name based on the
username. This must contain the placeholder ``%(user)s``.


.. _AUTH_LDAP_USER_FLAGS_BY_GROUP:

AUTH_LDAP_USER_FLAGS_BY_GROUP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``{}``

A mapping from boolean :class:`~django.contrib.auth.models.User` field names to
distinguished names of LDAP groups. The corresponding field is set to ``True``
or ``False`` according to whether the user is a member of the group.


.. _AUTH_LDAP_USER_SEARCH:

AUTH_LDAP_USER_SEARCH
~~~~~~~~~~~~~~~~~~~~~

Default: ``None``

An :class:`~django_auth_ldap.config.LDAPSearch` object that will locate a user
in the directory. The filter parameter should contain the placeholder
``%(user)s`` for the username. It must return exactly one result for
authentication to succeed.


Module Properties
-----------------

.. module:: django_auth_ldap

.. data:: version

    The library's current version number as a 3-tuple.

.. data:: version_string

    The library's current version number as a string.


Configuration
-------------

.. module:: django_auth_ldap.config

.. class:: LDAPSearch

    .. method:: __init__(base_dn, scope, filterstr='(objectClass=*)')

        * ``base_dn``: The distinguished name of the search base.
        * ``scope``: One of ``ldap.SCOPE_*``.
        * ``filterstr``: An optional filter string (e.g. '(objectClass=person)').
          In order to be valid, ``filterstr`` must be enclosed in parentheses.


.. class:: LDAPGroupType

    The base class for objects that will determine group membership for various
    LDAP grouping mechanisms. Implementations are provided for common group
    types or you can write your own. See the source code for subclassing notes.

    .. method:: __init__(name_attr='cn')

        By default, LDAP groups will be mapped to Django groups by taking the
        first value of the cn attribute. You can specify a different attribute
        with ``name_attr``.


.. class:: PosixGroupType

    A concrete subclass of :class:`~django_auth_ldap.config.LDAPGroupType` that
    handles the ``posixGroup`` object class. This checks for both primary group
    and group membership.

    .. method:: __init__(name_attr='cn')

.. class:: MemberDNGroupType

    A concrete subclass of
    :class:`~django_auth_ldap.config.LDAPGroupType` that handles grouping
    mechanisms wherein the group object contains a list of its member DNs.

    .. method:: __init__(member_attr, name_attr='cn')

        * ``member_attr``: The attribute on the group object that contains a
          list of member DNs. 'member' and 'uniqueMember' are common examples.


.. class:: NestedMemberDNGroupType

    Similar to :class:`~django_auth_ldap.config.MemberDNGroupType`, except this
    allows groups to contain other groups as members. Group hierarchies will be
    traversed to determine membership.

    .. method:: __init__(member_attr, name_attr='cn')

        As above.


.. class:: GroupOfNamesType

    A concrete subclass of :class:`~django_auth_ldap.config.MemberDNGroupType`
    that handles the ``groupOfNames`` object class. Equivalent to
    ``MemberDNGroupType('member')``.

    .. method:: __init__(name_attr='cn')


.. class:: NestedGroupOfNamesType

    A concrete subclass of
    :class:`~django_auth_ldap.config.NestedMemberDNGroupType` that handles the
    ``groupOfNames`` object class. Equivalent to
    ``NestedMemberDNGroupType('member')``.

    .. method:: __init__(name_attr='cn')


.. class:: GroupOfUniqueNamesType

    A concrete subclass of :class:`~django_auth_ldap.config.MemberDNGroupType`
    that handles the ``groupOfUniqueNames`` object class. Equivalent to
    ``MemberDNGroupType('uniqueMember')``.

    .. method:: __init__(name_attr='cn')


.. class:: NestedGroupOfUniqueNamesType

    A concrete subclass of
    :class:`~django_auth_ldap.config.NestedMemberDNGroupType` that handles the
    ``groupOfUniqueNames`` object class. Equivalent to
    ``NestedMemberDNGroupType('uniqueMember')``.

    .. method:: __init__(name_attr='cn')


.. class:: ActiveDirectoryGroupType

    A concrete subclass of :class:`~django_auth_ldap.config.MemberDNGroupType`
    that handles Active Directory groups. Equivalent to
    ``MemberDNGroupType('member')``.

    .. method:: __init__(name_attr='cn')


.. class:: NestedActiveDirectoryGroupType

    A concrete subclass of
    :class:`~django_auth_ldap.config.NestedMemberDNGroupType` that handles
    Active Directory groups. Equivalent to
    ``NestedMemberDNGroupType('member')``.

    .. method:: __init__(name_attr='cn')


Backend
-------

.. module:: django_auth_ldap.backend

.. data:: populate_user

    This is a Django signal that is sent when clients should perform additional
    customization of a :class:`~django.contrib.auth.models.User` object. It is
    sent after a user has been authenticated and the backend has finished
    populating it, and just before it is saved. The client may take this
    opportunity to populate additional model fields, perhaps based on
    ``ldap_user.attrs``. This signal has two keyword arguments: ``user`` is the
    :class:`~django.contrib.auth.models.User` object and ``ldap_user`` is the
    same as ``user.ldap_user``. The sender is the
    :class:`~django_auth_ldap.backend.LDAPBackend` class.

.. data:: populate_user_profile

    Like :data:`~django_auth_ldap.backend.populate_user`, but sent for the user
    profile object. This will only be sent if the user has an existing profile.
    As with :data:`~django_auth_ldap.backend.populate_user`, it is sent after the
    backend has finished setting properties and before the object is saved. This
    signal has two keyword arguments: ``profile`` is the user profile object and
    ``ldap_user`` is the same as ``user.ldap_user``. The sender is the
    :class:`~django_auth_ldap.backend.LDAPBackend` class.

.. class:: LDAPBackend

    :class:`~django_auth_ldap.backend.LDAPBackend` has one method that may be
    called directly and several that may be overridden in subclasses.

    .. method:: populate_user(username)

        Populates the Django user for the given LDAP username. This connects to
        the LDAP directory with the default credentials and attempts to populate
        the indicated Django user as if they had just logged in.
        :ref:`AUTH_LDAP_ALWAYS_UPDATE_USER` is ignored (assumed ``True``).

    .. method:: get_or_create_user(self, username, ldap_user)

        Given a username and an LDAP user object, this must return the
        associated Django User object. The ``username`` argument has already
        been passed through
        :meth:`~django_auth_ldap.backend.LDAPBackend.ldap_to_django_username`.
        You can get information about the LDAP user via ``ldap_user.dn`` and
        ``ldap_user.attrs``. The return value must be the same as
        ``User.objects.get_or_create()``: a (User, created) two-tuple.

        The default implementation calls ``User.objects.get_or_create()``, using
        a case-insensitive query and creating new users with lowercase
        usernames. Subclasses are welcome to associate LDAP users to Django
        users any way they like.

    .. method:: ldap_to_django_username(username)

        Returns a valid Django username based on the given LDAP username (which
        is what the user enters). By default, ``username`` is returned
        unchanged. This can be overriden by subclasses.

    .. method:: django_to_ldap_username(username)

        The inverse of
        :meth:`~django_auth_ldap.backend.LDAPBackend.ldap_to_django_username`.
        If this is not symmetrical to
        :meth:`~django_auth_ldap.backend.LDAPBackend.ldap_to_django_username`,
        the behavior is undefined.


License
=======

Copyright (c) 2009, Peter Sagerson
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright notice, this
  list of conditions and the following disclaimer in the documentation and/or
  other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

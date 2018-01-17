Reference
=========

Settings
--------

.. setting:: AUTH_LDAP_ALWAYS_UPDATE_USER

AUTH_LDAP_ALWAYS_UPDATE_USER
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``True``

If ``True``, the fields of a :class:`~django.contrib.auth.models.User` object
will be updated with the latest values from the LDAP directory every time the
user logs in. Otherwise the :class:`~django.contrib.auth.models.User` object
will only be populated when it is automatically created.


.. setting:: AUTH_LDAP_AUTHORIZE_ALL_USERS

AUTH_LDAP_AUTHORIZE_ALL_USERS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``False``

If ``True``, :class:`~django_auth_ldap.backend.LDAPBackend` will be able furnish
permissions for any Django user, regardless of which backend authenticated it.


.. setting:: AUTH_LDAP_BIND_AS_AUTHENTICATING_USER

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


.. setting:: AUTH_LDAP_BIND_DN

AUTH_LDAP_BIND_DN
~~~~~~~~~~~~~~~~~

Default: ``''`` (Empty string)

The distinguished name to use when binding to the LDAP server (with
:setting:`AUTH_LDAP_BIND_PASSWORD`). Use the empty string (the default) for an
anonymous bind. To authenticate a user, we will bind with that user's DN and
password, but for all other LDAP operations, we will be bound as the DN in this
setting. For example, if :setting:`AUTH_LDAP_USER_DN_TEMPLATE` is not set, we'll
use this to search for the user. If :setting:`AUTH_LDAP_FIND_GROUP_PERMS` is
``True``, we'll also use it to determine group membership.


.. setting:: AUTH_LDAP_BIND_PASSWORD

AUTH_LDAP_BIND_PASSWORD
~~~~~~~~~~~~~~~~~~~~~~~

Default: ``''`` (Empty string)

The password to use with :setting:`AUTH_LDAP_BIND_DN`.


.. setting:: AUTH_LDAP_CACHE_GROUPS

AUTH_LDAP_CACHE_GROUPS
~~~~~~~~~~~~~~~~~~~~~~

Default: ``False``

If ``True``, LDAP group membership will be cached using Django's cache
framework. The cache timeout can be customized with
:setting:`AUTH_LDAP_GROUP_CACHE_TIMEOUT`.


.. setting:: AUTH_LDAP_CONNECTION_OPTIONS

AUTH_LDAP_CONNECTION_OPTIONS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``{}``

A dictionary of options to pass to each connection to the LDAP server via
``LDAPObject.set_option()``. Keys are `ldap.OPT_*
<http://python-ldap.org/doc/html/ldap.html#options>`_ constants.


.. setting:: AUTH_LDAP_DENY_GROUP

AUTH_LDAP_DENY_GROUP
~~~~~~~~~~~~~~~~~~~~~~~

Default: ``None``

The distinguished name of a group; authentication will fail for any user
that belongs to this group.


.. setting:: AUTH_LDAP_FIND_GROUP_PERMS

AUTH_LDAP_FIND_GROUP_PERMS
~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``False``

If ``True``, :class:`~django_auth_ldap.backend.LDAPBackend` will furnish group
permissions based on the LDAP groups the authenticated user belongs to.
:setting:`AUTH_LDAP_GROUP_SEARCH` and :setting:`AUTH_LDAP_GROUP_TYPE` must also be
set.


.. setting:: AUTH_LDAP_GLOBAL_OPTIONS

AUTH_LDAP_GLOBAL_OPTIONS
~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``{}``

A dictionary of options to pass to ``ldap.set_option()``. Keys are
`ldap.OPT_* <http://python-ldap.org/doc/html/ldap.html#options>`_ constants.

.. note::

    Due to its global nature, this setting ignores the :doc:`settings prefix
    <multiconfig>`. Regardless of how many backends are installed, this setting
    is referenced once by its default name at the time we load the ldap module.


.. setting:: AUTH_LDAP_GROUP_CACHE_TIMEOUT

AUTH_LDAP_GROUP_CACHE_TIMEOUT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``None``

If :setting:`AUTH_LDAP_CACHE_GROUPS` is ``True``, this is the cache timeout for
group memberships. If ``None``, the global cache timeout will be used.


.. setting:: AUTH_LDAP_GROUP_SEARCH

AUTH_LDAP_GROUP_SEARCH
~~~~~~~~~~~~~~~~~~~~~~

Default: ``None``

An :class:`~django_auth_ldap.config.LDAPSearch` object that finds all LDAP
groups that users might belong to. If your configuration makes any references to
LDAP groups, this and :setting:`AUTH_LDAP_GROUP_TYPE` must be set.


.. setting:: AUTH_LDAP_GROUP_TYPE

AUTH_LDAP_GROUP_TYPE
~~~~~~~~~~~~~~~~~~~~

Default: ``None``

An :class:`~django_auth_ldap.config.LDAPGroupType` instance describing the type
of group returned by :setting:`AUTH_LDAP_GROUP_SEARCH`.


.. setting:: AUTH_LDAP_MIRROR_GROUPS

AUTH_LDAP_MIRROR_GROUPS
~~~~~~~~~~~~~~~~~~~~~~~

Default: ``None``

If ``True``, :class:`~django_auth_ldap.backend.LDAPBackend` will mirror a user's
LDAP group membership in the Django database. Any time a user authenticates, we
will create all of their LDAP groups as Django groups and update their Django
group membership to exactly match their LDAP group membership. If the LDAP
server has nested groups, the Django database will end up with a flattened
representation.

This can also be a list or other collection of group names, in which case we'll
only mirror those groups and leave the rest alone. This is ignored if
:setting:`AUTH_LDAP_MIRROR_GROUPS_EXCEPT` is set.


.. setting:: AUTH_LDAP_MIRROR_GROUPS_EXCEPT

AUTH_LDAP_MIRROR_GROUPS_EXCEPT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``None``

If this is not ``None``, it must be a list or other collection of group names.
This will enable group mirroring, except that we'll never change the membership
of the indicated groups. :setting:`AUTH_LDAP_MIRROR_GROUPS` is ignored in this
case.


.. setting:: AUTH_LDAP_PERMIT_EMPTY_PASSWORD

AUTH_LDAP_PERMIT_EMPTY_PASSWORD
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``False``

If ``False`` (the default), authentication with an empty password will fail
immediately, without any LDAP communication. This is a secure default, as some
LDAP servers are configured to allow binds to succeed with no password, perhaps
at a reduced level of access. If you need to make use of this LDAP feature, you
can change this setting to ``True``.


.. setting:: AUTH_LDAP_REQUIRE_GROUP

AUTH_LDAP_REQUIRE_GROUP
~~~~~~~~~~~~~~~~~~~~~~~

Default: ``None``

The distinguished name of a group; authentication will fail for any user that
does not belong to this group. This can also be an
:class:`~django_auth_ldap.config.LDAPGroupQuery` instance.


.. setting:: AUTH_LDAP_SERVER_URI

AUTH_LDAP_SERVER_URI
~~~~~~~~~~~~~~~~~~~~

Default: ``'ldap://localhost'``

The URI of the LDAP server. This can be any URI that is supported by your
underlying LDAP libraries.


.. setting:: AUTH_LDAP_START_TLS

AUTH_LDAP_START_TLS
~~~~~~~~~~~~~~~~~~~

Default: ``False``

If ``True``, each connection to the LDAP server will call
:meth:`~ldap.LDAPObject.start_tls_s` to enable TLS encryption over the standard
LDAP port. There are a number of configuration options that can be given to
:setting:`AUTH_LDAP_GLOBAL_OPTIONS` that affect the TLS connection. For example,
:data:`ldap.OPT_X_TLS_REQUIRE_CERT` can be set to :data:`ldap.OPT_X_TLS_NEVER`
to disable certificate verification, perhaps to allow self-signed certificates.


.. setting:: AUTH_LDAP_USER_QUERY_FIELD

AUTH_LDAP_USER_QUERY_FIELD
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``None``

The field on the user model used to query the authenticating user in the
database. If unset, uses the value of ``USERNAME_FIELD`` of the model class.
When set, the value used to query is obtained through the
:setting:`AUTH_LDAP_USER_ATTR_MAP`.


.. setting:: AUTH_LDAP_USER_ATTRLIST

AUTH_LDAP_USER_ATTRLIST
~~~~~~~~~~~~~~~~~~~~~~~

Default: ``None``

A list of attribute names to load for the authenticated user. Normally, you can
ignore this and the LDAP server will send back all of the attributes of the
directory entry. One reason you might need to override this is to get
operational attributes, which are not normally included::

    AUTH_LDAP_USER_ATTRLIST = ['*', '+']


.. setting:: AUTH_LDAP_USER_ATTR_MAP

AUTH_LDAP_USER_ATTR_MAP
~~~~~~~~~~~~~~~~~~~~~~~

Default: ``{}``

A mapping from :class:`~django.contrib.auth.models.User` field names to LDAP
attribute names. A users's :class:`~django.contrib.auth.models.User` object will
be populated from his LDAP attributes at login.


.. setting:: AUTH_LDAP_USER_DN_TEMPLATE

AUTH_LDAP_USER_DN_TEMPLATE
~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``None``

A string template that describes any user's distinguished name based on the
username. This must contain the placeholder ``%(user)s``.


.. setting:: AUTH_LDAP_USER_FLAGS_BY_GROUP

AUTH_LDAP_USER_FLAGS_BY_GROUP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``{}``

A mapping from boolean :class:`~django.contrib.auth.models.User` field names to
distinguished names of LDAP groups. The corresponding field is set to ``True``
or ``False`` according to whether the user is a member of the group.

Values may be strings for simple group membership tests or
:class:`~django_auth_ldap.config.LDAPGroupQuery` instances for more complex
cases.


.. setting:: AUTH_LDAP_USER_SEARCH

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

        :param str base_dn: The distinguished name of the search base.
        :param int scope: One of ``ldap.SCOPE_*``.
        :param str filterstr: An optional filter string (e.g.
            '(objectClass=person)'). In order to be valid, ``filterstr`` must be
            enclosed in parentheses.


.. class:: LDAPSearchUnion

    .. versionadded:: 1.1

    .. method:: __init__(\*searches)

        :param searches: Zero or more LDAPSearch objects. The result of the
            overall search is the union (by DN) of the results of the underlying
            searches. The precedence of the underlying results and the ordering
            of the final results are both undefined.
        :type searches: :class:`LDAPSearch`


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


.. class:: NISGroupType

    A concrete subclass of :class:`~django_auth_ldap.config.LDAPGroupType` that
    handles the ``nisNetgroup`` object class.

    .. method:: __init__(name_attr='cn')


.. class:: MemberDNGroupType

    A concrete subclass of
    :class:`~django_auth_ldap.config.LDAPGroupType` that handles grouping
    mechanisms wherein the group object contains a list of its member DNs.

    .. method:: __init__(member_attr, name_attr='cn')

        :param str member_attr: The attribute on the group object that contains
            a list of member DNs. 'member' and 'uniqueMember' are common
            examples.


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


.. class:: OrganizationalRoleGroupType

    A concrete subclass of :class:`~django_auth_ldap.config.MemberDNGroupType`
    that handles the ``organizationalRole`` object class. Equivalent to
    ``MemberDNGroupType('roleOccupant')``.

    .. method:: __init__(name_attr='cn')


.. class:: NestedOrganizationalRoleGroupType

    A concrete subclass of
    :class:`~django_auth_ldap.config.NestedMemberDNGroupType` that handles the
    ``organizationalRole`` object class. Equivalent to
    ``NestedMemberDNGroupType('roleOccupant')``.

    .. method:: __init__(name_attr='cn')


.. class:: LDAPGroupQuery

    Represents a compound query for group membership.

    This can be used to construct an arbitrarily complex group membership query
    with AND, OR, and NOT logical operators. Construct primitive queries with a
    group DN as the only argument. These queries can then be combined with the
    ``&``, ``|``, and ``~`` operators.

    This is used by certain settings, including
    :setting:`AUTH_LDAP_REQUIRE_GROUP` and
    :setting:`AUTH_LDAP_USER_FLAGS_BY_GROUP`. An example is shown in
    :ref:`limiting-access`.

    .. method:: __init__(group_dn)

        :param str group_dn: The distinguished name of a group to test for
            membership.


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

.. data:: ldap_error


    This is a Django signal that is sent when we receive an
    :exc:`ldap.LDAPError` exception. The signal has three keyword arguments:

    - ``context``: one of ``'authenticate'``, ``'get_group_permissions'``, or
      ``'populate_user'``, indicating which API was being called when the
      exception was caught.
    - ``user``: the Django user being processed (if available).
    - ``exception``: the :exc:`~ldap.LDAPError` object itself.

    The sender is the :class:`~django_auth_ldap.backend.LDAPBackend` class (or
    subclass).

.. class:: LDAPBackend

    :class:`~django_auth_ldap.backend.LDAPBackend` has one method that may be
    called directly and several that may be overridden in subclasses.

    .. data:: settings_prefix

        A prefix for all of our Django settings. By default, this is
        ``'AUTH_LDAP_'``, but subclasses can override this. When different
        subclasses use different prefixes, they can both be installed and
        operate independently.

    .. data:: default_settings

        A dictionary of default settings. This is empty in
        :class:`~django_auth_ldap.backend.LDAPBackend`, but subclasses can
        populate this with values that will override the built-in defaults. Note
        that the keys should omit the ``'AUTH_LDAP_'`` prefix.

    .. method:: populate_user(username)

        Populates the Django user for the given LDAP username. This connects to
        the LDAP directory with the default credentials and attempts to populate
        the indicated Django user as if they had just logged in.
        :setting:`AUTH_LDAP_ALWAYS_UPDATE_USER` is ignored (assumed ``True``).

    .. method:: get_user_model(self)

        Returns the user model that
        :meth:`~django_auth_ldap.backend.LDAPBackend.get_or_build_user` will
        instantiate. By default, custom user models will be respected.
        Subclasses would most likely override this in order to substitute a
        :ref:`proxy model <proxy-models>`.

    .. method:: authenticate_ldap_user(self, ldap_user, password)

       Given an LDAP user object and password, authenticates the user and
       returns a Django user object. See :ref:`customizing-authentication`.

    .. method:: get_or_build_user(self, username, ldap_user)

        Given a username and an LDAP user object, this must return a valid
        Django user model instance. The ``username`` argument has already been
        passed through
        :meth:`~django_auth_ldap.backend.LDAPBackend.ldap_to_django_username`.
        You can get information about the LDAP user via ``ldap_user.dn`` and
        ``ldap_user.attrs``. The return value must be the same as
        :meth:`~django.db.models.query.QuerySet.get_or_create`--an (instance,
        created) two-tuple--although the instance does not need to be saved yet.

        The default implementation looks for the username with a
        case-insensitive query; if it's not found, the model returned by
        :meth:`~django_auth_ldap.backend.LDAPBackend.get_user_model` will be
        created with the lowercased username. New users will not be saved to the
        database until after the :data:`django_auth_ldap.backend.populate_user`
        signal has been sent.

        A subclass may override this to associate LDAP users to Django users any
        way it likes.

    .. method:: get_or_create_user(self, username, ldap_user)

        .. warning::

            Deprecated. This is supported for backwards-compatibility, but will
            be removed in a future version.

        Like :meth:`get_or_build_user`, but always returns a saved model
        instance. If you're overriding this, please convert to the new method.

    .. method:: ldap_to_django_username(username)

        Returns a valid Django username based on the given LDAP username (which
        is what the user enters). By default, ``username`` is returned
        unchanged. This can be overridden by subclasses.

    .. method:: django_to_ldap_username(username)

        The inverse of
        :meth:`~django_auth_ldap.backend.LDAPBackend.ldap_to_django_username`.
        If this is not symmetrical to
        :meth:`~django_auth_ldap.backend.LDAPBackend.ldap_to_django_username`,
        the behavior is undefined.

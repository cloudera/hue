Working With Groups
===================

Types of Groups
---------------

Working with groups in LDAP can be a tricky business, mostly because there are
so many different kinds. This module includes an extensible API for working with
any kind of group and includes implementations for the most common ones.
:class:`~django_auth_ldap.config.LDAPGroupType` is a base class whose concrete
subclasses can determine group membership for particular grouping mechanisms.
Four built-in subclasses cover most grouping mechanisms:

    * :class:`~django_auth_ldap.config.PosixGroupType`
    * :class:`~django_auth_ldap.config.NISGroupType`
    * :class:`~django_auth_ldap.config.MemberDNGroupType`
    * :class:`~django_auth_ldap.config.NestedMemberDNGroupType`

posixGroup and nisNetgroup objects are somewhat specialized, so they get their
own classes. The other two cover mechanisms whereby a group object stores a list
of its members as distinguished names. This includes groupOfNames,
groupOfUniqueNames, and Active Directory groups, among others. The nested
variant allows groups to contain other groups, to as many levels as you like.
For convenience and readability, several trivial subclasses of the above are
provided:

    * :class:`~django_auth_ldap.config.GroupOfNamesType`
    * :class:`~django_auth_ldap.config.NestedGroupOfNamesType`
    * :class:`~django_auth_ldap.config.GroupOfUniqueNamesType`
    * :class:`~django_auth_ldap.config.NestedGroupOfUniqueNamesType`
    * :class:`~django_auth_ldap.config.ActiveDirectoryGroupType`
    * :class:`~django_auth_ldap.config.NestedActiveDirectoryGroupType`
    * :class:`~django_auth_ldap.config.OrganizationalRoleGroupType`
    * :class:`~django_auth_ldap.config.NestedOrganizationalRoleGroupType`


Finding Groups
--------------

To get started, you'll need to provide some basic information about your LDAP
groups. :setting:`AUTH_LDAP_GROUP_SEARCH` is an
:class:`~django_auth_ldap.config.LDAPSearch` object that identifies the set of
relevant group objects. That is, all groups that users might belong to as well
as any others that we might need to know about (in the case of nested groups,
for example). :setting:`AUTH_LDAP_GROUP_TYPE` is an instance of the class
corresponding to the type of group that will be returned by
:setting:`AUTH_LDAP_GROUP_SEARCH`. All groups referenced elsewhere in the
configuration must be of this type and part of the search results.

.. code-block:: python

    import ldap
    from django_auth_ldap.config import LDAPSearch, GroupOfNamesType

    AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=groups,dc=example,dc=com",
        ldap.SCOPE_SUBTREE, "(objectClass=groupOfNames)"
    )
    AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()


.. _limiting-access:

Limiting Access
---------------

The simplest use of groups is to limit the users who are allowed to log in. If
:setting:`AUTH_LDAP_REQUIRE_GROUP` is set, then only users who are members of
that group will successfully authenticate. :setting:`AUTH_LDAP_DENY_GROUP` is
the reverse: if given, members of this group will be rejected.

.. code-block:: python

    AUTH_LDAP_REQUIRE_GROUP = "cn=enabled,ou=groups,dc=example,dc=com"
    AUTH_LDAP_DENY_GROUP = "cn=disabled,ou=groups,dc=example,dc=com"

However, these two settings alone may not be enough to satisfy your needs. In
such cases, you can use the :class:`~django_auth_ldap.config.LDAPGroupQuery`
object to perform more complex matches against a user's groups. For example:

.. code-block:: python

    from django_auth_ldap.config import LDAPGroupQuery

    AUTH_LDAP_REQUIRE_GROUP = (
        (
            LDAPGroupQuery("cn=enabled,ou=groups,dc=example,dc=com") |
            LDAPGroupQuery("cn=also_enabled,ou=groups,dc=example,dc=com")
        ) &
        ~LDAPGroupQuery("cn=disabled,ou=groups,dc=example,dc=com")
    )

It is important to note a couple features of the example above. First and foremost,
this handles the case of both `AUTH_LDAP_REQUIRE_GROUP` and `AUTH_LDAP_DENY_GROUP`
in one setting. Second, you can use three operators on these queries: ``&``, ``|``,
and ``~``: ``and``, ``or``, and ``not``, respectively.

When groups are configured, you can always get the list of a user's groups from
``user.ldap_user.group_dns`` or ``user.ldap_user.group_names``. More advanced
uses of groups are covered in the next two sections.

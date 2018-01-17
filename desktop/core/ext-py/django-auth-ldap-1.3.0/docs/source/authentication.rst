Authentication
==============

Server Config
-------------

If your LDAP server isn't running locally on the default port, you'll want to
start by setting :setting:`AUTH_LDAP_SERVER_URI` to point to your server. The
value of this setting can be anything that your LDAP library supports. For
instance, openldap may allow you to give a comma- or space-separated list of
URIs to try in sequence.

.. code-block:: python

    AUTH_LDAP_SERVER_URI = "ldap://ldap.example.com"

If your server location is even more dynamic than this, you may provide a
function (or any callable object) that returns the URI. You should assume that
this will be called on every request, so if it's an expensive operation, some
caching is in order.

.. code-block:: python

    from my_module import find_my_ldap_server

    AUTH_LDAP_SERVER_URI = find_my_ldap_server

If you need to configure any python-ldap options, you can set
:setting:`AUTH_LDAP_GLOBAL_OPTIONS` and/or
:setting:`AUTH_LDAP_CONNECTION_OPTIONS`. For example, disabling referrals is not
uncommon::

    import ldap

    AUTH_LDAP_CONNECTION_OPTIONS = {
        ldap.OPT_REFERRALS: 0
    }


Search/Bind
-----------

Now that you can talk to your LDAP server, the next step is to authenticate a
username and password. There are two ways to do this, called search/bind and
direct bind. The first one involves connecting to the LDAP server either
anonymously or with a fixed account and searching for the distinguished name of
the authenticating user. Then we can attempt to bind again with the user's
password. The second method is to derive the user's DN from his username and
attempt to bind as the user directly.

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
anonymously, you can set :setting:`AUTH_LDAP_BIND_DN` to the distinguished name
of an authorized user and :setting:`AUTH_LDAP_BIND_PASSWORD` to the password.

Search Unions
^^^^^^^^^^^^^

.. versionadded:: 1.1

If you need to search in more than one place for a user, you can use
:class:`~django_auth_ldap.config.LDAPSearchUnion`. This takes multiple
LDAPSearch objects and returns the union of the results. The precedence of the
underlying searches is unspecified.

.. code-block:: python

    import ldap
    from django_auth_ldap.config import LDAPSearch, LDAPSearchUnion

    AUTH_LDAP_USER_SEARCH = LDAPSearchUnion(
        LDAPSearch("ou=users,dc=example,dc=com", ldap.SCOPE_SUBTREE, "(uid=%(user)s)"),
        LDAPSearch("ou=otherusers,dc=example,dc=com", ldap.SCOPE_SUBTREE, "(uid=%(user)s)"),
    )


Direct Bind
-----------

To skip the search phase, set :setting:`AUTH_LDAP_USER_DN_TEMPLATE` to a
template that will produce the authenticating user's DN directly. This template
should have one placeholder, ``%(user)s``. If the first example had used
``ldap.SCOPE_ONELEVEL``, the following would be a more straightforward (and
efficient) equivalent::

    AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=users,dc=example,dc=com"


.. _customizing-authentication:

Customizing Authentication
--------------------------

.. versionadded:: 1.3

It is possible to further customize the authentication process by subclassing
:class:`~django_auth_ldap.backend.LDAPBackend` and overriding
:meth:`~django_auth_ldap.backend.LDAPBackend.authenticate_ldap_user`. The first
argument is the unauthenticated :ref:`ldap_user <ldap_user>`, the second is the
supplied password. The intent is to give subclasses a simple pre- and
post-authentication hook.

If a subclass decides to proceed with the authentication, it must call the
inherited implementation. It may then return either the authenticated user or
``None``. The behavior of any other return value--such as substituting a
different user object--is undefined. :doc:`users` has more on managing Django
user objects.

Obviously, it is always safe to access ``ldap_user.dn`` before authenticating
the user. Accessing ``ldap_user.attrs`` and others should be safe unless you're
relying on special binding behavior, such as
:setting:`AUTH_LDAP_BIND_AS_AUTHENTICATING_USER`.

Notes
-----

LDAP is fairly flexible when it comes to matching DNs.
:class:`~django_auth_ldap.backend.LDAPBackend` makes an effort to accommodate
this by forcing usernames to lower case when creating Django users and trimming
whitespace when authenticating.

Some LDAP servers are configured to allow users to bind without a password. As a
precaution against false positives,
:class:`~django_auth_ldap.backend.LDAPBackend` will summarily reject any
authentication attempt with an empty password. You can disable this behavior by
setting :setting:`AUTH_LDAP_PERMIT_EMPTY_PASSWORD` to True.

By default, all LDAP operations are performed with the
:setting:`AUTH_LDAP_BIND_DN` and :setting:`AUTH_LDAP_BIND_PASSWORD` credentials,
not with the user's. Otherwise, the LDAP connection would be bound as the
authenticating user during login requests and as the default credentials during
other requests, so you might see inconsistent LDAP attributes depending on the
nature of the Django view. If you're willing to accept the inconsistency in
order to retrieve attributes while bound as the authenticating user, see
:setting:`AUTH_LDAP_BIND_AS_AUTHENTICATING_USER`.

By default, LDAP connections are unencrypted and make no attempt to protect
sensitive information, such as passwords. When communicating with an LDAP server
on localhost or on a local network, this might be fine. If you need a secure
connection to the LDAP server, you can either use an ``ldaps://`` URL or enable
the StartTLS extension. The latter is generally the preferred mechanism. To
enable StartTLS, set :setting:`AUTH_LDAP_START_TLS` to ``True``::

    AUTH_LDAP_START_TLS = True

If :class:`~django_auth_ldap.backend.LDAPBackend` receives an
:exc:`~ldap.LDAPError` from python_ldap, it will normally swallow it and log a
warning. If you'd like to perform any special handling for these exceptions, you
can add a signal handler to :data:`django_auth_ldap.backend.ldap_error`. The
signal handler can handle the exception any way you like, including re-raising
it or any other exception.

User objects
============

Authenticating against an external source is swell, but Django's auth module is
tightly bound to a user model. When a user logs in, we have to create a model
object to represent them in the database. Because the LDAP search is
case-insensitive, the default implementation also searches for existing Django
users with an iexact query and new users are created with lowercase usernames.
See :meth:`~django_auth_ldap.backend.LDAPBackend.get_or_create_user` if you'd
like to override this behavior. See
:meth:`~django_auth_ldap.backend.LDAPBackend.get_user_model` if you'd like to
substitute a proxy model.

.. note::

    Prior to Django 1.5, user objects were always instances of
    :class:`~django.contrib.auth.models.User`. Current versions of Django
    support custom user models via the :setting:`AUTH_USER_MODEL` setting. As of
    version 1.1.4, django-auth-ldap will respect custom user models.

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
will have an :attr:`ldap_username` attribute with the original (LDAP) username.
:attr:`~django.contrib.auth.models.User.username` (or
:meth:`~django.contrib.auth.models.AbstractBaseUser.get_username`) will, of
course, be the Django username.

.. note::

    Users created by :class:`~django_auth_ldap.backend.LDAPBackend` will have an
    unusable password set. This will only happen when the user is created, so if
    you set a valid password in Django, the user will be able to log in through
    :class:`~django.contrib.auth.backends.ModelBackend` (if configured) even if
    they are rejected by LDAP. This is not generally recommended, but could be
    useful as a fail-safe for selected users in case the LDAP server is
    unavailable.


User Attributes
---------------

LDAP directories tend to contain much more information about users that you may
wish to propagate. A pair of settings, :setting:`AUTH_LDAP_USER_ATTR_MAP` and
:setting:`AUTH_LDAP_PROFILE_ATTR_MAP`, serve to copy directory information into
:class:`~django.contrib.auth.models.User` and profile objects. These are
dictionaries that map user and profile model keys, respectively, to
(case-insensitive) LDAP attribute names::

    AUTH_LDAP_USER_ATTR_MAP = {"first_name": "givenName", "last_name": "sn"}
    AUTH_LDAP_PROFILE_ATTR_MAP = {"home_directory": "homeDirectory"}

Only string fields can be mapped to attributes. Boolean fields can be defined by
group membership::

    AUTH_LDAP_USER_FLAGS_BY_GROUP = {
        "is_active": "cn=active,ou=groups,dc=example,dc=com",
        "is_staff": ["cn=staff,ou=groups,dc=example,dc=com",
                     "cn=admin,ou=groups,dc=example,dc=com"],
        "is_superuser": "cn=superuser,ou=groups,dc=example,dc=com"
    }

    AUTH_LDAP_PROFILE_FLAGS_BY_GROUP = {
        "is_awesome": ["cn=awesome,ou=groups,dc=example,dc=com"]
    }

If a list of groups is given, the flag will be set if the user is a member of
any group.


Updating Users
--------------

By default, all mapped user fields will be updated each time the user logs in.
To disable this, set :setting:`AUTH_LDAP_ALWAYS_UPDATE_USER` to ``False``. If
you need to populate a user outside of the authentication process—for example,
to create associated model objects before the user logs in for the first
time—you can call :meth:`django_auth_ldap.backend.LDAPBackend.populate_user`.
You'll need an instance of :class:`~django_auth_ldap.backend.LDAPBackend`, which
you should feel free to create yourself.
:meth:`~django_auth_ldap.backend.LDAPBackend.populate_user` returns the
:class:`~django.contrib.auth.models.User` or `None` if the user could not be
found in LDAP.

.. code-block:: python

    from django_auth_ldap.backend import LDAPBackend

    user = LDAPBackend().populate_user('alice')
    if user is None:
        raise Exception('No user named alice')


Direct Attribute Access
-----------------------

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
      :setting:`AUTH_LDAP_MIRROR_GROUPS` is used.

Python-ldap returns all attribute values as utf8-encoded strings. For
convenience, this module will try to decode all values into Unicode strings. Any
string that can not be successfully decoded will be left as-is; this may apply
to binary values such as Active Directory's objectSid.


Custom Field Population
-----------------------

If you would like to perform any additional population of user or profile
objects, :mod:`django_auth_ldap.backend` exposes two custom signals to help:
:data:`~django_auth_ldap.backend.populate_user` and
:data:`~django_auth_ldap.backend.populate_user_profile`. These are sent after
the backend has finished populating the respective objects and before they are
saved to the database. You can use this to propagate additional information from
the LDAP directory to the user and profile objects any way you like.

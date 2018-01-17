User objects
============

Authenticating against an external source is swell, but Django's auth module is
tightly bound to a user model. When a user logs in, we have to create a model
object to represent them in the database. Because the LDAP search is
case-insensitive, the default implementation also searches for existing Django
users with an iexact query and new users are created with lowercase usernames.
See :meth:`~django_auth_ldap.backend.LDAPBackend.get_or_build_user` if you'd
like to override this behavior. See
:meth:`~django_auth_ldap.backend.LDAPBackend.get_user_model` if you'd like to
substitute a proxy model.

By default, lookups on existing users are done using the user model's
:attr:`~django.contrib.auth.models.CustomUser.USERNAME_FIELD`. To lookup by a
different field, use :setting:`AUTH_LDAP_USER_LOOKUP_FIELD`. When set, the
username field is ignored.

When using the default for lookups, the only required field for a user is the
username. The default :class:`~django.contrib.auth.models.User` model can be
picky about the characters allowed in usernames, so
:class:`~django_auth_ldap.backend.LDAPBackend` includes a pair of hooks,
:meth:`~django_auth_ldap.backend.LDAPBackend.ldap_to_django_username` and
:meth:`~django_auth_ldap.backend.LDAPBackend.django_to_ldap_username`, to
translate between LDAP usernames and Django usernames. You may need this, for
example, if your LDAP names have periods in them. You can subclass
:class:`~django_auth_ldap.backend.LDAPBackend` to implement these hooks; by
default the username is not modified. :class:`~django.contrib.auth.models.User`
objects that are authenticated by
:class:`~django_auth_ldap.backend.LDAPBackend` will have an
:attr:`ldap_username` attribute with the original (LDAP) username.
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


Populating Users
----------------

You can perform arbitrary population of your user models by adding listeners to
the :mod:`Django signal <django:django.dispatch>`:
:data:`django_auth_ldap.backend.populate_user`. This signal is sent after the
user object has been created and any configured attribute mapping has been
applied (see below). You can use this to propagate information from the LDAP
directory to the user object any way you like. The user instance will be saved
automatically after the signal handlers are run.

If you need an attribute that isn't included by default in the LDAP search
results, see :setting:`AUTH_LDAP_USER_ATTRLIST`.


Easy Attributes
---------------

If you just want to copy a few attribute values directly from the user's LDAP
directory entry to their Django user, the setting,
:setting:`AUTH_LDAP_USER_ATTR_MAP`, makes it easy. This is a dictionary that
maps user model keys, respectively, to (case-insensitive) LDAP attribute
names::

    AUTH_LDAP_USER_ATTR_MAP = {"first_name": "givenName", "last_name": "sn"}

Only string fields can be mapped to attributes. Boolean fields can be defined by
group membership::

    AUTH_LDAP_USER_FLAGS_BY_GROUP = {
        "is_active": "cn=active,ou=groups,dc=example,dc=com",
        "is_staff": (
            LDAPGroupQuery("cn=staff,ou=groups,dc=example,dc=com") |
            LDAPGroupQuery("cn=admin,ou=groups,dc=example,dc=com")
        ),
        "is_superuser": "cn=superuser,ou=groups,dc=example,dc=com"
    }

Values in this dictionary may be simple DNs (as strings), lists or tuples of
DNs, or :class:`~django_auth_ldap.config.LDAPGroupQuery` instances. Lists are
converted to queries joined by ``|``.

Remember that if these settings don't do quite what you want, you can always use
the signals described in the previous section to implement your own logic.


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


.. _ldap_user:

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

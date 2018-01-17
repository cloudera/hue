Multiple LDAP Configs
=====================

.. versionadded:: 1.1

You've probably noticed that all of the settings for this backend have the
prefix AUTH_LDAP\_. This is the default, but it can be customized by subclasses
of :class:`~django_auth_ldap.backend.LDAPBackend`. The main reason you would
want to do this is to create two backend subclasses that reference different
collections of settings and thus operate independently. For example, you might
have two separate LDAP servers that you want to authenticate against. A short
example should demonstrate this:

.. code-block:: python

    # mypackage.ldap

    from django_auth_ldap.backend import LDAPBackend

    class LDAPBackend1(LDAPBackend):
        settings_prefix = "AUTH_LDAP_1_"

    class LDAPBackend2(LDAPBackend):
        settings_prefix = "AUTH_LDAP_2_"


.. code-block:: python

    # settings.py

    AUTH_LDAP_1_SERVER_URI = "ldap://ldap1.example.com"
    AUTH_LDAP_1_USER_DN_TEMPLATE = "uid=%(user)s,ou=users,dc=example,dc=com"

    AUTH_LDAP_2_SERVER_URI = "ldap://ldap2.example.com"
    AUTH_LDAP_2_USER_DN_TEMPLATE = "uid=%(user)s,ou=users,dc=example,dc=com"

    AUTHENTICATION_BACKENDS = (
        "mypackage.ldap.LDAPBackend1",
        "mypackage.ldap.LDAPBackend2",
    )

All of the usual rules apply: Django will attempt to authenticate a user with
each backend in turn until one of them succeeds. When a particular backend
successfully authenticates a user, that user will be linked to the backend for
the duration of their session.

.. note::

    Due to its global nature, :setting:`AUTH_LDAP_GLOBAL_OPTIONS` ignores the
    settings prefix. Regardless of how many backends are installed, this setting
    is referenced once by its default name at the time we load the ldap module.

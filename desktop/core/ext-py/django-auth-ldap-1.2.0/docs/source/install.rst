Installation
============

This authentication backend enables a Django project to authenticate against any
LDAP server. To use it, add :class:`django_auth_ldap.backend.LDAPBackend` to
:django:setting:`AUTHENTICATION_BACKENDS`. Adding `django_auth_ldap` to
:django:setting:`INSTALLED_APPS` is not recommended unless you would like to run
the unit tests. LDAP configuration can be as simple as a single distinguished
name template, but there are many rich options for working with
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

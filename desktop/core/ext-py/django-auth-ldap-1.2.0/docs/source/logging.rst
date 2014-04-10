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

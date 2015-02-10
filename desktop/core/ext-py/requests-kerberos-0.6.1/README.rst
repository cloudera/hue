requests Kerberos/GSSAPI authentication library
===============================================

Requests is an HTTP library, written in Python, for human beings. This library
adds optional Kerberos/GSSAPI authentication support and supports mutual
authentication. Basic GET usage:


.. code-block:: pycon

    >>> import requests
    >>> from requests_kerberos import HTTPKerberosAuth
    >>> r = requests.get("http://example.org", auth=HTTPKerberosAuth())
    ...

The entire ``requests.api`` should be supported.

Authentication Failures
-----------------------

Client authentication failures will be communicated to the caller by returning
the 401 response.

Mutual Authentication
---------------------

By default, ``HTTPKerberosAuth`` will require mutual authentication from the
server, and if a server emits a non-error response which cannot be
authenticated, a ``requests_kerberos.errors.MutualAuthenticationError`` will be
raised. If a server emits an error which cannot be authenticated, it will be
returned to the user but with its contents and headers stripped.

OPTIONAL
^^^^^^^^

If you'd prefer to not require mutual authentication, you can set your
preference when constructing your ``HTTPKerberosAuth`` object:

.. code-block:: pycon

    >>> import requests
    >>> from requests_kerberos import HTTPKerberosAuth, OPTIONAL
    >>> kerberos_auth = HTTPKerberosAuth(mutual_authentication=OPTIONAL)
    >>> r = requests.get("http://example.org", auth=kerberos_auth)
    ...

This will cause ``requests_kerberos`` to attempt mutual authentication if the
server advertises that it supports it, and cause a failure if authentication
fails, but not if the server does not support it at all.

DISABLED
^^^^^^^^

While we don't recommend it, if you'd prefer to never attempt mutual
authentication, you can do that as well:

.. code-block:: pycon

    >>> import requests
    >>> from requests_kerberos import HTTPKerberosAuth, DISABLED
    >>> kerberos_auth = HTTPKerberosAuth(mutual_authentication=DISABLED)
    >>> r = requests.get("http://example.org", auth=kerberos_auth)
    ...

Logging
-------

This library makes extensive use of Python's logging facilities.

Log messages are logged to the ``requests_kerberos`` and
``requests_kerberos.kerberos_`` named loggers.

If you are having difficulty we suggest you configure logging. Issues with the
underlying kerberos libraries will be made apparent. Additionally, copious debug
information is made available which may assist in troubleshooting if you
increase your log level all the way up to debug.

requests Kerberos/GSSAPI authentication library
===============================================

.. image:: https://travis-ci.org/requests/requests-kerberos.svg?branch=master
    :target: https://travis-ci.org/requests/requests-kerberos

.. image:: https://coveralls.io/repos/github/requests/requests-kerberos/badge.svg?branch=master
    :target: https://coveralls.io/github/requests/requests-kerberos?branch=master

Requests is an HTTP library, written in Python, for human beings. This library
adds optional Kerberos/GSSAPI authentication support and supports mutual
authentication. Basic GET usage:


.. code-block:: python

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

REQUIRED
^^^^^^^^

By default, ``HTTPKerberosAuth`` will require mutual authentication from the
server, and if a server emits a non-error response which cannot be
authenticated, a ``requests_kerberos.errors.MutualAuthenticationError`` will
be raised. If a server emits an error which cannot be authenticated, it will
be returned to the user but with its contents and headers stripped. If the
response content is more important than the need for mutual auth on errors,
(eg, for certain WinRM calls) the stripping behavior can be suppressed by
setting ``sanitize_mutual_error_response=False``:

.. code-block:: python

    >>> import requests
    >>> from requests_kerberos import HTTPKerberosAuth, REQUIRED
    >>> kerberos_auth = HTTPKerberosAuth(mutual_authentication=REQUIRED, sanitize_mutual_error_response=False)
    >>> r = requests.get("https://windows.example.org/wsman", auth=kerberos_auth)
    ...


OPTIONAL
^^^^^^^^

If you'd prefer to not require mutual authentication, you can set your
preference when constructing your ``HTTPKerberosAuth`` object:

.. code-block:: python

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

.. code-block:: python

    >>> import requests
    >>> from requests_kerberos import HTTPKerberosAuth, DISABLED
    >>> kerberos_auth = HTTPKerberosAuth(mutual_authentication=DISABLED)
    >>> r = requests.get("http://example.org", auth=kerberos_auth)
    ...

Preemptive Authentication
-------------------------

``HTTPKerberosAuth`` can be forced to preemptively initiate the Kerberos
GSS exchange and present a Kerberos ticket on the initial request (and all
subsequent). By default, authentication only occurs after a
``401 Unauthorized`` response containing a Kerberos or Negotiate challenge
is received from the origin server. This can cause mutual authentication
failures for hosts that use a persistent connection (eg, Windows/WinRM), as
no Kerberos challenges are sent after the initial auth handshake. This
behavior can be altered by setting  ``force_preemptive=True``:

.. code-block:: python
    
    >>> import requests
    >>> from requests_kerberos import HTTPKerberosAuth, REQUIRED
    >>> kerberos_auth = HTTPKerberosAuth(mutual_authentication=REQUIRED, force_preemptive=True)
    >>> r = requests.get("https://windows.example.org/wsman", auth=kerberos_auth)
    ...

Hostname Override
-----------------

If communicating with a host whose DNS name doesn't match its
kerberos hostname (eg, behind a content switch or load balancer),
the hostname used for the Kerberos GSS exchange can be overridden by
setting the ``hostname_override`` arg:

.. code-block:: python

    >>> import requests
    >>> from requests_kerberos import HTTPKerberosAuth, REQUIRED
    >>> kerberos_auth = HTTPKerberosAuth(hostname_override="internalhost.local")
    >>> r = requests.get("https://externalhost.example.org/", auth=kerberos_auth)
    ...

Explicit Principal
------------------

``HTTPKerberosAuth`` normally uses the default principal (ie, the user for
whom you last ran ``kinit`` or ``kswitch``, or an SSO credential if
applicable). However, an explicit principal can be specified, which will
cause Kerberos to look for a matching credential cache for the named user.
This feature depends on OS support for collection-type credential caches,
as well as working principal support in PyKerberos (it is broken in many
builds). An explicit principal can be specified with the ``principal`` arg:

.. code-block:: python

    >>> import requests
    >>> from requests_kerberos import HTTPKerberosAuth, REQUIRED
    >>> kerberos_auth = HTTPKerberosAuth(principal="user@REALM")
    >>> r = requests.get("http://example.org", auth=kerberos_auth)
    ...

On Windows, WinKerberos is used instead of PyKerberos. WinKerberos allows the
use of arbitrary principals instead of a credential cache. Passwords can be
specified by following the form ``user@realm:password`` for ``principal``.

Delegation
----------

``requests_kerberos`` supports credential delegation (``GSS_C_DELEG_FLAG``).
To enable delegation of credentials to a server that requests delegation, pass
``delegate=True`` to ``HTTPKerberosAuth``:

.. code-block:: python

    >>> import requests
    >>> from requests_kerberos import HTTPKerberosAuth
    >>> r = requests.get("http://example.org", auth=HTTPKerberosAuth(delegate=True))
    ...

Be careful to only allow delegation to servers you trust as they will be able
to impersonate you using the delegated credentials.

Logging
-------

This library makes extensive use of Python's logging facilities.

Log messages are logged to the ``requests_kerberos`` and
``requests_kerberos.kerberos_`` named loggers.

If you are having difficulty we suggest you configure logging. Issues with the
underlying kerberos libraries will be made apparent. Additionally, copious debug
information is made available which may assist in troubleshooting if you
increase your log level all the way up to debug.

requests GSSAPI authentication library
===============================================

Requests is an HTTP library, written in Python, for human beings. This library
adds optional GSSAPI authentication support and supports mutual
authentication.

It provides a fully backward-compatible shim for the old
python-requests-kerberos library: simply replace ``import requests_kerberos``
with ``import requests_gssapi``.  A more powerful interface is provided by the
HTTPSPNEGOAuth component, but this is of course not guaranteed to be
compatible.  Documentation below is written toward the new interface.

Basic GET usage:


.. code-block:: python

    >>> import requests
    >>> from requests_gssapi import HTTPSPNEGOAuth
    >>> r = requests.get("http://example.org", auth=HTTPSPNEGOAuth())
    ...

The entire ``requests.api`` should be supported.

Setup
-----

In order to use this library, there must already be a Kerberos Ticket-Granting
Ticket (TGT) in a credential cache (ccache).  Whether a TGT is available can
be easily determined by running the ``klist`` command.  If no TGT is
available, then it first must be obtained (for instance, by running the
``kinit`` command, or pointing the $KRB5CCNAME to a credential cache with a
valid TGT).

In short, the library will handle the "negotiations" of Kerberos
authentication, but ensuring that a credentials are available and valid is the
responsibility of the user.

Authentication Failures
-----------------------

Client authentication failures will be communicated to the caller by returning
a 401 response.  A 401 response may also be the result of expired credentials
(including the TGT).

Mutual Authentication
---------------------

Mutual authentication is a poorly-named feature of the GSSAPI which doesn't
provide any additional security benefit to most possible uses of
requests_gssapi.  Practically speaking, in most mechanism implementations
(including krb5), it requires another round-trip between the client and server
during the authentication handshake.  Many clients and servers do not properly
handle the authentication handshake taking more than one round-trip.  If you
encounter a MutualAuthenticationError, this is probably why.

So long as you're running over a TLS link whose security guarantees you trust,
there's no benefit to mutual authentication.  If you don't trust the link at
all, mutual authentication won't help (since it's not tamper-proof, and GSSAPI
isn't being used post-authentication.  There's some middle ground between the
two where it helps a small amount (e.g., passive adversary over
encrypted-but-unverified channel), but for Negotiate (what we're doing here),
it's not generally helpful.

For a more technical explanation of what mutual authentication actually
guarantees, I refer you to rfc2743 (GSSAPIv2), rfc4120 (krb5 in GSSAPI),
rfc4178 (SPNEGO), and rfc4559 (HTTP Negotiate).


DISABLED
^^^^^^^^

By default, there's no need to explicitly disable mutual authentication.
However, for compatability with older versions of request_gssapi or
requests_kerberos, you can explicitly request it not be attempted:

.. code-block:: python

    >>> import requests
    >>> from requests_gssapi import HTTPSPNEGOAuth, DISABLED
    >>> gssapi_auth = HTTPSPNEGOAuth(mutual_authentication=DISABLED)
    >>> r = requests.get("https://example.org", auth=gssapi_auth)
    ...

REQUIRED
^^^^^^^^

This was historically the default, but no longer is.  If requested,
``HTTPSPNEGOAuth`` will require mutual authentication from the server, and if
a server emits a non-error response which cannot be authenticated, a
``requests_gssapi.errors.MutualAuthenticationError`` will be raised.  (See
above for what this means.)  If a server emits an error which cannot be
authenticated, it will be returned to the user but with its contents and
headers stripped.  If the response content is more important than the need for
mutual auth on errors, (eg, for certain WinRM calls) the stripping behavior
can be suppressed by setting ``sanitize_mutual_error_response=False``:

.. code-block:: python

    >>> import requests
    >>> from requests_gssapi import HTTPSPNEGOAuth, REQUIRED
    >>> gssapi_auth = HTTPSPNEGOAuth(mutual_authentication=REQUIRED, sanitize_mutual_error_response=False)
    >>> r = requests.get("https://windows.example.org/wsman", auth=gssapi_auth)
    ...

OPTIONAL
^^^^^^^^

This will cause ``requests_gssapi`` to attempt mutual authentication if the
server advertises that it supports it, and cause a failure if authentication
fails, but not if the server does not support it at all.  This is probably not
what you want: link tampering will either cause hard failures, or silently
cause it to not happen at all.  It is retained for compatability.

.. code-block:: python

    >>> import requests
    >>> from requests_gssapi import HTTPSPNEGOAuth, OPTIONAL
    >>> gssapi_auth = HTTPSPNEGOAuth(mutual_authentication=OPTIONAL)
    >>> r = requests.get("https://example.org", auth=gssapi_auth)
    ...

Opportunistic Authentication
----------------------------

``HTTPSPNEGOAuth`` can be forced to preemptively initiate the GSSAPI
exchange and present a token on the initial request (and all
subsequent). By default, authentication only occurs after a
``401 Unauthorized`` response containing a Negotiate challenge
is received from the origin server. This can cause mutual authentication
failures for hosts that use a persistent connection (eg, Windows/WinRM), as
no GSSAPI challenges are sent after the initial auth handshake. This
behavior can be altered by setting  ``opportunistic_auth=True``:

.. code-block:: python

    >>> import requests
    >>> from requests_gssapi import HTTPSPNEGOAuth
    >>> gssapi_auth = HTTPSPNEGOAuth(opportunistic_auth=True)
    >>> r = requests.get("https://windows.example.org/wsman", auth=gssapi_auth)
    ...

Hostname Override
-----------------

If communicating with a host whose DNS name doesn't match its
hostname (eg, behind a content switch or load balancer),
the hostname used for the GSSAPI exchange can be overridden by
passing in a custom name (string or ``gssapi.Name``):

.. code-block:: python

    >>> import requests
    >>> from requests_gssapi import HTTPSPNEGOAuth
    >>> gssapi_auth = HTTPSPNEGOAuth(target_name="internalhost.local")
    >>> r = requests.get("https://externalhost.example.org/", auth=gssapi_auth)
    ...

Explicit Principal
------------------

``HTTPSPNEGOAuth`` normally uses the default principal (ie, the user for whom
you last ran ``kinit`` or ``kswitch``, or an SSO credential if
applicable). However, an explicit credential can be in instead, if desired.

.. code-block:: python

    >>> import gssapi
    >>> import requests
    >>> from requests_gssapi import HTTPSPNEGOAuth
    >>> name = gssapi.Name("user@REALM", gssapi.NameType.hostbased_service)
    >>> creds = gssapi.Credentials(name=name, usage="initiate")
    >>> gssapi_auth = HTTPSPNEGOAuth(creds=creds)
    >>> r = requests.get("http://example.org", auth=gssapi_auth)
    ...

Explicit Mechanism
------------------

``HTTPSPNEGOAuth`` normally lets the underlying ``gssapi`` library decide which
negotiation mechanism to use. However, an explicit mechanism can be used instead
if desired. The ``mech`` parameter will be passed straight through to ``gssapi``
without interference. It is expected to be an instance of ``gssapi.mechs.Mechanism``.

.. code-block:: python

    >>> import gssapi
    >>> import requests
    >>> from requests_gssapi import HTTPSPNEGOAuth
    >>> try:
    ...   spnego = gssapi.mechs.Mechanism.from_sasl_name("SPNEGO")
    ... except AttributeError:
    ...   spnego = gssapi.OID.from_int_seq("1.3.6.1.5.5.2")
    >>> gssapi_auth = HTTPSPNEGOAuth(mech=spnego)
    >>> r = requests.get("http://example.org", auth=gssapi_auth)
    ...

Delegation
----------

``requests_gssapi`` supports credential delegation (``GSS_C_DELEG_FLAG``).
To enable delegation of credentials to a server that requests delegation, pass
``delegate=True`` to ``HTTPSPNEGOAuth``:

.. code-block:: python

    >>> import requests
    >>> from requests_gssapi import HTTPSPNEGOAuth
    >>> r = requests.get("http://example.org", auth=HTTPSPNEGOAuth(delegate=True))
    ...

Be careful to only allow delegation to servers you trust as they will be able
to impersonate you using the delegated credentials.

Logging
-------

This library makes extensive use of Python's logging facilities.

Log messages are logged to the ``requests_gssapi`` and
``requests_gssapi.gssapi`` named loggers.

If you are having difficulty we suggest you configure logging. Issues with the
underlying GSSAPI libraries will be made apparent. Additionally, copious debug
information is made available which may assist in troubleshooting if you
increase your log level all the way up to debug.

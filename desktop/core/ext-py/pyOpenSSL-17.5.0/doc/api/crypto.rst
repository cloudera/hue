.. _openssl-crypto:

:py:mod:`crypto` --- Generic cryptographic module
=================================================

.. py:module:: OpenSSL.crypto
   :synopsis: Generic cryptographic module

.. note::

    `pyca/cryptography`_ is likely a better choice than using this module.
    It contains a complete set of cryptographic primitives as well as a significantly better and more powerful X509 API.
    If necessary you can convert to and from cryptography objects using the ``to_cryptography`` and ``from_cryptography`` methods on ``X509``, ``X509Req``, ``CRL``, and ``PKey``.


Elliptic curves
---------------

.. py:function:: get_elliptic_curves

    Return a set of objects representing the elliptic curves supported in the
    OpenSSL build in use.

    The curve objects have a :py:class:`unicode` ``name`` attribute by which
    they identify themselves.

    The curve objects are useful as values for the argument accepted by
    :py:meth:`Context.set_tmp_ecdh` to specify which elliptical curve should be
    used for ECDHE key exchange.


.. py:function:: get_elliptic_curve(name)

    Return a single curve object selected by *name*.

    See :py:func:`get_elliptic_curves` for information about curve objects.

    If the named curve is not supported then :py:class:`ValueError` is raised.


Serialization and deserialization
---------------------------------

The following serialization functions take one of these constants to determine the format.

.. py:data:: FILETYPE_PEM

:data:`FILETYPE_PEM` serializes data to a Base64-encoded encoded representation of the underlying ASN.1 data structure. This representation includes delimiters that define what data structure is contained within the Base64-encoded block: for example, for a certificate, the delimiters are ``-----BEGIN CERTIFICATE-----`` and ``-----END CERTIFICATE-----``.

.. py:data:: FILETYPE_ASN1

:data:`FILETYPE_ASN1` serializes data to the underlying ASN.1 data structure. The format used by :data:`FILETYPE_ASN1` is also sometimes referred to as DER.

Certificates
~~~~~~~~~~~~

.. py:function:: dump_certificate(type, cert)

    Dump the certificate *cert* into a buffer string encoded with the type
    *type*.

.. py:function:: load_certificate(type, buffer)

    Load a certificate (X509) from the string *buffer* encoded with the
    type *type*.

Certificate signing requests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:function:: dump_certificate_request(type, req)

    Dump the certificate request *req* into a buffer string encoded with the
    type *type*.

.. py:function:: load_certificate_request(type, buffer)

    Load a certificate request (X509Req) from the string *buffer* encoded with
    the type *type*.

Private keys
~~~~~~~~~~~~

.. autofunction:: dump_privatekey

.. py:function:: load_privatekey(type, buffer[, passphrase])

    Load a private key (PKey) from the string *buffer* encoded with the type
    *type* (must be one of :py:const:`FILETYPE_PEM` and
    :py:const:`FILETYPE_ASN1`).

    *passphrase* must be either a string or a callback for providing the pass
    phrase.

Public keys
~~~~~~~~~~~

.. autofunction:: dump_publickey

.. autofunction:: load_publickey

Certificate revocation lists
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: dump_crl

.. py:function:: load_crl(type, buffer)

    Load Certificate Revocation List (CRL) data from a string *buffer*.
    *buffer* encoded with the type *type*.  The type *type* must either
    :py:const:`FILETYPE_PEM` or :py:const:`FILETYPE_ASN1`).


.. py:function:: load_pkcs7_data(type, buffer)

    Load pkcs7 data from the string *buffer* encoded with the type
    *type*. The type *type* must either :py:const:`FILETYPE_PEM` or
    :py:const:`FILETYPE_ASN1`).


.. py:function:: load_pkcs12(buffer[, passphrase])

    Load pkcs12 data from the string *buffer*. If the pkcs12 structure is
    encrypted, a *passphrase* must be included.  The MAC is always
    checked and thus required.

    See also the man page for the C function :py:func:`PKCS12_parse`.

Signing and verifying signatures
--------------------------------

.. py:function:: sign(key, data, digest)

    Sign a data string using the given key and message digest.

    *key* is a :py:class:`PKey` instance.  *data* is a ``str`` instance.
    *digest* is a ``str`` naming a supported message digest type, for example
    :py:const:`b"sha256"`.

    .. versionadded:: 0.11


.. py:function:: verify(certificate, signature, data, digest)

    Verify the signature for a data string.

    *certificate* is a :py:class:`X509` instance corresponding to the private
    key which generated the signature.  *signature* is a *str* instance giving
    the signature itself.  *data* is a *str* instance giving the data to which
    the signature applies.  *digest* is a *str* instance naming the message
    digest type of the signature, for example :py:const:`b"sha256"`.

    .. versionadded:: 0.11


.. _openssl-x509:

X509 objects
------------

.. autoclass:: X509
               :members:

.. _openssl-x509name:

X509Name objects
----------------

.. autoclass:: X509Name
               :members:
               :special-members:
               :exclude-members: __repr__, __getattr__, __weakref__

.. _openssl-x509req:

X509Req objects
---------------

.. autoclass:: X509Req
               :members:
               :special-members:
               :exclude-members: __weakref__

.. _openssl-x509store:

X509Store objects
-----------------

.. autoclass:: X509Store
               :members:

.. _openssl-x509storecontexterror:

X509StoreContextError objects
-----------------------------

.. autoclass:: X509StoreContextError
               :members:

.. _openssl-x509storecontext:

X509StoreContext objects
------------------------

.. autoclass:: X509StoreContext
               :members:

.. _openssl-pkey:

X509StoreFlags constants
------------------------

.. autoclass:: X509StoreFlags

    .. data:: CRL_CHECK
    .. data:: CRL_CHECK_ALL
    .. data:: IGNORE_CRITICAL
    .. data:: X509_STRICT
    .. data:: ALLOW_PROXY_CERTS
    .. data:: POLICY_CHECK
    .. data:: EXPLICIT_POLICY
    .. data:: INHIBIT_MAP
    .. data:: NOTIFY_POLICY
    .. data:: CHECK_SS_SIGNATURE
    .. data:: CB_ISSUER_CHECK

.. _openssl-x509storeflags:

PKey objects
------------

.. autoclass:: PKey
               :members:

.. _openssl-pkcs7:

.. py:data:: TYPE_RSA
             TYPE_DSA

    Key type constants.

PKCS7 objects
-------------

PKCS7 objects have the following methods:

.. py:method:: PKCS7.type_is_signed()

    FIXME

.. py:method:: PKCS7.type_is_enveloped()

    FIXME

.. py:method:: PKCS7.type_is_signedAndEnveloped()

    FIXME

.. py:method:: PKCS7.type_is_data()

    FIXME

.. py:method:: PKCS7.get_type_name()

    Get the type name of the PKCS7.

.. _openssl-pkcs12:

PKCS12 objects
--------------

.. autoclass:: PKCS12
               :members:

.. _openssl-509ext:

X509Extension objects
---------------------

.. autoclass:: X509Extension
               :members:
               :special-members:
               :exclude-members: __weakref__

.. _openssl-netscape-spki:

NetscapeSPKI objects
--------------------

.. autoclass:: NetscapeSPKI
               :members:
               :special-members:
               :exclude-members: __weakref__

.. _crl:

CRL objects
-----------

.. autoclass:: CRL
               :members:
               :special-members:
               :exclude-members: __weakref__

.. _revoked:

Revoked objects
---------------

.. autoclass:: Revoked
               :members:

Exceptions
----------

.. py:exception:: Error

    Generic exception used in the :py:mod:`.crypto` module.


Digest names
------------

Several of the functions and methods in this module take a digest name.
These must be strings describing a digest algorithm supported by OpenSSL (by ``EVP_get_digestbyname``, specifically).
For example, :const:`b"sha256"` or :const:`b"sha384"`.

More information and a list of these digest names can be found in the ``EVP_DigestInit(3)`` man page of your OpenSSL installation.
This page can be found online for the latest version of OpenSSL:
https://www.openssl.org/docs/manmaster/man3/EVP_DigestInit.html

.. _`pyca/cryptography`:  https://cryptography.io

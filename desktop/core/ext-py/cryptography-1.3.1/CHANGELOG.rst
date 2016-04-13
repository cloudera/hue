Changelog
=========

1.3.1 - 2016-03-21
~~~~~~~~~~~~~~~~~~

* Fixed a bug that caused an ``AttributeError`` when using ``mock`` to patch
  some ``cryptography`` modules.

1.3 - 2016-03-18
~~~~~~~~~~~~~~~~

* Added support for padding ANSI X.923 with
  :class:`~cryptography.hazmat.primitives.padding.ANSIX923`.
* Deprecated support for OpenSSL 0.9.8. Support will be removed in
  ``cryptography`` 1.4.
* Added support for the :class:`~cryptography.x509.PolicyConstraints`
  X.509 extension including both parsing and generation using
  :class:`~cryptography.x509.CertificateBuilder` and
  :class:`~cryptography.x509.CertificateSigningRequestBuilder`.
* Added :attr:`~cryptography.x509.CertificateSigningRequest.is_signature_valid`
  to :class:`~cryptography.x509.CertificateSigningRequest`.
* Fixed an intermittent ``AssertionError`` when performing an RSA decryption on
  an invalid ciphertext, ``ValueError`` is now correctly raised in all cases.
* Added
  :meth:`~cryptography.x509.AuthorityKeyIdentifier.from_issuer_subject_key_identifier`.

1.2.3 - 2016-03-01
~~~~~~~~~~~~~~~~~~

* Updated Windows and OS X wheels to be compiled against OpenSSL 1.0.2g.

1.2.2 - 2016-01-29
~~~~~~~~~~~~~~~~~~

* Updated Windows and OS X wheels to be compiled against OpenSSL 1.0.2f.

1.2.1 - 2016-01-08
~~~~~~~~~~~~~~~~~~

* Reverts a change to an OpenSSL ``EVP_PKEY`` object that caused errors with
  ``pyOpenSSL``.

1.2 - 2016-01-08
~~~~~~~~~~~~~~~~

* **BACKWARDS INCOMPATIBLE:**
  :class:`~cryptography.x509.RevokedCertificate`
  :attr:`~cryptography.x509.RevokedCertificate.extensions` now uses extension
  classes rather than returning raw values inside the
  :class:`~cryptography.x509.Extension`
  :attr:`~cryptography.x509.Extension.value`. The new classes
  are:

  * :class:`~cryptography.x509.CertificateIssuer`
  * :class:`~cryptography.x509.CRLReason`
  * :class:`~cryptography.x509.InvalidityDate`
* Deprecated support for OpenSSL 0.9.8 and 1.0.0. At this time there is no time
  table for actually dropping support, however we strongly encourage all users
  to upgrade, as those versions no longer receive support from the OpenSSL
  project.
* The :class:`~cryptography.x509.Certificate` class now has
  :attr:`~cryptography.x509.Certificate.signature` and
  :attr:`~cryptography.x509.Certificate.tbs_certificate_bytes` attributes.
* The :class:`~cryptography.x509.CertificateSigningRequest` class now has
  :attr:`~cryptography.x509.CertificateSigningRequest.signature` and
  :attr:`~cryptography.x509.CertificateSigningRequest.tbs_certrequest_bytes`
  attributes.
* The :class:`~cryptography.x509.CertificateRevocationList` class now has
  :attr:`~cryptography.x509.CertificateRevocationList.signature` and
  :attr:`~cryptography.x509.CertificateRevocationList.tbs_certlist_bytes`
  attributes.
* :class:`~cryptography.x509.NameConstraints` are now supported in the
  :class:`~cryptography.x509.CertificateBuilder` and
  :class:`~cryptography.x509.CertificateSigningRequestBuilder`.
* Support serialization of certificate revocation lists using the
  :meth:`~cryptography.x509.CertificateRevocationList.public_bytes` method of
  :class:`~cryptography.x509.CertificateRevocationList`.
* Add support for parsing :class:`~cryptography.x509.CertificateRevocationList`
  :meth:`~cryptography.x509.CertificateRevocationList.extensions` in the
  OpenSSL backend. The following extensions are currently supported:

  * :class:`~cryptography.x509.AuthorityInformationAccess`
  * :class:`~cryptography.x509.AuthorityKeyIdentifier`
  * :class:`~cryptography.x509.CRLNumber`
  * :class:`~cryptography.x509.IssuerAlternativeName`
* Added :class:`~cryptography.x509.CertificateRevocationListBuilder` and
  :class:`~cryptography.x509.RevokedCertificateBuilder` to allow creation of
  CRLs.
* Unrecognized non-critical X.509 extensions are now parsed into an
  :class:`~cryptography.x509.UnrecognizedExtension` object.

1.1.2 - 2015-12-10
~~~~~~~~~~~~~~~~~~

* Fixed a SIGBUS crash with the OS X wheels caused by redefinition of a
  method.
* Fixed a runtime error ``undefined symbol EC_GFp_nistp224_method`` that
  occurred with some OpenSSL installations.
* Updated Windows and OS X wheels to be compiled against OpenSSL 1.0.2e.

1.1.1 - 2015-11-19
~~~~~~~~~~~~~~~~~~

* Fixed several small bugs related to compiling the OpenSSL bindings with
  unusual OpenSSL configurations.
* Resolved an issue where, depending on the method of installation and
  which Python interpreter they were using, users on El Capitan (OS X 10.11)
  may have seen an ``InternalError`` on import.

1.1 - 2015-10-28
~~~~~~~~~~~~~~~~

* Added support for Elliptic Curve Diffie-Hellman with
  :class:`~cryptography.hazmat.primitives.asymmetric.ec.ECDH`.
* Added :class:`~cryptography.hazmat.primitives.kdf.x963kdf.X963KDF`.
* Added support for parsing certificate revocation lists (CRLs) using
  :func:`~cryptography.x509.load_pem_x509_crl` and
  :func:`~cryptography.x509.load_der_x509_crl`.
* Add support for AES key wrapping with
  :func:`~cryptography.hazmat.primitives.keywrap.aes_key_wrap` and
  :func:`~cryptography.hazmat.primitives.keywrap.aes_key_unwrap`.
* Added a ``__hash__`` method to :class:`~cryptography.x509.Name`.
* Add support for encoding and decoding elliptic curve points to a byte string
  form using
  :meth:`~cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePublicNumbers.encode_point`
  and
  :meth:`~cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePublicNumbers.from_encoded_point`.
* Added :meth:`~cryptography.x509.Extensions.get_extension_for_class`.
* :class:`~cryptography.x509.CertificatePolicies` are now supported in the
  :class:`~cryptography.x509.CertificateBuilder`.
* ``countryName`` is now encoded as a ``PrintableString`` when creating subject
  and issuer distinguished names with the Certificate and CSR builder classes.

1.0.2 - 2015-09-27
~~~~~~~~~~~~~~~~~~
* **SECURITY ISSUE**: The OpenSSL backend prior to 1.0.2 made extensive use
  of assertions to check response codes where our tests could not trigger a
  failure.  However, when Python is run with ``-O`` these asserts are optimized
  away.  If a user ran Python with this flag and got an invalid response code
  this could result in undefined behavior or worse. Accordingly, all response
  checks from the OpenSSL backend have been converted from ``assert``
  to a true function call. Credit **Emilia Käsper (Google Security Team)**
  for the report.

1.0.1 - 2015-09-05
~~~~~~~~~~~~~~~~~~

* We now ship OS X wheels that statically link OpenSSL by default. When
  installing a wheel on OS X 10.10+ (and using a Python compiled against the
  10.10 SDK) users will no longer need to compile. See :doc:`/installation` for
  alternate installation methods if required.
* Set the default string mask to UTF-8 in the OpenSSL backend to resolve
  character encoding issues with older versions of OpenSSL.
* Several new OpenSSL bindings have been added to support a future pyOpenSSL
  release.
* Raise an error during install on PyPy < 2.6. 1.0+ requires PyPy 2.6+.

1.0 - 2015-08-12
~~~~~~~~~~~~~~~~

* Switched to the new `cffi`_ ``set_source`` out-of-line API mode for
  compilation. This results in significantly faster imports and lowered
  memory consumption. Due to this change we no longer support PyPy releases
  older than 2.6 nor do we support any released version of PyPy3 (until a
  version supporting cffi 1.0 comes out).
* Fix parsing of OpenSSH public keys that have spaces in comments.
* Support serialization of certificate signing requests using the
  ``public_bytes`` method of
  :class:`~cryptography.x509.CertificateSigningRequest`.
* Support serialization of certificates using the ``public_bytes`` method of
  :class:`~cryptography.x509.Certificate`.
* Add ``get_provisioning_uri`` method to
  :class:`~cryptography.hazmat.primitives.twofactor.hotp.HOTP` and
  :class:`~cryptography.hazmat.primitives.twofactor.totp.TOTP` for generating
  provisioning URIs.
* Add :class:`~cryptography.hazmat.primitives.kdf.concatkdf.ConcatKDFHash`
  and :class:`~cryptography.hazmat.primitives.kdf.concatkdf.ConcatKDFHMAC`.
* Raise a ``TypeError`` when passing objects that are not text as the value to
  :class:`~cryptography.x509.NameAttribute`.
* Add support for :class:`~cryptography.x509.OtherName` as a general name
  type.
* Added new X.509 extension support in :class:`~cryptography.x509.Certificate`
  The following new extensions are now supported:

  * :class:`~cryptography.x509.OCSPNoCheck`
  * :class:`~cryptography.x509.InhibitAnyPolicy`
  * :class:`~cryptography.x509.IssuerAlternativeName`
  * :class:`~cryptography.x509.NameConstraints`

* Extension support was added to
  :class:`~cryptography.x509.CertificateSigningRequest`.
* Add support for creating signed certificates with
  :class:`~cryptography.x509.CertificateBuilder`. This includes support for
  the following extensions:

  * :class:`~cryptography.x509.BasicConstraints`
  * :class:`~cryptography.x509.SubjectAlternativeName`
  * :class:`~cryptography.x509.KeyUsage`
  * :class:`~cryptography.x509.ExtendedKeyUsage`
  * :class:`~cryptography.x509.SubjectKeyIdentifier`
  * :class:`~cryptography.x509.AuthorityKeyIdentifier`
  * :class:`~cryptography.x509.AuthorityInformationAccess`
  * :class:`~cryptography.x509.CRLDistributionPoints`
  * :class:`~cryptography.x509.InhibitAnyPolicy`
  * :class:`~cryptography.x509.IssuerAlternativeName`
  * :class:`~cryptography.x509.OCSPNoCheck`

* Add support for creating certificate signing requests with
  :class:`~cryptography.x509.CertificateSigningRequestBuilder`. This includes
  support for the same extensions supported in the ``CertificateBuilder``.
* Deprecate ``encode_rfc6979_signature`` and ``decode_rfc6979_signature`` in
  favor of
  :func:`~cryptography.hazmat.primitives.asymmetric.utils.encode_dss_signature`
  and
  :func:`~cryptography.hazmat.primitives.asymmetric.utils.decode_dss_signature`.


0.9.3 - 2015-07-09
~~~~~~~~~~~~~~~~~~

* Updated Windows wheels to be compiled against OpenSSL 1.0.2d.

0.9.2 - 2015-07-04
~~~~~~~~~~~~~~~~~~

* Updated Windows wheels to be compiled against OpenSSL 1.0.2c.

0.9.1 - 2015-06-06
~~~~~~~~~~~~~~~~~~

* **SECURITY ISSUE**: Fixed a double free in the OpenSSL backend when using DSA
  to verify signatures. Note that this only affects PyPy 2.6.0 and (presently
  unreleased) CFFI versions greater than 1.1.0.

0.9 - 2015-05-13
~~~~~~~~~~~~~~~~

* Removed support for Python 3.2. This version of Python is rarely used
  and caused support headaches. Users affected by this should upgrade to 3.3+.
* Deprecated support for Python 2.6. At the time there is no time table for
  actually dropping support, however we strongly encourage all users to upgrade
  their Python, as Python 2.6 no longer receives support from the Python core
  team.
* Add support for the
  :class:`~cryptography.hazmat.primitives.asymmetric.ec.SECP256K1` elliptic
  curve.
* Fixed compilation when using an OpenSSL which was compiled with the
  ``no-comp`` (``OPENSSL_NO_COMP``) option.
* Support :attr:`~cryptography.hazmat.primitives.serialization.Encoding.DER`
  serialization of public keys using the ``public_bytes`` method of
  :class:`~cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKeyWithSerialization`,
  :class:`~cryptography.hazmat.primitives.asymmetric.dsa.DSAPublicKeyWithSerialization`,
  and
  :class:`~cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePublicKeyWithSerialization`.
* Support :attr:`~cryptography.hazmat.primitives.serialization.Encoding.DER`
  serialization of private keys using the ``private_bytes`` method of
  :class:`~cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKeyWithSerialization`,
  :class:`~cryptography.hazmat.primitives.asymmetric.dsa.DSAPrivateKeyWithSerialization`,
  and
  :class:`~cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKeyWithSerialization`.
* Add support for parsing X.509 certificate signing requests (CSRs) with
  :func:`~cryptography.x509.load_pem_x509_csr` and
  :func:`~cryptography.x509.load_der_x509_csr`.
* Moved ``cryptography.exceptions.InvalidToken`` to
  :class:`cryptography.hazmat.primitives.twofactor.InvalidToken` and deprecated
  the old location. This was moved to minimize confusion between this exception
  and :class:`cryptography.fernet.InvalidToken`.
* Added support for X.509 extensions in :class:`~cryptography.x509.Certificate`
  objects. The following extensions are supported as of this release:

  * :class:`~cryptography.x509.BasicConstraints`
  * :class:`~cryptography.x509.AuthorityKeyIdentifier`
  * :class:`~cryptography.x509.SubjectKeyIdentifier`
  * :class:`~cryptography.x509.KeyUsage`
  * :class:`~cryptography.x509.SubjectAlternativeName`
  * :class:`~cryptography.x509.ExtendedKeyUsage`
  * :class:`~cryptography.x509.CRLDistributionPoints`
  * :class:`~cryptography.x509.AuthorityInformationAccess`
  * :class:`~cryptography.x509.CertificatePolicies`

  Note that unsupported extensions with the critical flag raise
  :class:`~cryptography.x509.UnsupportedExtension` while unsupported extensions
  set to non-critical are silently ignored. Read the
  :doc:`X.509 documentation</x509/index>` for more information.

0.8.2 - 2015-04-10
~~~~~~~~~~~~~~~~~~

* Fixed a race condition when initializing the OpenSSL or CommonCrypto backends
  in a multi-threaded scenario.

0.8.1 - 2015-03-20
~~~~~~~~~~~~~~~~~~

* Updated Windows wheels to be compiled against OpenSSL 1.0.2a.

0.8 - 2015-03-08
~~~~~~~~~~~~~~~~

* :func:`~cryptography.hazmat.primitives.serialization.load_ssh_public_key` can
  now load elliptic curve public keys.
* Added
  :attr:`~cryptography.x509.Certificate.signature_hash_algorithm` support to
  :class:`~cryptography.x509.Certificate`.
* Added
  :func:`~cryptography.hazmat.primitives.asymmetric.rsa.rsa_recover_prime_factors`
* :class:`~cryptography.hazmat.primitives.kdf.KeyDerivationFunction` was moved
  from :mod:`~cryptography.hazmat.primitives.interfaces` to
  :mod:`~cryptography.hazmat.primitives.kdf`.
* Added support for parsing X.509 names. See the
  :doc:`X.509 documentation</x509/index>` for more information.
* Added
  :func:`~cryptography.hazmat.primitives.serialization.load_der_private_key` to
  support loading of DER encoded private keys and
  :func:`~cryptography.hazmat.primitives.serialization.load_der_public_key` to
  support loading DER encoded public keys.
* Fixed building against LibreSSL, a compile-time substitute for OpenSSL.
* FreeBSD 9.2 was removed from the continuous integration system.
* Updated Windows wheels to be compiled against OpenSSL 1.0.2.
* :func:`~cryptography.hazmat.primitives.serialization.load_pem_public_key`
  and :func:`~cryptography.hazmat.primitives.serialization.load_der_public_key`
  now support PKCS1 RSA public keys (in addition to the previous support for
  SubjectPublicKeyInfo format for RSA, EC, and DSA).
* Added
  :class:`~cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKeyWithSerialization`
  and deprecated ``EllipticCurvePrivateKeyWithNumbers``.
* Added
  :meth:`~cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKeyWithSerialization.private_bytes`
  to
  :class:`~cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKeyWithSerialization`.
* Added
  :class:`~cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKeyWithSerialization`
  and deprecated ``RSAPrivateKeyWithNumbers``.
* Added
  :meth:`~cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKeyWithSerialization.private_bytes`
  to
  :class:`~cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKeyWithSerialization`.
* Added
  :class:`~cryptography.hazmat.primitives.asymmetric.dsa.DSAPrivateKeyWithSerialization`
  and deprecated ``DSAPrivateKeyWithNumbers``.
* Added
  :meth:`~cryptography.hazmat.primitives.asymmetric.dsa.DSAPrivateKeyWithSerialization.private_bytes`
  to
  :class:`~cryptography.hazmat.primitives.asymmetric.dsa.DSAPrivateKeyWithSerialization`.
* Added
  :class:`~cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKeyWithSerialization`
  and deprecated ``RSAPublicKeyWithNumbers``.
* Added ``public_bytes`` to
  :class:`~cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKeyWithSerialization`.
* Added
  :class:`~cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePublicKeyWithSerialization`
  and deprecated ``EllipticCurvePublicKeyWithNumbers``.
* Added ``public_bytes`` to
  :class:`~cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePublicKeyWithSerialization`.
* Added
  :class:`~cryptography.hazmat.primitives.asymmetric.dsa.DSAPublicKeyWithSerialization`
  and deprecated ``DSAPublicKeyWithNumbers``.
* Added ``public_bytes`` to
  :class:`~cryptography.hazmat.primitives.asymmetric.dsa.DSAPublicKeyWithSerialization`.
* :class:`~cryptography.hazmat.primitives.hashes.HashAlgorithm` and
  :class:`~cryptography.hazmat.primitives.hashes.HashContext` were moved from
  :mod:`~cryptography.hazmat.primitives.interfaces` to
  :mod:`~cryptography.hazmat.primitives.hashes`.
* :class:`~cryptography.hazmat.primitives.ciphers.CipherContext`,
  :class:`~cryptography.hazmat.primitives.ciphers.AEADCipherContext`,
  :class:`~cryptography.hazmat.primitives.ciphers.AEADEncryptionContext`,
  :class:`~cryptography.hazmat.primitives.ciphers.CipherAlgorithm`, and
  :class:`~cryptography.hazmat.primitives.ciphers.BlockCipherAlgorithm`
  were moved from :mod:`~cryptography.hazmat.primitives.interfaces` to
  :mod:`~cryptography.hazmat.primitives.ciphers`.
* :class:`~cryptography.hazmat.primitives.ciphers.modes.Mode`,
  :class:`~cryptography.hazmat.primitives.ciphers.modes.ModeWithInitializationVector`,
  :class:`~cryptography.hazmat.primitives.ciphers.modes.ModeWithNonce`, and
  :class:`~cryptography.hazmat.primitives.ciphers.modes.ModeWithAuthenticationTag`
  were moved from :mod:`~cryptography.hazmat.primitives.interfaces` to
  :mod:`~cryptography.hazmat.primitives.ciphers.modes`.
* :class:`~cryptography.hazmat.primitives.padding.PaddingContext` was moved
  from :mod:`~cryptography.hazmat.primitives.interfaces` to
  :mod:`~cryptography.hazmat.primitives.padding`.
*
  :class:`~cryptography.hazmat.primitives.asymmetric.padding.AsymmetricPadding`
  was moved from :mod:`~cryptography.hazmat.primitives.interfaces` to
  :mod:`~cryptography.hazmat.primitives.asymmetric.padding`.
*
  :class:`~cryptography.hazmat.primitives.asymmetric.AsymmetricSignatureContext`
  and
  :class:`~cryptography.hazmat.primitives.asymmetric.AsymmetricVerificationContext`
  were moved from :mod:`~cryptography.hazmat.primitives.interfaces` to
  :mod:`~cryptography.hazmat.primitives.asymmetric`.
* :class:`~cryptography.hazmat.primitives.asymmetric.dsa.DSAParameters`,
  :class:`~cryptography.hazmat.primitives.asymmetric.dsa.DSAParametersWithNumbers`,
  :class:`~cryptography.hazmat.primitives.asymmetric.dsa.DSAPrivateKey`,
  ``DSAPrivateKeyWithNumbers``,
  :class:`~cryptography.hazmat.primitives.asymmetric.dsa.DSAPublicKey` and
  ``DSAPublicKeyWithNumbers`` were moved from
  :mod:`~cryptography.hazmat.primitives.interfaces` to
  :mod:`~cryptography.hazmat.primitives.asymmetric.dsa`
* :class:`~cryptography.hazmat.primitives.asymmetric.ec.EllipticCurve`,
  :class:`~cryptography.hazmat.primitives.asymmetric.ec.EllipticCurveSignatureAlgorithm`,
  :class:`~cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKey`,
  ``EllipticCurvePrivateKeyWithNumbers``,
  :class:`~cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePublicKey`,
  and ``EllipticCurvePublicKeyWithNumbers``
  were moved from :mod:`~cryptography.hazmat.primitives.interfaces` to
  :mod:`~cryptography.hazmat.primitives.asymmetric.ec`.
* :class:`~cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey`,
  ``RSAPrivateKeyWithNumbers``,
  :class:`~cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey` and
  ``RSAPublicKeyWithNumbers`` were moved from
  :mod:`~cryptography.hazmat.primitives.interfaces` to
  :mod:`~cryptography.hazmat.primitives.asymmetric.rsa`.

0.7.2 - 2015-01-16
~~~~~~~~~~~~~~~~~~

* Updated Windows wheels to be compiled against OpenSSL 1.0.1l.
* ``enum34`` is no longer installed on Python 3.4, where it is included in
  the standard library.
* Added a new function to the OpenSSL bindings to support additional
  functionality in pyOpenSSL.

0.7.1 - 2014-12-28
~~~~~~~~~~~~~~~~~~

* Fixed an issue preventing compilation on platforms where ``OPENSSL_NO_SSL3``
  was defined.

0.7 - 2014-12-17
~~~~~~~~~~~~~~~~

* Cryptography has been relicensed from the Apache Software License, Version
  2.0, to being available under *either* the Apache Software License, Version
  2.0, or the BSD license.
* Added key-rotation support to :doc:`Fernet </fernet>` with
  :class:`~cryptography.fernet.MultiFernet`.
* More bit-lengths are now supported for ``p`` and ``q`` when loading DSA keys
  from numbers.
* Added :class:`~cryptography.hazmat.primitives.interfaces.MACContext` as a
  common interface for CMAC and HMAC and deprecated ``CMACContext``.
* Added support for encoding and decoding :rfc:`6979` signatures in
  :doc:`/hazmat/primitives/asymmetric/utils`.
* Added
  :func:`~cryptography.hazmat.primitives.serialization.load_ssh_public_key` to
  support the loading of OpenSSH public keys (:rfc:`4253`). Only RSA and DSA
  keys are currently supported.
* Added initial support for X.509 certificate parsing. See the
  :doc:`X.509 documentation</x509/index>` for more information.

0.6.1 - 2014-10-15
~~~~~~~~~~~~~~~~~~

* Updated Windows wheels to be compiled against OpenSSL 1.0.1j.
* Fixed an issue where OpenSSL 1.0.1j changed the errors returned by some
  functions.
* Added our license file to the ``cryptography-vectors`` package.
* Implemented DSA hash truncation support (per FIPS 186-3) in the OpenSSL
  backend. This works around an issue in 1.0.0, 1.0.0a, and 1.0.0b where
  truncation was not implemented.

0.6 - 2014-09-29
~~~~~~~~~~~~~~~~

* Added
  :func:`~cryptography.hazmat.primitives.serialization.load_pem_private_key` to
  ease loading private keys, and
  :func:`~cryptography.hazmat.primitives.serialization.load_pem_public_key` to
  support loading public keys.
* Removed the, deprecated in 0.4, support for the ``salt_length`` argument to
  the :class:`~cryptography.hazmat.primitives.asymmetric.padding.MGF1`
  constructor. The ``salt_length`` should be passed to
  :class:`~cryptography.hazmat.primitives.asymmetric.padding.PSS` instead.
* Fix compilation on OS X Yosemite.
* Deprecated ``elliptic_curve_private_key_from_numbers`` and
  ``elliptic_curve_public_key_from_numbers`` in favor of
  ``load_elliptic_curve_private_numbers`` and
  ``load_elliptic_curve_public_numbers`` on
  :class:`~cryptography.hazmat.backends.interfaces.EllipticCurveBackend`.
* Added ``EllipticCurvePrivateKeyWithNumbers`` and
  ``EllipticCurvePublicKeyWithNumbers`` support.
* Work around three GCM related bugs in CommonCrypto and OpenSSL.

  * On the CommonCrypto backend adding AAD but not subsequently calling update
    would return null tag bytes.

  * One the CommonCrypto backend a call to update without an empty add AAD call
    would return null ciphertext bytes.

  * On the OpenSSL backend with certain versions adding AAD only would give
    invalid tag bytes.

* Support loading EC private keys from PEM.

0.5.4 - 2014-08-20
~~~~~~~~~~~~~~~~~~

* Added several functions to the OpenSSL bindings to support new
  functionality in pyOpenSSL.
* Fixed a redefined constant causing compilation failure with Solaris 11.2.

0.5.3 - 2014-08-06
~~~~~~~~~~~~~~~~~~

* Updated Windows wheels to be compiled against OpenSSL 1.0.1i.

0.5.2 - 2014-07-09
~~~~~~~~~~~~~~~~~~

* Add ``TraditionalOpenSSLSerializationBackend`` support to
  :doc:`/hazmat/backends/multibackend`.
* Fix compilation error on OS X 10.8 (Mountain Lion).

0.5.1 - 2014-07-07
~~~~~~~~~~~~~~~~~~

* Add ``PKCS8SerializationBackend`` support to
  :doc:`/hazmat/backends/multibackend`.

0.5 - 2014-07-07
~~~~~~~~~~~~~~~~

* **BACKWARDS INCOMPATIBLE:**
  :class:`~cryptography.hazmat.primitives.ciphers.modes.GCM` no longer allows
  truncation of tags by default. Previous versions of ``cryptography`` allowed
  tags to be truncated by default, applications wishing to preserve this
  behavior (not recommended) can pass the ``min_tag_length`` argument.
* Windows builds now statically link OpenSSL by default. When installing a
  wheel on Windows you no longer need to install OpenSSL separately. Windows
  users can switch between static and dynamic linking with an environment
  variable. See :doc:`/installation` for more details.
* Added :class:`~cryptography.hazmat.primitives.kdf.hkdf.HKDFExpand`.
* Added :class:`~cryptography.hazmat.primitives.ciphers.modes.CFB8` support
  for :class:`~cryptography.hazmat.primitives.ciphers.algorithms.AES` and
  :class:`~cryptography.hazmat.primitives.ciphers.algorithms.TripleDES` on
  :doc:`/hazmat/backends/commoncrypto` and :doc:`/hazmat/backends/openssl`.
* Added ``AES`` :class:`~cryptography.hazmat.primitives.ciphers.modes.CTR`
  support to the OpenSSL backend when linked against 0.9.8.
* Added ``PKCS8SerializationBackend`` and
  ``TraditionalOpenSSLSerializationBackend`` support to the
  :doc:`/hazmat/backends/openssl`.
* Added :doc:`/hazmat/primitives/asymmetric/ec` and
  :class:`~cryptography.hazmat.backends.interfaces.EllipticCurveBackend`.
* Added :class:`~cryptography.hazmat.primitives.ciphers.modes.ECB` support
  for :class:`~cryptography.hazmat.primitives.ciphers.algorithms.TripleDES` on
  :doc:`/hazmat/backends/commoncrypto` and :doc:`/hazmat/backends/openssl`.
* Deprecated the concrete ``RSAPrivateKey`` class in favor of backend
  specific providers of the
  :class:`cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey`
  interface.
* Deprecated the concrete ``RSAPublicKey`` in favor of backend specific
  providers of the
  :class:`cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey`
  interface.
* Deprecated the concrete ``DSAPrivateKey`` class in favor of backend
  specific providers of the
  :class:`cryptography.hazmat.primitives.asymmetric.dsa.DSAPrivateKey`
  interface.
* Deprecated the concrete ``DSAPublicKey`` class in favor of backend specific
  providers of the
  :class:`cryptography.hazmat.primitives.asymmetric.dsa.DSAPublicKey`
  interface.
* Deprecated the concrete ``DSAParameters`` class in favor of backend specific
  providers of the
  :class:`cryptography.hazmat.primitives.asymmetric.dsa.DSAParameters`
  interface.
* Deprecated ``encrypt_rsa``, ``decrypt_rsa``, ``create_rsa_signature_ctx`` and
  ``create_rsa_verification_ctx`` on
  :class:`~cryptography.hazmat.backends.interfaces.RSABackend`.
* Deprecated ``create_dsa_signature_ctx`` and ``create_dsa_verification_ctx``
  on :class:`~cryptography.hazmat.backends.interfaces.DSABackend`.

0.4 - 2014-05-03
~~~~~~~~~~~~~~~~

* Deprecated ``salt_length`` on
  :class:`~cryptography.hazmat.primitives.asymmetric.padding.MGF1` and added it
  to :class:`~cryptography.hazmat.primitives.asymmetric.padding.PSS`. It will
  be removed from ``MGF1`` in two releases per our :doc:`/api-stability`
  policy.
* Added :class:`~cryptography.hazmat.primitives.ciphers.algorithms.SEED`
  support.
* Added :class:`~cryptography.hazmat.primitives.cmac.CMAC`.
* Added decryption support to
  :class:`~cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey`
  and encryption support to
  :class:`~cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey`.
* Added signature support to
  :class:`~cryptography.hazmat.primitives.asymmetric.dsa.DSAPrivateKey`
  and verification support to
  :class:`~cryptography.hazmat.primitives.asymmetric.dsa.DSAPublicKey`.

0.3 - 2014-03-27
~~~~~~~~~~~~~~~~

* Added :class:`~cryptography.hazmat.primitives.twofactor.hotp.HOTP`.
* Added :class:`~cryptography.hazmat.primitives.twofactor.totp.TOTP`.
* Added :class:`~cryptography.hazmat.primitives.ciphers.algorithms.IDEA`
  support.
* Added signature support to
  :class:`~cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey`
  and verification support to
  :class:`~cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey`.
* Moved test vectors to the new ``cryptography_vectors`` package.

0.2.2 - 2014-03-03
~~~~~~~~~~~~~~~~~~

* Removed a constant definition that was causing compilation problems with
  specific versions of OpenSSL.

0.2.1 - 2014-02-22
~~~~~~~~~~~~~~~~~~

* Fix a bug where importing cryptography from multiple paths could cause
  initialization to fail.

0.2 - 2014-02-20
~~~~~~~~~~~~~~~~

* Added :doc:`/hazmat/backends/commoncrypto`.
* Added initial :doc:`/hazmat/bindings/commoncrypto`.
* Removed ``register_cipher_adapter`` method from
  :class:`~cryptography.hazmat.backends.interfaces.CipherBackend`.
* Added support for the OpenSSL backend under Windows.
* Improved thread-safety for the OpenSSL backend.
* Fixed compilation on systems where OpenSSL's ``ec.h`` header is not
  available, such as CentOS.
* Added :class:`~cryptography.hazmat.primitives.kdf.pbkdf2.PBKDF2HMAC`.
* Added :class:`~cryptography.hazmat.primitives.kdf.hkdf.HKDF`.
* Added :doc:`/hazmat/backends/multibackend`.
* Set default random for the :doc:`/hazmat/backends/openssl` to the OS
  random engine.
* Added :class:`~cryptography.hazmat.primitives.ciphers.algorithms.CAST5`
  (CAST-128) support.

0.1 - 2014-01-08
~~~~~~~~~~~~~~~~

* Initial release.

.. _`master`: https://github.com/pyca/cryptography/
.. _`cffi`: https://cffi.readthedocs.org/en/latest/

Changelog
=========

Versions are year-based with a strict backward-compatibility policy.
The third digit is only for regressions.

17.5.0 (2017-11-30)
-------------------


Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* The minimum ``cryptography`` version is now 2.1.4.


Deprecations:
^^^^^^^^^^^^^

*none*


Changes:
^^^^^^^^

- Fixed a potential use-after-free in the verify callback and resolved a memory leak when loading PKCS12 files with ``cacerts``.
  `#723 <https://github.com/pyca/pyopenssl/pull/723>`_
- Added ``Connection.export_keying_material`` for RFC 5705 compatible export of keying material.
  `#725 <https://github.com/pyca/pyopenssl/pull/725>`_

----



17.4.0 (2017-11-21)
-------------------


Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*none*


Deprecations:
^^^^^^^^^^^^^

*none*


Changes:
^^^^^^^^


- Re-added a subset of the ``OpenSSL.rand`` module.
  This subset allows conscientious users to reseed the OpenSSL CSPRNG after fork.
  `#708 <https://github.com/pyca/pyopenssl/pull/708>`_
- Corrected a use-after-free when reusing an issuer or subject from an ``X509`` object after the underlying object has been mutated.
  `#709 <https://github.com/pyca/pyopenssl/pull/709>`_

----


17.3.0 (2017-09-14)
-------------------


Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Dropped support for Python 3.3.
  `#677 <https://github.com/pyca/pyopenssl/pull/677>`_
- Removed the deprecated ``OpenSSL.rand`` module.
  This is being done ahead of our normal deprecation schedule due to its lack of use and the fact that it was becoming a maintenance burden.
  ``os.urandom()`` should be used instead.
  `#675 <https://github.com/pyca/pyopenssl/pull/675>`_


Deprecations:
^^^^^^^^^^^^^

- Deprecated ``OpenSSL.tsafe``.
  `#673 <https://github.com/pyca/pyopenssl/pull/673>`_

Changes:
^^^^^^^^

- Fixed a memory leak in ``OpenSSL.crypto.CRL``.
  `#690 <https://github.com/pyca/pyopenssl/pull/690>`_
- Fixed a memory leak when verifying certificates with ``OpenSSL.crypto.X509StoreContext``.
  `#691 <https://github.com/pyca/pyopenssl/pull/691>`_


----


17.2.0 (2017-07-20)
-------------------


Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*none*


Deprecations:
^^^^^^^^^^^^^

- Deprecated ``OpenSSL.rand`` - callers should use ``os.urandom()`` instead.
  `#658 <https://github.com/pyca/pyopenssl/pull/658>`_


Changes:
^^^^^^^^

- Fixed a bug causing ``Context.set_default_verify_paths()`` to not work with cryptography ``manylinux1`` wheels on Python 3.x.
  `#665 <https://github.com/pyca/pyopenssl/pull/665>`_
- Fixed a crash with (EC)DSA signatures in some cases.
  `#670 <https://github.com/pyca/pyopenssl/pull/670>`_


----


17.1.0 (2017-06-30)
-------------------


Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Removed the deprecated ``OpenSSL.rand.egd()`` function.
  Applications should prefer ``os.urandom()`` for random number generation.
  `#630 <https://github.com/pyca/pyopenssl/pull/630>`_
- Removed the deprecated default ``digest`` argument to ``OpenSSL.crypto.CRL.export()``.
  Callers must now always pass an explicit ``digest``.
  `#652 <https://github.com/pyca/pyopenssl/pull/652>`_
- Fixed a bug with ``ASN1_TIME`` casting in ``X509.set_notBefore()``,
  ``X509.set_notAfter()``, ``Revoked.set_rev_date()``, ``Revoked.set_nextUpdate()``,
  and ``Revoked.set_lastUpdate()``. You must now pass times in the form
  ``YYYYMMDDhhmmssZ``. ``YYYYMMDDhhmmss+hhmm`` and ``YYYYMMDDhhmmss-hhmm``
  will no longer work. `#612 <https://github.com/pyca/pyopenssl/pull/612>`_


Deprecations:
^^^^^^^^^^^^^


- Deprecated the legacy "Type" aliases: ``ContextType``, ``ConnectionType``, ``PKeyType``, ``X509NameType``, ``X509ExtensionType``, ``X509ReqType``, ``X509Type``, ``X509StoreType``, ``CRLType``, ``PKCS7Type``, ``PKCS12Type``, ``NetscapeSPKIType``.
  The names without the "Type"-suffix should be used instead.


Changes:
^^^^^^^^

- Added ``OpenSSL.crypto.X509.from_cryptography()`` and ``OpenSSL.crypto.X509.to_cryptography()`` for converting X.509 certificate to and from pyca/cryptography objects.
  `#640 <https://github.com/pyca/pyopenssl/pull/640>`_
- Added ``OpenSSL.crypto.X509Req.from_cryptography()``, ``OpenSSL.crypto.X509Req.to_cryptography()``, ``OpenSSL.crypto.CRL.from_cryptography()``, and ``OpenSSL.crypto.CRL.to_cryptography()`` for converting X.509 CSRs and CRLs to and from pyca/cryptography objects.
  `#645 <https://github.com/pyca/pyopenssl/pull/645>`_
- Added ``OpenSSL.debug`` that allows to get an overview of used library versions (including linked OpenSSL) and other useful runtime information using ``python -m OpenSSL.debug``.
  `#620 <https://github.com/pyca/pyopenssl/pull/620>`_
- Added a fallback path to ``Context.set_default_verify_paths()`` to accommodate the upcoming release of ``cryptography`` ``manylinux1`` wheels.
  `#633 <https://github.com/pyca/pyopenssl/pull/633>`_


----


17.0.0 (2017-04-20)
-------------------

Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*none*


Deprecations:
^^^^^^^^^^^^^

*none*


Changes:
^^^^^^^^

- Added ``OpenSSL.X509Store.set_time()`` to set a custom verification time when verifying certificate chains.
  `#567 <https://github.com/pyca/pyopenssl/pull/567>`_
- Added a collection of functions for working with OCSP stapling.
  None of these functions make it possible to validate OCSP assertions, only to staple them into the handshake and to retrieve the stapled assertion if provided.
  Users will need to write their own code to handle OCSP assertions.
  We specifically added: ``Context.set_ocsp_server_callback()``, ``Context.set_ocsp_client_callback()``, and ``Connection.request_ocsp()``.
  `#580 <https://github.com/pyca/pyopenssl/pull/580>`_
- Changed the ``SSL`` module's memory allocation policy to avoid zeroing memory it allocates when unnecessary.
  This reduces CPU usage and memory allocation time by an amount proportional to the size of the allocation.
  For applications that process a lot of TLS data or that use very lage allocations this can provide considerable performance improvements.
  `#578 <https://github.com/pyca/pyopenssl/pull/578>`_
- Automatically set ``SSL_CTX_set_ecdh_auto()`` on ``OpenSSL.SSL.Context``.
  `#575 <https://github.com/pyca/pyopenssl/pull/575>`_
- Fix empty exceptions from ``OpenSSL.crypto.load_privatekey()``.
  `#581 <https://github.com/pyca/pyopenssl/pull/581>`_


----


16.2.0 (2016-10-15)
-------------------

Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*none*


Deprecations:
^^^^^^^^^^^^^

*none*


Changes:
^^^^^^^^

- Fixed compatibility errors with OpenSSL 1.1.0.
- Fixed an issue that caused failures with subinterpreters and embedded Pythons.
  `#552 <https://github.com/pyca/pyopenssl/pull/552>`_


----


16.1.0 (2016-08-26)
-------------------

Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*none*


Deprecations:
^^^^^^^^^^^^^

- Dropped support for OpenSSL 0.9.8.


Changes:
^^^^^^^^

- Fix memory leak in ``OpenSSL.crypto.dump_privatekey()`` with ``FILETYPE_TEXT``.
  `#496 <https://github.com/pyca/pyopenssl/pull/496>`_
- Enable use of CRL (and more) in verify context.
  `#483 <https://github.com/pyca/pyopenssl/pull/483>`_
- ``OpenSSL.crypto.PKey`` can now be constructed from ``cryptography`` objects and also exported as such.
  `#439 <https://github.com/pyca/pyopenssl/pull/439>`_
- Support newer versions of ``cryptography`` which use opaque structs for OpenSSL 1.1.0 compatibility.


----


16.0.0 (2016-03-19)
-------------------

This is the first release under full stewardship of PyCA.
We have made *many* changes to make local development more pleasing.
The test suite now passes both on Linux and OS X with OpenSSL 0.9.8, 1.0.1, and 1.0.2.
It has been moved to `pytest <https://docs.pytest.org/>`_, all CI test runs are part of `tox <https://tox.readthedocs.io/>`_ and the source code has been made fully `flake8 <https://flake8.readthedocs.io/>`_ compliant.

We hope to have lowered the barrier for contributions significantly but are open to hear about any remaining frustrations.


Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Python 3.2 support has been dropped.
  It never had significant real world usage and has been dropped by our main dependency ``cryptography``.
  Affected users should upgrade to Python 3.3 or later.


Deprecations:
^^^^^^^^^^^^^

- The support for EGD has been removed.
  The only affected function ``OpenSSL.rand.egd()`` now uses ``os.urandom()`` to seed the internal PRNG instead.
  Please see `pyca/cryptography#1636 <https://github.com/pyca/cryptography/pull/1636>`_ for more background information on this decision.
  In accordance with our backward compatibility policy ``OpenSSL.rand.egd()`` will be *removed* no sooner than a year from the release of 16.0.0.

  Please note that you should `use urandom <https://sockpuppet.org/blog/2014/02/25/safely-generate-random-numbers/>`_ for all your secure random number needs.
- Python 2.6 support has been deprecated.
  Our main dependency ``cryptography`` deprecated 2.6 in version 0.9 (2015-05-14) with no time table for actually dropping it.
  pyOpenSSL will drop Python 2.6 support once ``cryptography`` does.


Changes:
^^^^^^^^

- Fixed ``OpenSSL.SSL.Context.set_session_id``, ``OpenSSL.SSL.Connection.renegotiate``, ``OpenSSL.SSL.Connection.renegotiate_pending``, and ``OpenSSL.SSL.Context.load_client_ca``.
  They were lacking an implementation since 0.14.
  `#422 <https://github.com/pyca/pyopenssl/pull/422>`_
- Fixed segmentation fault when using keys larger than 4096-bit to sign data.
  `#428 <https://github.com/pyca/pyopenssl/pull/428>`_
- Fixed ``AttributeError`` when ``OpenSSL.SSL.Connection.get_app_data()`` was called before setting any app data.
  `#304 <https://github.com/pyca/pyopenssl/pull/304>`_
- Added ``OpenSSL.crypto.dump_publickey()`` to dump ``OpenSSL.crypto.PKey`` objects that represent public keys, and ``OpenSSL.crypto.load_publickey()`` to load such objects from serialized representations.
  `#382 <https://github.com/pyca/pyopenssl/pull/382>`_
- Added ``OpenSSL.crypto.dump_crl()`` to dump a certificate revocation list out to a string buffer.
  `#368 <https://github.com/pyca/pyopenssl/pull/368>`_
- Added ``OpenSSL.SSL.Connection.get_state_string()`` using the OpenSSL binding ``state_string_long``.
  `#358 <https://github.com/pyca/pyopenssl/pull/358>`_
- Added support for the ``socket.MSG_PEEK`` flag to ``OpenSSL.SSL.Connection.recv()`` and ``OpenSSL.SSL.Connection.recv_into()``.
  `#294 <https://github.com/pyca/pyopenssl/pull/294>`_
- Added ``OpenSSL.SSL.Connection.get_protocol_version()`` and ``OpenSSL.SSL.Connection.get_protocol_version_name()``.
  `#244 <https://github.com/pyca/pyopenssl/pull/244>`_
- Switched to ``utf8string`` mask by default.
  OpenSSL formerly defaulted to a ``T61String`` if there were UTF-8 characters present.
  This was changed to default to ``UTF8String`` in the config around 2005, but the actual code didn't change it until late last year.
  This will default us to the setting that actually works.
  To revert this you can call ``OpenSSL.crypto._lib.ASN1_STRING_set_default_mask_asc(b"default")``.
  `#234 <https://github.com/pyca/pyopenssl/pull/234>`_


----


Older Changelog Entries
-----------------------

The changes from before release 16.0.0 are preserved in the `repository <https://github.com/pyca/pyopenssl/blob/master/doc/ChangeLog_old.txt>`_.

History
=======

0.12.0: 2017-12-20
------------------------

- Add support for channel binding tokens (assumes pykerberos support >= 1.2.1)
- Add support for kerberos message encryption (assumes pykerberos support >= 1.2.1)
- Misc CI/test fixes

0.11.0: 2016-11-02
------------------

- Switch dependency on Windows from kerberos-sspi/pywin32 to WinKerberos.
  This brings Custom Principal support to Windows users.

0.10.0: 2016-05-18
------------------

- Make it possible to receive errors without having their contents and headers
  stripped.
- Resolve a bug caused by passing the ``principal`` keyword argument to
  kerberos-sspi on Windows.

0.9.0: 2016-05-06
-----------------

- Support for principal, hostname, and realm override.

- Added support for mutual auth.

0.8.0: 2016-01-07
-----------------

- Support for Kerberos delegation.

- Fixed problems declaring kerberos-sspi on Windows installs.

0.7.0: 2015-05-04
-----------------

- Added Windows native authentication support by adding kerberos-sspi as an
  alternative backend.

- Prevent infinite recursion when a server returns 401 to an authorization
  attempt.

- Reduce the logging during successful responses.

0.6.1: 2014-11-14
-----------------

- Fix HTTPKerberosAuth not to treat non-file as a file

- Prevent infinite recursion when GSSErrors occurs

0.6: 2014-11-04
---------------

- Handle mutual authentication (see pull request 36_)

  All users should upgrade immediately. This has been reported to
  oss-security_ and we are awaiting a proper CVE identifier.

  **Update**: We were issued CVE-2014-8650

- Distribute as a wheel.

.. _36: https://github.com/requests/requests-kerberos/pull/36
.. _oss-security: http://www.openwall.com/lists/oss-security/

0.5: 2014-05-14
---------------

- Allow non-HTTP service principals with HTTPKerberosAuth using a new optional
  argument ``service``.

- Fix bug in ``setup.py`` on distributions where the ``compiler`` module is
  not available.

- Add test dependencies to ``setup.py`` so ``python setup.py test`` will work.

0.4: 2013-10-26
---------------

- Minor updates in the README
- Change requirements to depend on requests above 1.1.0

0.3: 2013-06-02
---------------

- Work with servers operating on non-standard ports

0.2: 2013-03-26
---------------

- Not documented

0.1: Never released
-------------------

- Initial Release

History
=======

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

python-ldap FAQ
===============

Project
-------

**Q**: Is python-ldap yet another abandon-ware project?

  **A1**: “Jump on in.”

  **A2**: “Jump into the C ;-)”

  **A3**: see file CHANGES in source distribution
  or `repository`_.

.. _repository: https://github.com/python-ldap/python-ldap/blob/master/CHANGES


Usage
-----

**Q**: Does it work with Python 3?

  **A0**: Yes, from 3.0 on.

  **A1**. For earlier versions, there's `pyldap`_, an independent fork
  now merged into python-ldap.

.. _pyldap: https://pypi.org/project/pyldap/


**Q**: Does it work with Python 2.6? (1.5|2.0|2.1|2.2|2.3|2.4|2.5)?

  **A**: No. Old versions of python-ldap are still available from PyPI, though.


**Q**: My code imports module ``_ldap``.
That used to work, but after an upgrade it does not work anymore. Why?

   **A**: Despite some outdated programming examples, the extension module
    ``_ldap`` **MUST NOT** be imported directly, unless you really know what
    you're doing (e.g. for internal regression testing).

    Import ``ldap`` instead, which is a Python wrapper around ``_ldap``
    providing the full functionality.

**Q**: My script bound to MS Active Directory but a a search operation results
in the exception :exc:`ldap.OPERATIONS_ERROR` with the diagnostic messages text
“In order to perform this operation a successful bind must be
completed on the connection.”
What's happening here?

    **A**: When searching from the domain level, MS AD returns referrals (search continuations)
    for some objects to indicate to the client where to look for these objects.
    Client-chasing of referrals is a broken concept, since LDAPv3 does not specify
    which credentials to use when chasing the referral. Windows clients are supposed
    to simply use their Windows credentials, but this does not work in general when
    chasing referrals received from and pointing to arbitrary LDAP servers.

    Therefore, per default, ``libldap`` automatically chases the referrals
    internally with an *anonymous* access which fails with MS AD.

    So, the best thing to do is to switch this behaviour off::

      l = ldap.initialize('ldap://foobar')
      l.set_option(ldap.OPT_REFERRALS,0)

**Q**: Why am I seeing a ``ldap.SUCCESS`` traceback as output?

    **A**: Most likely, you are using one of the non-synchronous calls, and probably
    mean to be using a synchronous call
    (see detailed explanation in :ref:`sending-ldap-requests`).

**Q**: Can I use LDAPv2 via python-ldap?

    **A**: Yes, by explicitly setting the class attribute
    :attr:`~ldap.LDAPObject.protocol_version`.

    You should not do that nowadays since
    `LDAPv2 is considered historic <https://tools.ietf.org/html/rfc3494>`_
    since many years.



Installing
----------

**Q**: Does it work with Windows 32?

    **A**: Yes. You can find links to unofficial pre-compiled packages
    for Windows on the :ref:`installing` page.


**Q**: Can python-ldap be built against OpenLDAP 2.3 libs or older?

    **A**: No.
    The needed minimal version of OpenLDAP is documented in :ref:`build prerequisites`.
    Patched builds of python-ldap linked to older libs are not supported by the
    python-ldap project.


**Q**: During build there are warning messages displayed
telling Lib/ldap.py and Lib/ldap/schema.py are not found::

      warning: build_py: file Lib/ldap.py (for module ldap) not found
      warning: build_py: file Lib/ldap/schema.py (for module ldap.schema) not found

..

    **A**: ``ldap`` and ``ldap.schema`` are both module packages
    (directories containing various sub-modules).
    The messages above are falsely produced by DistUtils.
    Don't worry about it.

.. _install-macosx:

**Q**: What's the correct way to install on macOS?

  **A**::

      xcode-select --install
      pip install python-ldap \
         --global-option=build_ext \
         --global-option="-I$(xcrun --show-sdk-path)/usr/include/sasl"


**Q**: While importing module ``ldap``, some shared lib files are not found.
The error message looks similar to this::

      ImportError: ld.so.1: /usr/local/bin/python: fatal: liblber.so.2: open failed: No such file or directory

..

    **A1**: You need to make sure that the path to ``liblber.so.2`` and
    ``libldap.so.2`` is in your ``LD_LIBRARY_PATH`` environment variable.

    **A2**: Alternatively, if you're on Linux, you can add the path to
    ``liblber.so.2`` and ``libldap.so.2`` to ``/etc/ld.so.conf``
    and invoke the command ``ldconfig`` afterwards.



Historic
--------

**Q**: Can python-ldap 2.x be built against Netscape, Mozilla or Novell libs?

  **A**: Nope.


**Q**: My binary version of python-ldap was build with LDAP libs 3.3.
But the python-ldap docs say LDAP libs 2.x are needed. I'm confused!

  Short answer:
      See answer above and the :ref:`installing` page for
      a more recent version.

  Long answer:
      E.g. some Win32 DLLs floating around for download are based on
      the old Umich LDAP code which is not maintained anymore for
      *many* years! Last Umich 3.3 release was 1997 if I remember correctly.

      The OpenLDAP project took over the Umich code and started releasing
      OpenLDAP 1.x series mainly fixing bugs and doing some improvements
      to the database backend. Still, only LDAPv2 was supported at server
      and client side. (Many commercial vendors also derived their products
      from the Umich code.)

      OpenLDAP 2.x is a full-fledged LDAPv3 implementation. It has
      its roots in Umich code but has many more features/improvements.


**Q**: While importing module ``ldap``, there are undefined references reported.
The error message looks similar to this::

    ImportError: /usr/local/lib/libldap.so.2: undefined symbol: res_query

..

    **A**: Especially on older Linux systems, you might have to explicitly link
    against ``libresolv``.

    Tweak ``setup.cfg`` to contain this line::

        libs = lber ldap resolv

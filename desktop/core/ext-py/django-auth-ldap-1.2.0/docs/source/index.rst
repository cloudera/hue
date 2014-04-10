================================
Django Authentication Using LDAP
================================

This is a Django authentication backend that authenticates against an LDAP
service. Configuration can be as simple as a single distinguished name template,
but there are many rich configuration options for working with users, groups,
and permissions.

This version is officially supported on Python >= 2.6 and < 3, Django >= 1.3,
and python-ldap >= 2.0. It is known to work on earlier versions (especially of
Django) and backwards-compatibility is not broken needlessly, however users of
older dependencies are urged to test their deployments carefully and be wary of
updates.

Support for Python >= 3.3 is considered experimental at this time. Since
python-ldap doesn't support Python 3 yet, you have to install a fork::

    $ pip install git+https://github.com/rbarrois/python-ldap.git@py3

.. toctree::
    :maxdepth: 2

    install
    authentication
    groups
    users
    permissions
    multiconfig
    logging
    performance
    example
    reference
    changes


Older Versions
==============

- `django-auth-ldap 1.0.19 <_static/versions/1.0.19/index.html>`_


License
=======

.. include:: ../../LICENSE

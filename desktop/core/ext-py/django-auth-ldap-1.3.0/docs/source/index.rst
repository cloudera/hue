================================
Django Authentication Using LDAP
================================

This is a Django authentication backend that authenticates against an LDAP
service. Configuration can be as simple as a single distinguished name template,
but there are many rich configuration options for working with users, groups,
and permissions.

* Repository: https://bitbucket.org/illocution/django-auth-ldap
* Documentation: https://django-auth-ldap.readthedocs.io/
* Mailing list: https://groups.google.com/group/django-auth-ldap

This version is supported on Python 2.7 and 3.4+; and Django 1.8 and 1.10+.
Under Python 2, it requires `python-ldap
<https://pypi.python.org/pypi/python-ldap>`_ >= 2.0; under Python 3, it uses
`pyldap <https://pypi.python.org/pypi/pyldap>`_.

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


License
=======

.. include:: ../../LICENSE

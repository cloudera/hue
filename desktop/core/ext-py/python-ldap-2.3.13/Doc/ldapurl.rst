.. % $Id: ldapurl.rst,v 1.5 2010/02/05 13:13:19 stroeder Exp $

################################
:mod:`ldapurl` LDAP URL handling
################################

.. module:: ldapurl
   :synopsis: Parses and generates LDAP URLs
.. moduleauthor:: python-ldap project (see http://www.python-ldap.org/)


This module parses and generates LDAP URLs.    It is implemented in pure Python
and does not rely on any  non-standard modules. Therefore it can be used stand-
alone without  the rest of the python-ldap package.    Compability note: This
module has been solely tested on Python 2.x and above.

.. seealso::

   :rfc:`4516` - The LDAP URL Format


The :mod:`ldapurl` module exports the following constants:

.. data:: SEARCH_SCOPE

   This dictionary maps a search scope string identifier  to the corresponding
   integer value used with search operations  in :mod:`ldap`.


.. data:: SEARCH_SCOPE_STR

   This dictionary is the inverse to :const:`SEARCH_SCOPE`. It  maps a search scope
   integer value to the corresponding string identifier  used in a LDAP URL string
   representation.


.. data:: LDAP_SCOPE_BASE


.. data:: LDAP_SCOPE_ONELEVEL


.. data:: LDAP_SCOPE_SUBTREE



.. _ldapurl-ldapurl:

LDAPUrl Objects
^^^^^^^^^^^^^^^^

A :class:`LDAPUrl` object represents a complete LDAP URL.

All class methods:

Class attributes:

Instance attributes:

.. Here the actual docstring could be used provided it is fixed according rst rules
.. autoclass:: ldapurl.LDAPUrl 


.. _ldapurl-ldapurlextension:

LDAPUrlExtension Objects
^^^^^^^^^^^^^^^^^^^^^^^^

A :class:`LDAPUrlExtension` object represents a single LDAP URL extension.

All class methods:

Class attributes:

Instance attributes:

.. Here the actual docstring could be used provided it is fixed according rst rules
.. autoclass:: ldapurl.LDAPUrlExtension


.. _ldapurl-example:

Example
^^^^^^^^

Important security advice:
For security reasons you shouldn't specify passwords in LDAP URLs
unless you really know what you are doing.

The following example demonstrates how to parse a LDAP URL
with :mod:`ldapurl` module.


>>> import ldapurl
>>> ldap_url = ldapurl.LDAPUrl('ldap://localhost:1389/dc=stroeder,dc=com?cn,mail???bindname=cn=Michael%2cdc=stroeder%2cdc=com,X-BINDPW=secret')
>>> # Using the parsed LDAP URL by reading the class attributes
>>> ldap_url.dn
'dc=stroeder,dc=com'
>>> ldap_url.hostport
'localhost:1389'
>>> ldap_url.attrs
['cn','mail']
>>> ldap_url.filterstr
'(objectclass=*)'
>>> ldap_url.who
'cn=Michael,dc=stroeder,dc=com'
>>> ldap_url.cred
'secret'
>>> ldap_url.scope
0


The following example demonstrates how to generate a LDAP URL
with \module{ldapurl} module.

>>> import ldapurl
>>> ldap_url = ldapurl.LDAPUrl(hostport='localhost:1389',dn='dc=stroeder,dc=com',attrs=['cn','mail'],who='cn=Michael,dc=stroeder,dc=com',cred='secret')
>>> ldap_url.unparse()
'ldap://localhost:1389/dc=stroeder,dc=com?cn,mail?base?(objectclass=*)?bindname=cn=Michael%2Cdc=stroeder%2Cdc=com,X-BINDPW=secret'


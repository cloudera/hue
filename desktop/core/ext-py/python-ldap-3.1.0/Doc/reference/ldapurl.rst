###################################
:py:mod:`ldapurl` LDAP URL handling
###################################

.. py:module:: ldapurl
   :synopsis: Parses and generates LDAP URLs
.. moduleauthor:: python-ldap project (see https://www.python-ldap.org/)


This module parses and generates LDAP URLs.    It is implemented in pure Python
and does not rely on any  non-standard modules. Therefore it can be used stand-
alone without  the rest of the python-ldap package.  Compatibility note: This
module has been solely tested on Python 2.x and above.

.. seealso::

   :rfc:`4516` - The LDAP URL Format


Constants
=========

The :mod:`ldapurl` module exports the following constants:

.. py:data:: SEARCH_SCOPE

   This dictionary maps a search scope string identifier  to the corresponding
   integer value used with search operations  in :mod:`ldap`.


.. py:data:: SEARCH_SCOPE_STR

   This dictionary is the inverse to :const:`SEARCH_SCOPE`. It  maps a search scope
   integer value to the corresponding string identifier  used in a LDAP URL string
   representation.


.. py:data:: LDAP_SCOPE_BASE


.. py:data:: LDAP_SCOPE_ONELEVEL


.. py:data:: LDAP_SCOPE_SUBTREE


Functions
=========

.. autofunction:: ldapurl.isLDAPUrl


.. autofunction:: ldapurl.ldapUrlEscape


Classes
=======

.. _ldapurl-ldapurl:

LDAP URLs
^^^^^^^^^

A :py:class:`LDAPUrl` object represents a complete LDAP URL.

.. autoclass:: ldapurl.LDAPUrl
   :members:


LDAP URL extensions
^^^^^^^^^^^^^^^^^^^

A :py:class:`LDAPUrlExtension` object represents a single LDAP URL extension
whereas :py:class:`LDAPUrlExtensions` represents a list of LDAP URL extensions.


.. _ldapurl-ldapurlextension:

.. autoclass:: ldapurl.LDAPUrlExtension
   :members:

.. _ldapurl-ldapurlextensions:

.. autoclass:: ldapurl.LDAPUrlExtensions
   :members:


.. _ldapurl-example:

Example
^^^^^^^

Important security advice:
For security reasons you should not specify passwords in LDAP URLs
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

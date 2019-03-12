:py:mod:`ldap.dn` LDAP Distinguished Name handling
====================================================

.. py:module:: ldap.dn
   :synopsis: LDAP Distinguished Name handling.
.. moduleauthor:: python-ldap project (see https://www.python-ldap.org/)


.. % Author of the module code;


.. seealso::

   For LDAPv3 DN syntax see:

   :rfc:`4514` - Lightweight Directory Access Protocol (LDAP): String Representation of Distinguished Names

.. seealso::

   For deprecated LDAPv2 DN syntax (obsoleted by LDAPv3) see:

   :rfc:`1779` - A String Representation of Distinguished Names

The :mod:`ldap.dn` module defines the following functions:


.. function:: escape_dn_chars(s) -> string

   This function escapes characters in string *s* which  are special in LDAP
   distinguished names. You should use  this function when building LDAP DN strings
   from arbitrary input.


.. function:: str2dn(s [, flags=0]) -> list

   This function takes *s* and breaks it up into its component parts  down to AVA
   level. The optional parameter *flags* describes the DN format of s  (see
   :ref:`ldap-dn-flags`). Note that hex-encoded non-ASCII chars are decoded
   to the raw bytes.

   Internally this function is implemented by calling OpenLDAP C function
   `ldap_str2dn(3) <https://www.openldap.org/software/man.cgi?query=ldap_str2dn&sektion=3>`_.


.. function:: dn2str(dn) -> string

   This function takes a decomposed DN in *dn* and returns  a single string. It's
   the inverse to :func:`str2dn`.  Special characters are escaped with the help of
   function :func:`escape_dn_chars`.


.. function:: explode_dn(dn [, notypes=False[, flags=0]]) -> list

   This function takes *dn* and breaks it up into its component parts.   Each part
   is known as an RDN (Relative Distinguished Name). The optional  *notypes*
   parameter is used to specify that only the RDN values be   returned and not
   their types. The optional parameter *flags*  describes the DN format of s (see
   :ref:`ldap-dn-flags`). This function is emulated by function
   :func:`str2dn`  since the function ldap_explode_dn() in the C library is
   deprecated.


.. function:: explode_rdn(rdn [, notypes=False[, flags=0]]) -> list

   This function takes a (multi-valued) *rdn* and breaks it up  into a list of
   characteristic attributes. The optional  *notypes* parameter is used to specify
   that only the RDN values be   returned and not their types. The optional *flags*
   parameter  describes the DN format of s (see :ref:`ldap-dn-flags`).    This
   function is emulated by function :func:`str2dn`  since the function
   ldap_explode_rdn() in the C library is deprecated.


.. function:: is_dn(dn[, flags=0]) -> boolean

   This function checks whether *dn* is a valid LDAP distinguished name by
   passing it to function :func:`str2dn`.


.. _ldap-dn-example:

Examples
^^^^^^^^^

Splitting a LDAPv3 DN to AVA level. Note that both examples have the same result
but in the first example the non-ASCII chars are passed as is (byte buffer string)
whereas in the second example the hex-encoded DN representation are passed to the function.

>>> ldap.dn.str2dn('cn=Michael Str\xc3\xb6der,dc=example,dc=com',flags=ldap.DN_FORMAT_LDAPV3)
[[('cn', 'Michael Str\xc3\xb6der', 4)], [('dc', 'example', 1)], [('dc', 'com', 1)]]
>>> ldap.dn.str2dn('cn=Michael Str\C3\B6der,dc=example,dc=com',flags=ldap.DN_FORMAT_LDAPV3)
[[('cn', 'Michael Str\xc3\xb6der', 4)], [('dc', 'example', 1)], [('dc', 'com', 1)]]


Splitting a LDAPv2 DN into RDN parts:

>>> ldap.dn.explode_dn('cn=John Doe;dc=example;dc=com',flags=ldap.DN_FORMAT_LDAPV2)
['cn=John Doe', 'dc=example', 'dc=com']


Splitting a multi-valued RDN:

>>> ldap.dn.explode_rdn('cn=John Doe+mail=john.doe@example.com',flags=ldap.DN_FORMAT_LDAPV2)
['cn=John Doe', 'mail=john.doe@example.com']

Splitting a LDAPv3 DN with a multi-valued RDN into its AVA parts:


>>> ldap.dn.str2dn('cn=John Doe+mail=john.doe@example.com,dc=example,dc=com')
[[('cn', 'John Doe', 1), ('mail', 'john.doe@example.com', 1)], [('dc', 'example', 1)], [('dc', 'com', 1)]]

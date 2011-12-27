.. % $Id: ldap-dn.rst,v 1.6 2011/07/22 07:43:45 stroeder Exp $


:py:mod:`ldap.dn` LDAP Distinguished Name handling
====================================================

.. py:module:: ldap.dn
   :synopsis: LDAP Distinguished Name handling.
.. moduleauthor:: python-ldap project (see http://www.python-ldap.org/)


.. % Author of the module code;


.. seealso::

   For LDAPv3 DN syntax see:

   :rfc:`4514` - Lightweight Directory Access Protocol (LDAP): String Representation of Distinguished Names

.. seealso::

   For deprecated LDAPv2 DN syntax (obsoleted by LDAPv3) see:

   :rfc:`1779` - A String Representation of Distinguished Names

The :mod:`ldap.dn` module defines the following functions:


.. function:: escape_dn_chars(s)

   This function escapes characters in string *s* which  are special in LDAP
   distinguished names. You should use  this function when building LDAP DN strings
   from arbitrary input.

   .. % -> string


.. function:: str2dn(s [, flags=0])

   This function takes *s* and breaks it up into its component parts  down to AVA
   level. The optional parameter *flags* describes the DN format of s  (see
   :ref:`ldap-dn-flags`). Note that hex-encoded non-ASCII chars are decoded
   to the raw bytes.

   .. % -> list


.. function:: dn2str(dn)

   This function takes a decomposed DN in *dn* and returns  a single string. It's
   the inverse to :func:`str2dn`.  Special characters are escaped with the help of
   function :func:`escape_dn_chars`.

   .. % -> string


.. function:: explode_dn(dn [, notypes=0[, flags=0]])

   This function takes *dn* and breaks it up into its component parts.   Each part
   is known as an RDN (Relative Distinguished Name). The optional  *notypes*
   parameter is used to specify that only the RDN values be   returned and not
   their types. The optional parameter *flags*  describes the DN format of s (see
   :ref:`ldap-dn-flags`).    This function is emulated by function
   :func:`str2dn`  since the function ldap_explode_dn() in the C library is
   deprecated.

   .. % -> list


.. function:: explode_rdn(rdn [, notypes=0[, flags=0]])

   This function takes a (multi-valued) *rdn* and breaks it up  into a list of
   characteristic attributes. The optional  *notypes* parameter is used to specify
   that only the RDN values be   returned and not their types. The optional *flags*
   parameter  describes the DN format of s (see :ref:`ldap-dn-flags`).    This
   function is emulated by function :func:`str2dn`  since the function
   ldap_explode_rdn() in the C library is deprecated.

   .. % -> list


.. _ldap-dn-example:

Examples
^^^^^^^^^

Splitting a LDAPv3 DN to AVA level. Note that both examples have the same result
but in the first example the non-ASCII chars are passed as is (byte buffer string)
whereas in the second example the hex-encoded DN representation are passed to the function.

>>> ldap.dn.str2dn('cn=Michael Str\xc3\xb6der,dc=stroeder,dc=com',flags=ldap.DN_FORMAT_LDAPV3)
[[('cn', 'Michael Str\xc3\xb6der', 4)], [('dc', 'stroeder', 1)], [('dc', 'com', 1)]]
>>> ldap.dn.str2dn('cn=Michael Str\C3\B6der,dc=stroeder,dc=com',flags=ldap.DN_FORMAT_LDAPV3)
[[('cn', 'Michael Str\xc3\xb6der', 4)], [('dc', 'stroeder', 1)], [('dc', 'com', 1)]]


Splitting a LDAPv2 DN into RDN parts:

>>> ldap.dn.explode_dn('cn=Michael Stroeder;dc=stroeder;dc=com',flags=ldap.DN_FORMAT_LDAPV2)
['cn=Michael Stroeder', 'dc=stroeder', 'dc=com']


Splitting a multi-valued RDN:

>>> ldap.dn.explode_rdn('cn=Michael Stroeder+mail=michael@stroeder.com',flags=ldap.DN_FORMAT_LDAPV2)
['cn=Michael Stroeder', 'mail=michael@stroeder.com']

Splitting a LDAPv3 DN with a multi-valued RDN into its AVA parts:


>>> ldap.dn.str2dn('cn=Michael Stroeder+mail=michael@stroeder.com,dc=stroeder,dc=com')
[[('cn', 'Michael Stroeder', 1), ('mail', 'michael@stroeder.com', 1)], [('dc', 'stroeder', 1)], [('dc', 'com', 1)]]


.. % $Id: ldap-filter.rst,v 1.4 2011/07/21 20:33:26 stroeder Exp $


:py:mod:`ldap.filter` LDAP filter handling
============================================

.. py:module:: ldap.filter
   :synopsis: LDAP filter handling.
.. moduleauthor:: python-ldap project (see http://www.python-ldap.org/)


.. % Author of the module code;


.. seealso::

   :rfc:`4515` - Lightweight Directory Access Protocol (LDAP): String Representation of Search Filters.

The :mod:`ldap.filter` module defines the following functions:


.. function:: escape_filter_chars(assertion_value[, escape_mode=0])

   This function escapes characters in *assertion_value* which  are special in LDAP
   filters. You should use this function when  building LDAP filter strings from
   arbitrary input.    *escape_mode* means:  If :const:`0` only special chars
   mentioned in RFC 4515 are escaped.  If :const:`1` all NON-ASCII chars are
   escaped.  If :const:`2` all chars are escaped.

   .. % -> string


.. function:: filter_format(filter_template, assertion_values)

   This function applies :func:`escape_filter_chars` to each of the strings in
   list *assertion_values*. After that *filter_template* containing  as many
   :const:`%s` placeholders as count of assertion values is  used to build the
   whole filter string.

   .. % -> string


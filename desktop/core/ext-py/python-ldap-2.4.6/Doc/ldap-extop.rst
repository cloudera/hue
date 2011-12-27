.. % $Id: ldap-extop.rst,v 1.4 2011/07/22 17:28:46 stroeder Exp $

********************************************************************
:py:mod:`ldap.extop` High-level access to LDAPv3 extended operations
********************************************************************

.. py:module:: ldap.extop
   :synopsis: High-level access to LDAPv3 extended operations.


Classes
=======

This module defines the following classes:

.. autoclass:: ldap.extop.ExtendedRequest
   :members:


.. autoclass:: ldap.extop.ExtendedResponse
   :members:


:py:mod:`ldap.extop.dds` Classes for Dynamic Entries extended operations
========================================================================

.. py:module:: ldap.extop.dds
   :synopsis: Classes for Dynamic Entries extended operations

This requires :py:mod:`pyasn1` and :py:mod:`pyasn1_modules` to be installed.

.. seealso::

   :rfc:`2589` - Lightweight Directory Access Protocol (v3): Extensions for Dynamic Directory Services


.. autoclass:: ldap.extop.dds.RefreshRequest
   :members:


.. autoclass:: ldap.extop.dds.RefreshResponse
   :members:


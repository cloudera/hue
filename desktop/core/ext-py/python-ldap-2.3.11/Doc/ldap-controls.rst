.. % $Id: ldap-controls.rst,v 1.2 2009/04/17 12:14:52 stroeder Exp $


:mod:`ldap.controls` High-level access to LDAP controls
============================================================

.. module:: ldap.controls
   :synopsis: High-level access to LDAP controls.
.. moduleauthor:: python-ldap project (see http://www.python-ldap.org/)


The :mod:`ldap.controls` module defines the following classes:

.. % Author of the module code;


.. class:: LDAPControl(controlType, criticality [, controlValue=:const:`None` [, encodedControlValue=:const:`None`]])

   Base class for all LDAP controls. This class should not be used directly,
   instead one of the following subclasses should be used as appropriate.


   .. method:: LDAPControl.encodeControlValue(value)

      Dummy method to be overridden by subclasses.


   .. method:: LDAPControl.decodeControlValue(value)

      Dummy method to be overridden by subclasses.


   .. method:: LDAPControl.getEncodedTuple()

      Return a readily encoded 3-tuple which can be directly  passed to C module
      _ldap. This method is called by  function :func:`ldap.EncodeControlTuples`.


.. class:: BooleanControl(controlType, criticality [, controlValue=:const:`None` [, encodedControlValue=:const:`None`]])

   Base class for simple controls with booelan control value.    In this base class
   *controlValue* has to be passed as  boolean type (:const:`True`/:const:`False`
   or :const:`1`/:const:`0`).


.. class:: SimplePagedResultsControl(controlType, criticality [, controlValue=:const:`None` [, encodedControlValue=:const:`None`]])

   The class provides the LDAP Control Extension for Simple Paged Results
   Manipulation. *controlType* is ignored  in favor of
   :const:`ldap.LDAP_CONTROL_PAGE_OID`.


   .. seealso::

      :rfc:`2696` - LDAP Control Extension for Simple Paged Results Manipulation

.. class:: MatchedValuesControl(criticality [, controlValue=:const:`None`])

   This class provides the LDAP Matched Values control. *controlValue* is an LDAP
   filter.


   .. seealso::

      :rfc:`3876` - Returning Matched Values with the Lightweight Directory Access Protocol version 3 (LDAPv3)

The :mod:`ldap.controls` module defines the following functions:


.. function:: EncodeControlTuples(ldapControls)

   Returns list of readily encoded 3-tuples which can be directly  passed to C
   module _ldap.

   .. % -> list


.. function:: DecodeControlTuples(ldapControlTuples)

   Decodes a list of readily encoded 3-tuples as returned by the C module _ldap.

   .. % -> list


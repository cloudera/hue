.. % $Id: ldap-resiter.rst,v 1.5 2011/08/27 15:43:06 stroeder Exp $


:py:mod:`ldap.resiter` Generator for stream-processing of large search results
==============================================================================

.. py:module:: ldap.resiter
   :synopsis: Generator for stream-processing of large search results.
.. moduleauthor:: python-ldap project (see http://www.python-ldap.org/)


.. _ldap.resiter-classes:

.. py:class:: ResultProcessor

This is a mix-in class to be used with class :py:class:`ldap.LDAPObject` or
derived classes which has these methods:

  .. automethod:: ldap.resiter.ResultProcessor.allresults


.. _ldap.resiter-example:


Examples
========

.. _ldap.resiter.ResultProcessor-example:

Using ldap.resiter.ResultProcessor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This example demonstrates how to use mix-in class ldap.resiter.ResultProcessor for
retrieving results formerly requested with :py:meth:`ldap.LDAPObject.search()` and
processing them in a for-loop.

::

  import sys,ldap,ldap.resiter

  class MyLDAPObject(ldap.ldapobject.LDAPObject,ldap.resiter.ResultProcessor):
    pass

  l = MyLDAPObject('ldap://localhost')

  # Asynchronous search method
  msg_id = l.search('dc=stroeder,dc=com',ldap.SCOPE_SUBTREE,'(objectClass=*)')

  for res_type,res_data,res_msgid,res_controls in l.allresults(msg_id):
    for dn,entry in res_data:
      # process dn and entry
      print dn,entry['objectClass']

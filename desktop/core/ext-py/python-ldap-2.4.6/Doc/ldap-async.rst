.. % $Id: ldap-async.rst,v 1.4 2011/07/28 08:52:01 stroeder Exp $


**************************************************************
:py:mod:`ldap.async` Stream-processing of large search results
**************************************************************

.. py:module:: ldap.async
   :synopsis: Framework for stream-processing of large search results.

With newer Python versions one might want to consider using
:py:mod:`ldap.resiter` instead.


Classes
=======

.. autoclass:: ldap.async.AsyncSearchHandler
   :members:

.. autoclass:: ldap.async.List
   :members:

.. autoclass:: ldap.async.Dict
   :members:

.. autoclass:: ldap.async.IndexedDict
   :members:

.. autoclass:: ldap.async.LDIFWriter
   :members:

.. autoclass:: ldap.async.DSMLWriter
   :members:

.. _ldap.async-example:

Examples
========

.. _ldap.async-example.List:

Using ldap.async.List
^^^^^^^^^^^^^^^^^^^^^

This example demonstrates how to use class ldap.async.List for
retrieving partial search results even though the exception
:exc:`ldap.SIZELIMIT_EXCEEDED` was raised because a server side limit was hit. ::

   import sys,ldap,ldap.async

   s = ldap.async.List(
     ldap.initialize('ldap://localhost'),
   )

   s.startSearch(
     'dc=stroeder,dc=com',
     ldap.SCOPE_SUBTREE,
     '(objectClass=*)',
   )

   try:
     partial = s.processResults()
   except ldap.SIZELIMIT_EXCEEDED:
     sys.stderr.write('Warning: Server-side size limit exceeded.\n')
   else:
     if partial:
       sys.stderr.write('Warning: Only partial results received.\n')

   sys.stdout.write(
     '%d results received.\n' % (
       len(s.allResults)
     )
   )

.. _ldap.async-example.LDIFWriter:

Using ldap.async.LDIFWriter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This example demonstrates how to use class ldap.async.LDIFWriter
for writing search results as LDIF to stdout. ::

   import sys,ldap,ldap.async

   s = ldap.async.LDIFWriter(
     ldap.initialize('ldap://localhost:1390'),
     sys.stdout
   )

   s.startSearch(
     'dc=stroeder,dc=com',
     ldap.SCOPE_SUBTREE,
     '(objectClass=*)',
   )

   try:
     partial = s.processResults()
   except ldap.SIZELIMIT_EXCEEDED:
     sys.stderr.write('Warning: Server-side size limit exceeded.\n')
   else:
     if partial:
       sys.stderr.write('Warning: Only partial results received.\n')

   sys.stderr.write(
     '%d results received.\n' % (
       s.endResultBreak-s.beginResultsDropped
     )
   )


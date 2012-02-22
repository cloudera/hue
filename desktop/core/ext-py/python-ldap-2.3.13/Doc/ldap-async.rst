.. % $Id: ldap-async.rst,v 1.2 2009/04/17 12:14:52 stroeder Exp $


:mod:`ldap.async` Framework for stream-processing of large search results
==============================================================================

.. module:: ldap.async
   :synopsis: Framework for stream-processing of large search results.
.. moduleauthor:: python-ldap project (see http://www.python-ldap.org/)


.. % Author of the module code;


.. _ldap.async-example:

Examples for ldap.async
------------------------

.. _ldap.async-example.List:

Using ldap.async.List
^^^^^^^^^^^^^^^^^^^^^^

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


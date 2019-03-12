********************************************************************
:py:mod:`ldap.asyncsearch` Stream-processing of large search results
********************************************************************

.. py:module:: ldap.asyncsearch
   :synopsis: Framework for stream-processing of large search results.

With newer Python versions one might want to consider using
:py:mod:`ldap.resiter` instead.


.. versionchanged:: 3.0
   In Python 3.7 ``async`` is a reserved keyword. The module
   :py:mod:`ldap.async` has been renamed to :py:mod:`ldap.asyncsearch`. The
   old name :py:mod:`ldap.async` is still available for backwards
   compatibility.

.. deprecated:: 3.0
   The old name :py:mod:`ldap.async` is deprecated, but will not be removed
   until Python 3.6 reaches end-of-life.


Classes
=======

.. autoclass:: ldap.asyncsearch.AsyncSearchHandler
   :members:

.. autoclass:: ldap.asyncsearch.List
   :members:

.. autoclass:: ldap.asyncsearch.Dict
   :members:

.. autoclass:: ldap.asyncsearch.IndexedDict
   :members:

.. autoclass:: ldap.asyncsearch.LDIFWriter
   :members:

.. _ldap.asyncsearch-example:

Examples
========

.. _ldap.asyncsearch-example.List:

Using ldap.asyncsearch.List
^^^^^^^^^^^^^^^^^^^^^^^^^^^

This example demonstrates how to use class ldap.asyncsearch.List for
retrieving partial search results even though the exception
:exc:`ldap.SIZELIMIT_EXCEEDED` was raised because a server side limit was hit. ::

   import sys,ldap,ldap.asyncsearch

   s = ldap.asyncsearch.List(
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

.. _ldap.asyncsearch-example.LDIFWriter:

Using ldap.asyncsearch.LDIFWriter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This example demonstrates how to use class ldap.asyncsearch.LDIFWriter
for writing search results as LDIF to stdout. ::

   import sys,ldap,ldap.asyncsearch

   s = ldap.asyncsearch.LDIFWriter(
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

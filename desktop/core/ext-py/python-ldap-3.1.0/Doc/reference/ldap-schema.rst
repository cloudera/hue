********************************************
:py:mod:`ldap.schema` Handling LDAPv3 schema
********************************************

.. py:module:: ldap.schema

This module deals with schema information usually retrieved from
a special subschema subentry provided by the server.
It is closely modeled along the directory information model described
in the following RFC with which you should make yourself familiar
when trying to use this module:

.. seealso::

   :rfc:`4512` - Lightweight Directory Access Protocol (LDAP): Directory Information Models


:py:mod:`ldap.schema.subentry` Processing LDAPv3 subschema subentry
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. py:module:: ldap.schema.subentry


.. py:data:: NOT_HUMAN_READABLE_LDAP_SYNTAXES

   Dictionary where the keys are the OIDs of LDAP syntaxes known to be
   not human-readable when displayed to a console without conversion
   and which cannot be decoded to a :py:data:`types.UnicodeType`.


Functions
=========

.. autofunction:: ldap.schema.subentry.urlfetch

Classes
=======

.. autoclass:: ldap.schema.subentry.SubSchema
   :members:


:py:mod:`ldap.schema.models` Schema elements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. py:module:: ldap.schema.models


.. autoclass:: ldap.schema.models.Entry
   :members:

.. autoclass:: ldap.schema.models.SchemaElement
   :members:

.. autoclass:: ldap.schema.models.AttributeType
   :members:

.. autoclass:: ldap.schema.models.ObjectClass
   :members:

.. autoclass:: ldap.schema.models.MatchingRule
   :members:

.. autoclass:: ldap.schema.models.MatchingRuleUse
   :members:

.. autoclass:: ldap.schema.models.DITContentRule
   :members:

.. autoclass:: ldap.schema.models.NameForm
   :members:

.. autoclass:: ldap.schema.models.DITStructureRule
   :members:


.. _ldap.schema-example:

Examples for ldap.schema
^^^^^^^^^^^^^^^^^^^^^^^^

::

   import ldap.schema

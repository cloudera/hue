.. % $Id: ldap-modlist.rst,v 1.2 2009/04/17 12:14:52 stroeder Exp $


:mod:`ldap.modlist` Generate modify lists
==============================================

.. module:: ldap.modlist
   :synopsis: Generate modify lists.
.. moduleauthor:: python-ldap project (see http://www.python-ldap.org/)


The :mod:`ldap.modlist` module defines the following functions:

.. % Author of the module code;


.. function:: addModlist(entry [, ignore_attr_types=[]])

   This function builds a list suitable for passing it  directly as argument
   *modlist* to method :meth:`add` or  its synchronous counterpart :meth:`add_s`.
   *entry* is a dictionary like returned when  receiving search results.

   .. % -> list


.. function:: modifyModlist( old_entry, new_entry [, ignore_attr_types=[] [, ignore_oldexistent=0]])

   This function builds a list suitable for passing it directly as argument
   *modlist* to method :meth:`modify` or its synchronous counterpart
   :meth:`modify_s`.  Roughly when applying the resulting modify list to an entry
   holding  the data *old_entry* it will be modified in such a way that the  entry
   holds *new_entry* after the modify operation. It is handy in  situations when it
   is impossible to track user changes to an entry's  data or for synchronizing
   operations. *old_entry* and *new_entry* are dictionaries  like returned when
   receiving search results. *ignore_attr_types* is a list of attribute type
   names which  shall be ignored completely. These attribute types will not appear
   in the result. If *ignore_oldexistent* is non-zero attribute type names which
   are in *old_entry* but are not found in *new_entry* at all  are not deleted.
   This is handy for situations where your application  sets attribute value to "
   for deleting an attribute.  In most cases leave zero.

   .. % -> list


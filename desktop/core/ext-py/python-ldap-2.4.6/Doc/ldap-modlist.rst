.. % $Id: ldap-modlist.rst,v 1.4 2011/07/22 17:39:44 stroeder Exp $


:py:mod:`ldap.modlist` Generate modify lists
==============================================

.. py:module:: ldap.modlist


The :mod:`ldap.modlist` module defines the following functions:


.. function:: addModlist(entry [, ignore_attr_types=[]]) -> list

   This function builds a list suitable for passing it directly as argument
   *modlist* to method :py:meth:`ldap.ldapobject.LDAPObject.add` or
   its synchronous counterpart :py:meth:`ldap.ldapobject.LDAPObject.add_s`.

   *entry* is a dictionary like returned when receiving search results.

   *ignore_attr_types* is a list of attribute type
   names which shall be ignored completely. Attributes of these types will not appear
   in the result at all.


.. function:: modifyModlist( old_entry, new_entry [, ignore_attr_types=[] [, ignore_oldexistent=0 [, case_ignore_attr_types=None]]]) -> list

   This function builds a list suitable for passing it directly as argument
   *modlist* to method :py:meth:`ldap.ldapobject.LDAPObject.modify` or
   its synchronous counterpart :py:meth:`ldap.ldapobject.LDAPObject.modify_s`. 
   
   Roughly when applying the resulting modify list to an entry
   holding  the data *old_entry* it will be modified in such a way that the entry
   holds *new_entry* after the modify operation. It is handy in situations when it
   is impossible to track user changes to an entry's data or for synchronizing
   operations.
   
   *old_entry* and *new_entry* are dictionaries like returned when
   receiving search results.
   
   *ignore_attr_types* is a list of attribute type
   names which shall be ignored completely. These attribute types will not appear
   in the result at all.

   If *ignore_oldexistent* is non-zero attribute type names which
   are in *old_entry* but are not found in *new_entry* at all are not deleted.
   This is handy for situations where your application sets attribute value to
   an empty string for deleting an attribute. In most cases leave zero.

   If *case_ignore_attr_types* is a list of attribute type names for which
   the comparison will be conducted case-insensitive. It is useful in
   situations where a LDAP server normalizes values and one wants to avoid
   unnecessary changes (e.g. case of attribute type names in DNs).

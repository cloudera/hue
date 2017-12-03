Backward Compatibility
======================

pyOpenSSL has a very strong backward compatibility policy.
Generally speaking, you shouldn't ever be afraid of updating.

If breaking changes are needed do be done, they are:

#. …announced in the :doc:`changelog`.
#. …the old behavior raises a :exc:`DeprecationWarning` for a year.
#. …are done with another announcement in the :doc:`changelog`.

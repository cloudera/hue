
.. _migration-structure:

Migration Structure
===================

Migrations are, at the most basic level, files inside your app's migrations/
directory.

When South loads migrations, it loads all the python files inside migrations/
in ASCII sort order (e.g. 1 is before 10 is before 2), and expects to find a
class called Migration inside each one, with at least a ``forwards()``
and ``backwards()`` method.

When South wants to apply a migration, it simply calls the ``forwards()``
method, and similarly when it wants to roll back a migration it calls
``backwards()``. It's up to you what you do inside these methods; the usual
thing is to do database changes, but you don't have to.

Sort Order
----------

Since migrations are loaded in ASCII sort order, they won't be applied in the
correct order if you call them ``1_first, 2_second, ..., 10_tenth``.
(10 sorts before 2).

Rather than force a specific naming convention, we suggest that if you want to
use numerical migrations in this fashion (as we suggest you do) that you prefix
the numbers with zeroes like so: ``0001_first, 0002_second, 0010_tenth``.

All of South's automatic creation code will follow this scheme.

Transactions
------------

Whenever ``forwards()`` or ``backwards()`` is called it is called inside a
database transaction, which is committed if the method executes successfully
or rolled back if it raises an error.

If you need to use two or more transactions inside a migration, either use
two separate migrations (if you think it's appropriate), or have a snippet
like this where you want a new transaction::

    db.commit_transaction()     # Commit the first transaction
    db.start_transaction()      # Start the second, committed on completion

Note that you must commit and start the next transaction if you are making
both data and column changes. If you don't do this, you'll end up with your
database hating you for asking it the impossible.

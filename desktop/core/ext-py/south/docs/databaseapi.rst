
.. _database-api:

Database API
============

South ships with a full database-agnostic API for performing schema changes
on databases, much like Django's ORM provides data manipulation support.

Currently, South supports:

 - PostgreSQL
 - MySQL
 - SQLite
 - Microsoft SQL Server (beta support)
 - Oracle (alpha support)


.. _accessing-the-api:

Accessing The API
-----------------

South automatically exposes the correct set of database API operations as
``south.db.db``; it detects which database backend you're using from your
Django settings file. It's usually imported using::

 from south.db import db

If you're using multiple database support (Django 1.2 and higher),
there's a corresponding ``south.db.dbs`` dictionary
which contains a DatabaseOperations object (the object which has the methods
defined above) for each database alias in your configuration file::

 from south.db import dbs
 dbs['users'].create_table(...)
 
You can tell which backend you're talking to inside of a migration by examining
``db.backend_name`` - it will be one of ``postgres``, ``mysql``, ``sqlite3``, 
``pyodbc`` or ``oracle``.


Database-Specific Issues
------------------------

South provides a large amount of features, and not all features are supported by
all database backends.

 - PostgreSQL supports all of the South features; if you're unsure which database
   engine to pick, it's the one we recommend for migrating on.

 - MySQL doesn't have transaction support for schema modification, meaning that
   if a migration fails to apply, the database is left in an inconsistent state,
   and you'll probably have to manually fix it. South will try and sanity-check
   migrations in a dry-run phase, and give you hints of what to do when it
   fails, however.

 - SQLite doesn't natively support much schema altering at all, but South
   has workarounds to allow deletion/altering of columns. Unique indexes are
   still unsupported, however; South will silently ignore any such commands.
 
 - SQL Server has been supported for a while, and works in theory, but the
   implementation itself may have bugs, as it's a contributed module and isn't
   under primary development. Patches and bug reports are welcome.
 
 - Oracle is a new module as of the 0.7 release, and so is very much alpha.
   The most common operations work, but others may be missing completely;
   we welcome bug reports and patches against it (as with all other modules).


Methods
-------

These are how you perform changes on the database. See :ref:`accessing-the-api`
to see how to get access to the ``db`` object.

.. contents::
   :local:
   :depth: 1
 


db.add_column
^^^^^^^^^^^^^

::

 db.add_column(table_name, field_name, field, keep_default=True)
 
Adds a column called ``field_name`` to the table ``table_name``, of the type
specified by the field instance field.

If ``keep_default`` is True, then any default value specified on the field will
be added to the database schema for that column permanently. If not, then the
default is only used when adding the column, and then dropped afterwards.

Note that the default value for fields given here is only ever used when
adding the column to a non-empty table; the default used by the ORM in your
application is the one specified on the field in your models.py file, as Django
handles adding default values before the query hits the database.

The only case where having the default stored in the database as well would make
a difference would be where you are interacting with the database from somewhere
else, or Django doesn't know about the added column at all.

Also, note that the name you give for the column is the **field name**, not the
column name - if the field you pass in is a ForeignKey, for example, the
real column name will have _id on the end.

Examples
""""""""

A normal column addition (the column is nullable, so all existing rows will have
it set to NULL)::

 db.add_column('core_profile', 'height', models.IntegerField(null=True))

Providing a default value instead, so all current rows will get this value for
'height'::

 db.add_column('core_profile', 'height', models.IntegerField(default=-1))

Same as above, but the default is not left in the database schema::

 db.add_column('core_profile', 'height', models.IntegerField(default=-1), keep_default=False)



db.alter_column
^^^^^^^^^^^^^^^

::

 db.alter_column(table_name, column_name, field, explicit_name=True)
 
Alters the column ``column_name`` on the table ``table_name`` to match
``field``. Note that this cannot alter all field attributes; for example, if
you want to make a field ``unique=True``, you should instead use
``db.add_index`` with ``unique=True``, and if you want to make it a primary
key, you should look into ``db.drop_primary_key`` and ``db.create_primary_key``.

If explicit_name is false, ForeignKey? fields will have _id appended to the end
of the given column name - this lets you address fields as they are represented
in the model itself, rather than as the column name.

Examples
""""""""

A simple change of the length of a VARCHAR column::

 # Assume the table was created with name = models.CharField(max_length=50)
 db.alter_column('core_nation', 'name', models.CharField(max_length=200))

We can also change it to a compatible field type::

 db.alter_column('core_nation', 'name', models.TextField())

If we have a ForeignKey? named 'user', we can address it without the implicit '_id' on the end::

 db.alter_column('core_profile', 'user', models.ForeignKey(orm['auth.User'], null=True, blank=True), explicit_name=False)

Or you can specify the same operation with an explicit name::

 db.alter_column('core_profile', 'user_id', models.ForeignKey(orm['auth.User'], null=True, blank=True))



db.clear_table
^^^^^^^^^^^^^^

::

 db.clear_table(table_name)

Deletes all rows from the table (truncation). Never used by South's
autogenerators, but can prove useful if you're writing data migrations.

Examples
""""""""

Clear all cached geocode results, as the schema is changing::

 db.clear_table('core_geocoded')
 db.add_column('core_geocoded', ...) 



db.commit_transaction
^^^^^^^^^^^^^^^^^^^^^

::

 db.commit_transaction()
 
Commits the transaction started at a ``db.start_transaction`` call.



db.create_index
^^^^^^^^^^^^^^^

::

 db.create_index(table_name, column_names, unique=False, db_tablespace='')
 
Creates an index on the list of columns ``column_names`` on the table
``table_name``.

By default, the index is simply for speed; if you would like a unique index,
then specify ``unique=True``, although you're better off using
``db.create_unique`` for that.

``db_tablespace`` is an Oracle-specific option, and it's likely you won't need
to use it.

Examples
""""""""

Creating an index on the 'name' column::

 db.create_index('core_profile', ['name'])
 
Creating a unique index on the combination of 'name' and 'age' columns::

 db.create_index('core_profile', ['name', 'age'], unique=True)



db.create_primary_key
^^^^^^^^^^^^^^^^^^^^^

::

 db.create_primary_key(table_name, columns)
 
Creates a primary key spanning the given ``columns`` for the table. Remember,
you can only have one primary key per table; use ``db.delete_primary_key``
first if you already have one.

Examples
""""""""

Swapping from the ``id`` to ``uuid`` as a primary key::

 db.delete_primary_key('core_upload')
 db.create_primary_key('core_upload', ['uuid'])
 
Adding a new composite primary key on "first name" and "last name"::

 db.create_primary_key('core_people', ['first_name', 'last_name'])
 


db.create_table
^^^^^^^^^^^^^^^

::

 db.create_table(table_name, fields)
 fields = ((field_name, models.SomeField(somearg=4)), ...)
 
This call creates a table called *table_name* in the database with the schema
specified by *fields*, which is a tuple of ``(field_name, field_instance)``
tuples.

Note that this call will not automatically add an id column;
you are responsible for doing that.

We recommend you create calls to this function using ``schemamigration``, either
in ``--auto`` mode, or by using ``--add-model``.

Examples
""""""""

A simple table, with one field, name, and the default id column::

 db.create_table('core_planet', (
     ('id', models.AutoField(primary_key=True)),
     ('name', models.CharField(unique=True, max_length=50)),
 ))
 
A more complex table, which uses the ORM Freezer for its foreign keys::

 db.create_table('core_nation', (
     ('name', models.CharField(max_length=255)),
     ('short_name', models.CharField(max_length=50)),
     ('slug', models.SlugField(unique=True)),
     ('planet', models.ForeignKey(orm.Planet, related_name="nations")),
     ('flag', models.ForeignKey(orm.Flag, related_name="nations")),
     ('planet_name', models.CharField(max_length=50)),
     ('id', models.AutoField(primary_key=True)),
 ))



db.create_unique
^^^^^^^^^^^^^^^^

::

 create_unique(table_name, columns)
 
Creates a unique index or constraint on the list of columns ``columns`` on the
table ``table_name``.

Examples
""""""""

Declare the pair of fields ``first_name`` and ``last_name`` to be unique::

 db.create_unique('core_people', ['first_name', 'last_name'])



db.delete_column
^^^^^^^^^^^^^^^^

::

 db.delete_column(table_name, column_name)
 
Deletes the column ``column_name`` from the table ``table_name``.

Examples
""""""""

Delete a column from a table::

 db.delete_column('core_nation', 'title')



db.delete_foreign_key
^^^^^^^^^^^^^^^^^^^^^

::

 delete_foreign_key(table_name, column)
 
Drops any foreign key constraints on the given column, if the database backend
supported them in the first place.

Examples
""""""""

Remove the foreign key constraint from user_id:

 db.delete_foreign_key('core_people', 'user_id')



db.delete_primary_key
^^^^^^^^^^^^^^^^^^^^^

::

 db.delete_primary_key(table_name)
 
Deletes the current primary key constraint on the table. Does not remove the
columns the primary key was using.

Examples
""""""""

Swapping from the ``id`` to ``uuid`` as a primary key::

 db.delete_primary_key('core_upload')
 db.create_primary_key('core_upload', ['uuid'])
 

 
db.delete_table
^^^^^^^^^^^^^^^

::

 db.delete_table(table_name, cascade=True)

Deletes (drops) the named table from the database. If cascade is True, drops any
related constraints as well.

Examples
""""""""

Usual call::

 db.delete_table("core_planet")

Not cascading (beware, may fail)::

 db.delete_table("core_planet", cascade=False)



db.delete_unique
^^^^^^^^^^^^^^^^

::

 delete_unique(table_name, columns)
 
Deletes a unique index or constraint on the list of columns ``columns`` on the
table ``table_name``. The constraint/index. must already exist.

Examples
""""""""

Declare the pair of fields ``first_name`` and ``last_name`` to no longer
be unique::

 db.delete_unique('core_people', ['first_name', 'last_name'])



db.execute
^^^^^^^^^^

::

 db.execute(sql, params=[])
 
Executes the **single** raw SQL statement ``sql`` on the database; optionally
use params to replace the %s instances in sql (this is the recommended way of
doing parameters, as it escapes them correctly for all databases).

If you want to execute a series of SQL statements instead, use
``db.execute_many``.

Note that you should avoid using raw SQL wherever possible, as it will break the
database abstraction in many cases. If you want to handle data, consider using
the ORM Freezer, and remember that many operations such as creating indexes and
changing primary keys have functions in the DB layer.

If there's a common operation you'd like to see added to the DB abstraction
layer in South, consider asking on the mailing list or creating a ticket.

Examples
""""""""

VACUUMing a table::

 db.execute("VACUUM ANALYZE core_profile")

Updating values (this sort of task should really be done using the frozen ORM)::

 db.execute("UPDATE core_profile SET name = %s WHERE name = %s", ["andy", "andrew"])



db.execute_many
^^^^^^^^^^^^^^^

::

 db.execute_many(sql, regex=r"(?mx) ([^';]* (?:'[^']*'[^';]*)*)", comment_regex=r"(?mx) (?:^\s*$)|(?:--.*$)")
 
Executes the given multi-statement SQL string ``sql``. The two parameters are
the regular expressions for splitting up statements (``regex``) and removing
comments (``comment_regex``). We recommend you leave these at their default
values, as they work on almost all SQL files.

If you only want to execute a single SQL statement, consider using
``db.execute``, as it offers parameter escaping, and the regexes sometimes get
the splitting wrong.

Examples
""""""""

Run the PostGIS initialisation file::

 db.execute_many(open("/path/to/lwpostgis.sql").read())



db.rename_column
^^^^^^^^^^^^^^^^

::

 db.rename_column(table_name, column_name, new_column_name)
 
Renames the column ``column_name`` in table ``table_name`` to
``new_column_name``.

Examples
""""""""

Simple rename::

 db.rename_column('core_nation', 'name', 'title')

 

db.rename_table
^^^^^^^^^^^^^^^

::

 db.rename_table(table_name, new_table_name)

Renames the table table_name to the new name new_table_name.

This won't affect what tables your models are looking for, of course;
this is useful, for example, if you've renamed a model
(and don't want to specify the old table name in Meta).

Examples
""""""""

Simple rename::

 db.rename_table('core_profile', 'core_userprofile')



db.rollback_transaction
^^^^^^^^^^^^^^^^^^^^^^^

::

 db.rollback_transaction()
 
Rolls back the transaction started at a ``db.start_transaction`` call.



db.send_create_signal
^^^^^^^^^^^^^^^^^^^^^

::

 db.send_create_signal(app_label, model_names)
 
Sends the post_syncdb signal for the given models ``model_names`` in the app
``app_label``.

This signal is used by various bits of django internals - such as contenttypes
- to hook new models into themselves, so you should really call it after the
relevant ``db.create_table`` call. ``startmigration`` will add this
automatically for you.

Note that the signals are not sent until the end of the whole migration
sequence, so your handlers will not get called until all migrations are done.
This is so that your handlers can deal with the most recent version of the
model's schema, rather than the one in the migration where the signal is
originally sent.

Examples
""""""""

Sending a signal for the 'Profile' and 'Planet' models in my app 'core'::

 db.send_create_signal('core', ['Profile', 'Planet'])



db.start_transaction
^^^^^^^^^^^^^^^^^^^^

::

 db.start_transaction()
 
Wraps the following code (until it meets a ``db.rollback_transaction`` or
``db.commit_transaction`` call) in a transaction.

 


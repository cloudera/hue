
.. _commands:

Command Reference
=================

South is mainly used via the console and its three important commands: migrate,
schemamigration and datamigration. It also overrides a few parts of syncdb.

migrate
-------

The migrate command is used to control the migration of the system forwards or
backwards through the series of migrations for any given app.

The most common use is::

 ./manage.py migrate myapp
 
This will migrate the app myapp forwards through all the migrations.
If you want to migrate all the apps at once, run::

 ./manage.py migrate

This has the same effect as calling the first example for every app,
and will deal with Dependencies properly.

You can also specify a specific migration to migrate to::

 ./manage.py migrate myapp 0002_add_username

Note that, if the system has already migrated past the specified migration,
it will roll back to it instead. If you want to migrate all the way back,
specify the special migration name zero::

 ./manage.py migrate myapp zero

You can also just give prefixes of migrations, to save typing::

 ./manage.py migrate myapp 0002

But they must be unique::

 $ ./manage.py migrate myapp 000
 Running migrations for myapp:
  - Prefix 00 matches more than one migration:
      0001_initial
      0002_add_username

Options
^^^^^^^

 - ``--all``: Used instead of an app name, allows you to migrate all
   applications to the same target. For example,
   ``./manage.py migrate --all --fake 0001`` if you are converting a lot of apps.
 - ``--list``: Shows what migrations are available, and puts a * next to
   ones which have been applied.
 - ``--merge``: Runs any missed (out-of-order) migrations without rolling
   back to them.
 - ``--no-initial-data``: Doesn't load in any initial data fixtures after a
   full upwards migration, if there are any.
 - ``--fake``: Records the migration sequence as having been applied, but
   doesn't actually run it. Useful for ConvertingAnApp.
 - ``--db-dry-run``: Loads and runs the migration, but doesn't actually
   access the database (the SQL generated is thrown away at the last minute).
   The migration is also not recorded as being run; this is useful for
   sanity-testing migrations to check API calls are correct.

Conflict Resolution
^^^^^^^^^^^^^^^^^^^

South's migration system really comes into its own when you start getting
conflicting migrations - that is, migrations that have been applied in
the wrong sequence.

One example is if Anne writes new migrations 0003_foo and 0004_bar, runs the
migration up to 0004 to make sure her local copy is up-to-date, and then updates
her code from (say) Subversion. In the meantime, her coworker Bob has written a
migration 0003_baz, which gets pulled in.

Now, there's a problem. 0003_phou should have been applied before 0004_bar,
but it hasn't been; in this situation, South will helpfully say something like::

  Running migrations for aeblog:
   - Current migration: 5 (after 0004_bar)
   - Target migration: 5 (after 0004_bar)
   ! These migrations should have been applied already, but aren't:
     - 0003_phou
   ! Please re-run migrate with one of these switches:
     --skip: Ignore this migration mismatch and keep going
     --merge: Just apply the missing migrations out of order
     If you want to roll back to the first of these migrations
     and then roll forward, do:
       ./manage.py migrate --skip 0002_add_username
       ./manage.py migrate

As you can see, you have two real options; ``--merge``, which will just apply
the missing migration and continue, and the two commands which roll back to
before the missing migration (using ``--skip`` to ignore the error we're dealing
with) and then migrating properly, in order, from there to the end.

Using ``--skip`` by itself will let you continue, but isn't much of a solution;
South will still complain the next time you run a migrate without ``--skip``.

Sometimes, even worse things happen and South finds out that an applied
migration has gone missing from the filesystem. In this scenario, it will
politely tell you to go fix the problem yourself, although in more recent
versions, you also have the option to tell South to wipe all records of the
missing migrations being applied.

Initial Data and post_syncdb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

South will load initial_data files in the same way as syncdb, but it loads them
at the end of every successful migration process, so ensure they are kept
up-to-date, along with the rest of your fixtures (something to help ease the
pain of migrating fixtures may appear shortly in South).

South also sends the post_syncdb signal when a model's table is first created
(this functionality requires that you generated those migrations with
startmigration). This behaviour is intended to mirror the behaviour of syncdb,
although for sanity reasons you may want to consider moving any setup code
connected to such a signal into a migration.

schemamigration
---------------

*(In South 0.6 and below, this is called startmigration)*

While migrate is the real meat and bones of South, schemamigration is by
comparison an entirely optional extra. It's a utility to help write some of
your migrations (specifically, the ones which change the schema) for
you; if you like, you can ignore it and write everything youself, in which
case we wish you good luck, and happy typing.

However, if you have a sense of reason, you'll realise that having the large
majority of your migrations written for you in undoubtedly a good thing.

The main use of schemamigration is when you've just finished your shiny new
models.py and want to load up your database. In vanilla Django, you'd just run
syncdb - however, with migrations, you'll need a migration to create the tables.

In this scenario, you just run::

 ./manage.py schemamigration myapp --initial

That will write one big migration to create all the tables for the models in
your app; just run ``./manage.py migrate`` to get it in and you're done in only
one more step than syncdb!

Later on, you'll add models to your app, or change your fields. Each time you do
this, run schemamigration with the --auto flag::

 ./manage.py schemamigration myapp --auto changed_user_model_bug_434

You can also manually specify changes::

 ./manage.py schemamigration mitest some_cols --add-field User.age --add-model User

See the tutorial for more.

Finally, if you're writing a schema migration that South can't automatically create
for you (yet!) then you can just create a skeleton:

./manage.py schemamigration myapp my_new_column_migration --empty

Note that if you're writing a data migration, you should use the
:ref:`commands-datamigration` command instead.

Options
^^^^^^^

Note that you can combine as many ``--add-X`` options as you like.

 - ``--add-model``: Generates a creation migration for the given modelname.
 - ``--add-field``: Generates an add-column migration for modelname.field.
 - ``--add-index``: Generates an add-index migration for modelname.field.
 - ``--initial``: Like having --model for every model in your app.
   You should use this only for your first migration.
 - ``--auto``: Generates a migration with automatically-detected actions.
 - ``--stdout``: Writes the migration to stdout instead of a file.

.. _commands-datamigration: 
 
datamigration
-------------

*(In South 0.6 and below, this is called startmigration)*

When you want to create a data migration, use this command to create a blank
template to write your migration with::

 ./manage.py datamigration books capitalise_titles
 
You can also freeze in additional apps if you want::

 ./manage.py datamigration books capitalise_titles --freeze awards

Options
^^^^^^^

 - ``--freeze``: Use appname or appname.modelname to freeze additional models into the app.
 - ``--stdout``: Writes the migration to stdout instead of a file.
 
 
graphmigrations
---------------

*(New in South 0.7)*

Run this command to generate a graphviz .dot file for your migrations; you
can then use this to generate a graph of your migrations' dependencies.

Typical usage::

 ./manage.py graphmigrations | dot -Tpng -omigrations.png
 
This command can be particularly helpful to examine complex dependency sets
between lots of different apps [#]_.

 .. [#] This command was written and used for the first time while helping the
        debug the rather complex set of dependencies in django-cms; it's quite
        a sight to behold.

Options
^^^^^^^

This command has no options.


syncdb
------

South overrides the Django syncdb command; as well as changing the output
to show apps delineated by their migration status, it also makes syncdb only
work on a subset of the apps - those without migrations.

If you want to run syncdb on all of the apps, then use ``--all``, but be warned;
this will put your database schema and migrations out of sync. If you do this,
you *might* be able to fix it with::

 ./manage.py migrate --fake

Options
^^^^^^^

 - ``--all``: Makes syncdb operate on all apps, not just unmigrated ones.

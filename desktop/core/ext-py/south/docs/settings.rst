
.. _settings:

Settings
========

South has its own clutch of custom settings you can use to tweak its operation.
As with normal Django settings, these go in ``settings.py``, or a variant thereof.

SKIP_SOUTH_TESTS
----------------

South has a somewhat fragile test suite, as it has to fiddle with
``INSTALLED_APPS`` at runtime to load in its own testing apps. If the South
tests are failing for you, and you'd rather they be ignored
(by your CI system or similar, in particlar) set this to ``True``.
Defaults to ``False``.

SOUTH_DATABASE_ADAPTER
----------------------

*(Django 1.1 and below)*

If set, overrides the database module South uses for generating DDL commands.
Defaults to ``south.db.<DATABASE_ENGINE>``.

SOUTH_DATABASE_ADAPTERS
-----------------------

*(Django 1.2 and above)*

A dictionary with database aliases as keys and the database module South will
use as values. South defaults to using the internal ``south.db.<ENGINE> modules``.

DATABASE_STORAGE_ENGINE
-----------------------

Only for MySQL. If set, South will tell MySQL to use the given storage engine
for new items.

SOUTH_AUTO_FREEZE_APP
---------------------

When set, South freezes a migration's app and appends it to the bottom of the
migration file (the default behaviour, and required for ``--auto`` to work).
If you want to manually pass in ``--freeze appname`` instead, or just don't
like the clutter, set this to ``False``. Defaults to ``True``.

SOUTH_TESTS_MIGRATE
-------------------

If this is ``False``, South's test runner integration will make the test
database be created using syncdb, rather than via migrations (the default).
Set this to ``False`` if you have migrations which take too long to migrate
every time tests run, but be wary if you rely on migrations to do special things.
Defaults to ``True`` in 0.7 and above, ``False`` in 0.6 and below.

SOUTH_LOGGING_ON
----------------

If this is True the SQL run by South is logged to a file.
You must also set ``SOUTH_LOGGING_FILE`` to a valid file that you want to log to.

SOUTH_LOGGING_FILE
------------------

See SOUTH_LOGGING_ON for more info.

A sample setting would be::

 SOUTH_LOGGING_FILE = os.path.join(os.path.dirname(__file__),"south.log")

 
.. _setting-south-migration-modules: 
 
SOUTH_MIGRATION_MODULES
-----------------------

*(South 0.7 and higher)*

A dictionary of alternative migration modules for apps. By default, apps look
for their migrations in "<appname>.migrations", but you can override this here,
if you have project-specific migrations sets.

Example::

 SOUTH_MIGRATION_MODULES = {
     'books': 'myproject.migrations.books',
 }
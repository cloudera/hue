Fixtures
========

A few things change when you're using fixtures with South.

initial_data
------------

Much like syncdb, South will load the initial_data fixture when an app has been
successfully migrated to the latest migration for an app. Note that the data in
the fixture will not be available before then; South only applies it at the end,
as it may not match the current database schema.

Fixtures from migrations
------------------------

If you need to load a fixture as part of your database setup - say, you have a
migration that depends on it being around - the best thing to do is to write a
new migration to load the fixture in. That way, the fixture will always be
loaded at the correct time.

To make such a migration, first make a blank migration::

 ./manage.py startmigration appname load_myfixture

Then, open the new migration file, and restructure your forwards() method
so it looks like this::

    def forwards(self, orm):
        from django.core.management import call_command
        call_command("loaddata", "my_fixture.json")
 
(you'll have to leave backwards() empty,
as there's no much you can do to reverse this).

Then, when this migration is run, it will load the given fixture.
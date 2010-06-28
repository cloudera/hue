
.. _converting-an-app:

Converting An App
=================

Converting an app to use South is very easy:

 - Edit your settings.py and put 'south' into `INSTALLED_APPS`
   (assuming you've installed it to the right place)
 
 - Run ``./manage.py syncdb`` to load the South table into the database.
   Note that syncdb looks different now - South modifies it.

 - Run ``./manage.py convert_to_south myapp`` - South will automatically make and
   pretend to apply your first migration.
 
Converting other installations and servers
------------------------------------------

The convert_to_south command only works entirely on the first machine you run it
on. Once you've committed the initial migrations it made into the database,
you'll have to run ``./manage.py migrate myapp 0001 --fake`` on every machine that
has a copy of the codebase (make sure they were up-to-date with models and
schema first).

Remember that new installations of the codebase after this don't need these
steps; you need only do a syncdb then a normal migrate.

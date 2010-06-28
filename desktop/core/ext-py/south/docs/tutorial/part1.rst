
.. _tutorial-part-1:

Part 1: The Basics
==================

Welcome to the South tutorial; here, we'll try and cover all the basic usage of
South, as well as giving you some general hints about what else to do.

If you've never heard of the idea of a migrations library, then please read
:ref:`what-are-migrations` first; that will help you get a better understanding
of what both South (and others, such as django-evolution) are trying to achieve.

This tutorial assumes you have South installed correctly; if not, see the
:ref:`installation instructions <installation>`.

Starting off
------------

In this tutorial, we'll follow the process of using migrations on a brand new
app. Don't worry about converting your existing apps; we'll cover that in the
next part.

The first thing to note is that South is per-application; migrations are stored
along with the app's code [#]_. If an app doesn't have any migrations defined,
South will ignore it, and it will behave as normal (that is, using syncdb).

.. [#] You can also :ref:`store them elsewhere <setting-south-migration-modules>` if you like.

So, find a project to work in (or make a new one, and set it up with a database
and other settings), and let's create our new app::

 ./manage.py startapp southtut
 
As usual, this should make a new directory ``southtut/``. First, add it to
``INSTALLED_APPS``, then open up the newly-created ``southtut/models.py``,
and create a new model::

 from django.db import models

 class Knight(models.Model):
     name = models.CharField(max_length=100)
     of_the_round_table = models.BooleanField()

It's quite simple, but it'll do. Now, instead of running ``syncdb`` to create
a table for the model in our database, we'll create a migration for it.

The First Migration
-------------------

South has several ways of creating migrations; some are automatic, some are
manual. As a basic user, you'll probably use the two automatic ways - ``--auto``
and ``--initial``.

``--auto`` looks at the previous migration, works out what's changed, and
creates a migration which applies the differences - for example, if you add a
field to a model, ``--auto`` will notice this, and make a migration which
creates a new column for that field on its model's table.

However, you'll notice that ``--auto`` needs a previous migration - our new
app doesn't have one. Instead, in this case, we need to use ``--initial``, which
will create tables and indexes for all of the models in the app; it's what you
use first, much like ``syncdb``, and ``--auto`` is then used afterwards for
each change.

So, let's create our first migration::

 $ ./manage.py schemamigration southtut --initial
 Creating migrations directory at '/home/andrew/Programs/litret/southtut/migrations'...
 Creating __init__.py in '/home/andrew/Programs/litret/southtut/migrations'...
  + Added model southtut.Knight
 Created 0001_initial.py. You can now apply this migration with: ./manage.py migrate southtut
 
As you can see, that's created a migrations directory for us, and made a new
migration inside it. All we need to do now is apply our new migration::

 $ ./manage.py migrate southtut
  Running migrations for southtut:
  - Migrating forwards to 0001_initial.
  > southtut:0001_initial
  - Loading initial data for southtut.

With that, South has created the new table for our model; check if you like, and
try adding a few Knights using ``./manage.py shell``.


Changing the model
------------------

So far, we've done nothing that ``syncdb`` couldn't accomplish; time to change
that (or rather, our model). Let's add another field to our model::

 from django.db import models

 class Knight(models.Model):
     name = models.CharField(max_length=100)
     of_the_round_table = models.BooleanField()
     dances_whenever_able = models.BooleanField()

Now, if we weren't using migrations, making this new column appear on our
``southtut_knight`` table would be annoying at best. However, with South, we
need only do two, quick steps: make a migration for the change, then apply it.

First, make the new migration, using the --auto feature::

 $ ./manage.py schemamigration southtut --auto
  + Added field dances_whenever_able on southtut.Knight
 Created 0002_auto__add_field_knight_dances_whenever_able.py. You can now apply this migration with: ./manage.py migrate southtut
 
*(Notice that South has automatically picked a name for this migration; you
can instead give migrations custom names by providing it as another argument)*

Now, apply it::

 $ ./manage.py migrate southtut
 Running migrations for southtut:
  - Migrating forwards to 0002_auto__add_field_knight_dances_whenever_able.
  > southtut:0002_auto__add_field_knight_dances_whenever_able
  - Loading initial data for southtut.

With that, our new column is created; again, go and check, you'll be able to
add Knights who can dance whenever they're able.

Once you're happy with this basic usage of South, move on to
:ref:`tutorial-part-2`.
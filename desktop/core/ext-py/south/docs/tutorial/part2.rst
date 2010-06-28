
.. _tutorial-part-2:

Part 2: Advanced Changes
========================

Now you've done a simple change to the model, let's look at some of the more
advanced changes you can do with South.

.. _tutorial-part-2-defaults:

Defaults
--------

Firstly, let's deal with more tricky column types. In the previous part, we
added a ``BooleanField`` to the table - this is easy for a database to handle,
as it has a default value (of ``False``) specified, so that's the value that
gets used for the column in all of the existing rows.

However, some columns don't have a default defined. If the column is nullable -
that is, ``null=True`` - then the existing rows will have NULL in the new
column. Otherwise, if you've given no default, but the column is ``NOT NULL``
(i.e. ``null=False``, the default), there's no value the database can put in
the new column, and so you won't be able to reliably add the column [#]_.

.. [#] Some database backends will let you add the column anyway if the table
       is empty, while some will refuse outright in this scenario.
       
If South detects such a situation, it will pop up and ask you what to do; let's
make it do so.

First, change your model to add a new field that has no default, but is also
not nullable::

 from django.db import models

 class Knight(models.Model):
     name = models.CharField(max_length=100)
     of_the_round_table = models.BooleanField()
     dances_whenever_able = models.BooleanField()
     shrubberies = models.IntegerField(null=False)

Now, let's try and get South to automatically generate a migration for that::

 ./manage.py schemamigration southtut --auto
  ? The field 'Knight.shrubberies' does not have a default specified, yet is NOT NULL.
  ? Since you are adding or removing this field, you MUST specify a default
  ? value to use for existing rows. Would you like to:
  ?  1. Quit now, and add a default to the field in models.py
  ?  2. Specify a one-off value to use for existing columns now
  ? Please select a choice:

South presents you with two options; if you select choice one, the command will
quit without doing anything, and you should edit your ``models.py`` and add a
default to the new field.

If you select choice two, you'll get a Python prompt, where you should enter the
default value you want to use for this migration. The default you enter will
only ever be used for the currently-existing rows - this is a good option if
you don't want the field on your model to have a default value.

We'll select choice two, and use ``0`` as our default (it is an IntegerField,
after all)::

  ? Please select a choice: 2
  ? Please enter Python code for your one-off default value.
  ? The datetime module is available, so you can do e.g. datetime.date.today()
  >>> 0
  + Added field shrubberies on southtut.Knight
 Created 0003_auto__add_field_knight_shrubberies.py. You can now apply this migration with: ./manage.py migrate southtut
 
If you look at the generated migration, you'll see that there's a default
specified for the new field, so your database won't cry. Finish off by running
the migration::

 $ ./manage.py migrate southtut
 Running migrations for southtut:
  - Migrating forwards to 0003_auto__add_field_knight_shrubberies.
  > southtut:0003_auto__add_field_knight_shrubberies
  - Loading initial data for southtut.


Uniques
-------

As well as detecting new fields (and also ones you've removed), South also
detects most changes to fields, including changing their ``unique`` attributes.

First, let's make our Knights have unique names::

 from django.db import models

 class Knight(models.Model):
     name = models.CharField(max_length=100, unique=True)
     of_the_round_table = models.BooleanField()
     dances_whenever_able = models.BooleanField()
     shrubberies = models.IntegerField(null=False)
 
Run the automatic migration creator::

 $ ./manage.py schemamigration --auto southtut
  + Added unique constraint for ['name'] on southtut.Knight
 Created 0004_auto__add_unique_knight_name.py. You can now apply this migration with: ./manage.py migrate southtut
 
As you can see, it's detected the change in ``unique``; you can now apply it::

 $ ./manage.py migrate southtut
 Running migrations for southtut:
  - Migrating forwards to 0004_auto__add_unique_knight_name.
  > southtut:0004_auto__add_unique_knight_name
  - Loading initial data for southtut.

South also detects changes to ``unique_together`` in your model's ``Meta`` in
the same way.


ManyToMany fields
-----------------

South should automatically detect ManyToMany fields; when you add the field,
South will create the table the ManyToMany represents, and when you remove the
field, the table will be deleted.

The one exception to this is when you have a 'through model' (i.e. you're using
the ``through=`` option) - since the table for the model is already created when
the model is detected, South does nothing with these types of ManyToMany fields.

Custom fields
-------------

If you've looked closely at the migration files, you'll see that South stores
field definitions by storing their class, and the arguments that need to be
passed to the field's constructor.

Since Python offers no way to get the arguments used in a class' constructor
directly, South uses something called the *model introspector* to work out
what arguments fields were passed. This knows what variables the arguments
are stored into on the field, and using this knowledge, can reconstruct the
arguments directly.

Because custom fields (either those written by you, or included with third-party
apps) are all different, South can't work out how to get their arguments without
extra help, so if you try to add, change or remove custom fields, South will
bail out and say that you need to give it rules for your custom fields; this
topic is covered in detail in :ref:`custom-fields`.

More?
-----

South supports most operations you'll do on your models day-to-day; if you're
interested, there's a :ref:`full list of what the autodetector supports
<autodetector-supported-actions>`.

You'll probably want to read :ref:`tutorial-part-3` next.

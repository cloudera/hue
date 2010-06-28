
.. _autodetector:

The Autodetector
================

The autodetector is the part of South you'll probably be using the most, as well
as being the feature that people seem to like the most.

The general use of the autodetector is covered in :ref:`tutorial-part-1`; this
is more of a reference of what it's capable of.

When the autodetector runs, it compares your current models with those frozen
in your most recent migration on the app, and if it finds any changes, yields
one or more Actions to the South migration-file-writer.

.. _autodetector-supported-actions:

Supported Actions
-----------------

Model creation and deletion
^^^^^^^^^^^^^^^^^^^^^^^^^^^

South will happily detect the creation and deletion of models; this is the
oldest and most well-worn feature of the autodetector, and so has very few
caveats.

One thing to note is that, while South calls the post_syncdb hook on your
models (much like ``syncdb`` does), it calls it when it initially creates the
table, not at the end of the migration, so your hook might well get called
when the model doesn't have its full table.

Consider moving your hook code into its own data migration, or use one of
our own :ref:`signals`.


Field addition and removal
^^^^^^^^^^^^^^^^^^^^^^^^^^

South detects addition and removal of fields fine, and should correctly create
indexes and constraints for new fields.

Note that when you add or remove a field, you need a default specified; there's
more explanation on this in the :ref:`tutorial-part-2-defaults` part of the
tutorial.


Field changes
^^^^^^^^^^^^^

South will detect if you change a field, and should correctly change the field
type, with one exception:

 - If you alter to a field with a CHECK constraint (e.g. ``PositiveIntegerField``)
   the constraint won't be added to the column (it is removed if you alter away,
   however). This will be fixed in a future release.


ManyToMany addition and removal
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ManyToMany fields are detected on addition and removal; when you add the field,
South will create the table the ManyToMany represents, and when you remove the
field, the table will be deleted.

The one exception to this is when you have a 'through model' (i.e. you're using
the ``through=`` option) - since the table for the model is already created when
the model is detected, South does nothing with these types of ManyToMany fields.


Unique changes
^^^^^^^^^^^^^^

If you change the ``unique=`` attribute on a field, or the ``unique_together``
in a model's Meta, South will detect and change the constraints on the database
accordingly (except on SQLite, where we don't get have the code to edit UNIQUE
constraints).




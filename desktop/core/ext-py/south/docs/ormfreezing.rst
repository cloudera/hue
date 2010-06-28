
.. _orm-freezing:

ORM Freezing
============

South freezes the state of the ORM and models whenever you do a migration,
meaning that when your migrations run in the future, they see the models and
fields they're expecting (the ones that were around when they were created),
rather than the current set (which could be months or even years newer).

This is accomplished by serialising the models into a large dictionary called
``models`` at the bottom of every migration. It's easy to see; it's the large
chunk of dense code at the bottom.

Rationale behind the serialisation
----------------------------------

South doesn't freeze every aspect of a model; for example, it doesn't
preserve new managers, or custom model methods, as these would require
serialising the python code that runs those method (and the code that depends on,
and so forth).

If you want custom methods in your migration, you'll have to copy the code in,
including any imports it relies on to work.
Remember, however, for every import that you add, you're promising to keep
that import valid for the life for the migration.

We also use a human-readable format that's easy to change; since South relies
on the frozen models not only for reacreating the ORM but also for detecting
changes, it's really useful to be able to edit them now and again (and also
serves as a valuable debugging tool if you attach failing migrations to a
ticket).

Serialisation format
--------------------

``models`` is a dict of ``{'appname.modelname': fields}``, and ``fields`` is a
dict of ``{'fieldname': (fieldclass, positional_args, kwd_args)}``. ``'Meta'``
is also a valid entry in fields, in which case the value should be a dict
of its attributes.

Make note that the entries in positional_args and kwd_args are
**strings passed into eval**; thus, a string would be ``'"hello"'``.
We strongly recommend you use schemamigration/datamigration to freeze things.

Accessing the ORM
-----------------

From inside a migration, you can access models from the frozen ORM in two ways.
If the model you're accessing is part of the same app, you can simply call::

 orm.ModelName
 
Otherwise, you'll need to specify the app name as well, using::

 orm['myapp.ModelName']
 
For example, if you wanted to get a user with ID 1, you could use::

 orm['auth.User'].objects.get(id=1)
 
Note that you can only access models that have been frozen; South automatically
includes anything that could be reaches via foreign keys or many-to-many
relationships, but if you want to add other models in, simply pass ``--freeze appname``
to the ``./manage.py datamigration`` command.
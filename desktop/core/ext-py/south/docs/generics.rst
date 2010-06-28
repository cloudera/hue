Generic Relations
=================

Generic relations' fields are be frozen, but unfortunately
not the GenericForeignKey itself (see :ref:`orm-freezing` for a reason why).
To add it back onto a model, add the import
for generic at the top of the migration and then in the body of forwards() put::

    gfk = generic.GenericForeignKey()
    gfk.contribute_to_class(orm.FooModel, "object_link")

This will add the GenericForeignKey onto the model as model.object_link.
You can pass the optional content_type and id field names into the
constructor as usual.

Also, be careful when using ContentType; make sure to use the frozen
orm['contenttypes.ContentType'], and don't import it directly,
otherwise comparisons may fail.
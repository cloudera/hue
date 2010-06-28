
.. _custom-fields:

Custom Fields
=============

The Problem
-----------

South stores field definitions by storing both their class and the arguments that
need to be passed to the field's constructor, so it can recreate the field
instance simply by calling the class with the stored arguments.

However, since Python offers no way to get the arguments used in a class'
constructor directly, South uses something called the *model introspector* to
work out what arguments fields were passed. This knows what variables the
arguments are stored into on the field, and using this knowledge, can
reconstruct the arguments directly.

This isn't the case for custom fields [#]_, however; South has never seen them
before, and it can't guess at which variables mean what arguments, or what
arguments are even needed; it only knows the rules for Django's internal fields
and those of common third-party apps (those which are either South-aware, or
which South ships with a rules module for, such as django-tagging).

.. [#] 'Custom Fields' in this context refers to any field that is not part
       of Django's core. GeoDjango fields are part of the core, but ones in
       third-party apps are 'custom'. Note also that a field is considered
       custom even if it inherits directly from a core field and doesn't
       override anything; there's no way for South to reliably tell that it does
       so.

The Solution
------------

There are two ways to tell South how to work with a custom field; if it's
similar in form to other fields (in that it has a set type and a few options)
you'll probably want to :ref:`extend South's introspection rules
<extending-introspection>`.

However, if it's particularly odd - such as a field which takes fields as
arguments, or dynamically changes based on other factors - you'll probably find
it easier to :ref:`add a south_field_triple method <south-field-triple>`.


.. _extending-introspection:

Extending Introspection
=======================

(Note: This is also featured in the tutorial in :ref:`tutorial-part-4`)

South does the majority of its field introspection using a set of simple rules;
South works out what class a field is, and then runs all rules which have been
defined for either that class or a parent class of it.

This way, all of the common options (such as ``null=``) are defined against the 
main ``Field`` class (which all fields inherit from), while specific options
(such as ``max_length``) are defined on the specific fields they apply to
(in this case, ``CharField``).

If your custom field inherits from a core Django field, and doesn't add any new
attributes, then you probably won't have to add any rules for it, as it will
inherit all those from its parents.

However, South first checks that it has explicitly been told a class is
introspectable first; even though it will probably have rules defined (since it
inherits from Field, at least), there's no way to guarantee that it knows about
all of the possible rules until it has been told so.

Thus, there are two stages to adding support for your custom field to South;
firstly, adding some rules for the new arguments it introduces (or possibly
not adding any), and secondly, adding its field name to the list of patterns
South knows are safe to introspect.

Rules
-----

Rules are what make up the core logic of the introspector; you'll need to pass
South a (possibly empty) list of them. They consist of a tuple, containing:

 - A class or tuple of classes to which the rules apply (remember, the rules
   apply to the specified classes and all subclasses of them).
   
 - Rules for recovering positional arguments, in order of the arguments (you are
   strongly advised not to use this feature, and use keyword argument instead).
 
 - A dictionary of keyword argument rules, with the key being the name of the
   keyword argument, and the value being the rule.

Each rule is itself a list or tuple with two elements:

 - The first element is the name of the attribute the value is taken from - if
   a field stored its max_length argument as ``self.max_length``, say, this
   would be ``"max_length"``.
   
 - The second element is a (possibly empty) dictionary of options describing the
   various different variations on handling of the value.

An example (this is the South rule for the many-to-one relationships in core
Django)::

  rules = [
    (
      (models.ForeignKey, models.OneToOneField),
      [],
      {
          "to": ["rel.to", {}],
          "to_field": ["rel.field_name", {"default_attr": "rel.to._meta.pk.name"}],
          "related_name": ["rel.related_name", {"default": None}],
          "db_index": ["db_index", {"default": True}],
      },
    )
  ]

You'll notice that you're allowed to have dots in the attribute name; ForeignKeys,
for example, store their destination model as ``self.rel.to``, so the attribute
name is ``"rel.to"``.

The various options are detailed below; most of them allow you to specify the
default value for a parameter, so arguments can be omitted for clarity where
they're not necessary.

.. _is-value-keyword:

The one special case is the ``is_value`` keyword; if this is present and True,
then the first item in the list will be interpreted as the actual value, rather
than the attribute path to it on the field. For example::

 "frozen_by_south": [True, {"is_value": True}],

Parameters
^^^^^^^^^^

 - default: The default value of this field (directly as a Python object).
   If the value retrieved ends up being this, the keyword will be omitted
   from the frozen result. For example, the base Field class' "null" attribute
   has {'default':False}, so it's usually omitted, much like in the models.

 - default_attr: Similar to default, but the value given is another attribute
   to compare to for the default. This is used in to_field above, as this
   attribute's default value is the other model's pk name.

 - default_attr_concat: For when your default value is even more complex,
   default_attr_concat is a list where the first element is a format string,
   and the rest is a list of attribute names whose values should be formatted
   into the string.

 - ignore_if: Specifies an attribute that, if it coerces to true, causes this
   keyword to be omitted. Useful for ``db_index``, which has
   ``{'ignore_if': 'primary_key'}``, since it's always True in that case.
 
 - ignore_dynamics: If this is True, any value that is "dynamic" - such as model
   instances - will cause the field to be omitted instead. Used internally
   for the ``default`` keyword.

 - is_value: If present, the 'attribute name' is instead used directly as the
   value. See :ref:`above <is-value-keyword>` for more info.
 
 
Field name patterns
-------------------

The second of the two steps is to tell South that your field is now safe to
introspect (as you've made sure you've added all the rules it needs). 

Internally, South just has a long list of regular expressions it checks fields'
classes against; all you need to do is provide extra arguments to this list.

Example (this is in the GeoDjango module South ships with, and presumes
``rules`` is the rules triple you defined previously)::

 from south.modelsinspector import add_introspection_rules
 add_introspection_rules(rules, ["^django\.contrib\.gis"])
 
Additionally, you can ignore some fields completely if you know they're not
needed. For example, django-taggit has a manager that actually shows up as a
fake field (this makes the API for using it much nicer, but confuses South to no
end). The django-taggit module we ship with contains this rule to ignore it::

 from south.modelsinspector import add_ignored_fields
 add_ignored_fields(["^taggit\.managers"])
 
Where to put the code
---------------------

You need to put the call to ``add_introspection_rules`` somewhere where it will
get called before South runs; it's probably a good choice to have it either in
your ``models.py`` file or the module the custom fields are defined in.

General Caveats
---------------

If you have a custom field which adds other fields to the model dynamically
(i.e. it overrides contribute_to_class and adds more fields onto the model),
you'll need to write your introspection rules appropriately, to make South
ignore the extra fields at migration-freezing time, or to add a flag to your
field which tells it not to make the new fields again. An example can be
found `here <http://bitbucket.org/carljm/django-markitup/src/tip/markitup/fields.py#cl-68>`_.

.. _south-field-triple:

south_field_triple
==================

There are some cases where introspection of fields just isn't enough;
for example, field classes which dynamically change their database column
type based on options, or other odd things.

Note: :ref:`Extending the introspector <extending-introspection>` is often far
cleaner and easier than this method.

The method to implement for these fields is ``south_field_triple()``.

It should return the standard triple of::

 ('full.path.to.SomeFieldClass', ['positionalArg1', '"positionalArg2"'], {'kwarg':'"value"'})

(this is the same format used by the :ref:`ORM Freezer <orm-freezing>`;
South will just use your output verbatim).

Note that the strings are ones that will be passed into eval, so for this
reason, a variable reference would be ``'foo'`` while a string
would be ``'"foo"'``.

Example
-------

Here's an example of this method for django-modeltranslation's TranslationField.
This custom field stores the type it's wrapping in an attribute of itself,
so we'll just use that::

 def south_field_triple(self):
     "Returns a suitable description of this field for South."
     # We'll just introspect the _actual_ field.
     from south.modelsinspector import introspector
     field_class = self.translated_field.__class__.__module__ + "." + self.translated_field.__class__.__name__
     args, kwargs = introspector(self.translated_field)
     # That's our definition!
     return (field_class, args, kwargs)

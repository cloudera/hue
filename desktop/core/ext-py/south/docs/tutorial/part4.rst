
.. _tutorial-part-4:

Part 4: Custom Fields
=====================

South 0.7 introduced a reasonably radical change from previous versions. Before,
if you had a custom field, South would attempt to use magic [#]_ to determine
how to freeze that field, so it could be recreated in a migration.

.. [#] And not very nice magic, either; a combination of regexes and the python
       ``parser`` module.

While this worked surprisingly well for most people, in a small percentage of
cases it would get it completely wrong - even worse, you wouldn't know it was
wrong until things changed a few weeks later. In the interests of both sanity
and having less magic, you must now tell South how to freeze your custom fields.

Don't worry, it's pretty easy, and you only have to do it once per field.

Our Field
---------

In this example, we'll be using a custom field which stores a list of tags in
the database. We'll just store them in a TEXT column, with some delimiter
separating the values (by default, we'll use ``|``, but they can pass in
something else as a keyword argument).

Here's the field class; in my code, I put this in ``appname/fields.py``
(for more on writing custom fields, see the
`Django docs <http://docs.djangoproject.com/en/dev/howto/custom-model-fields/>`_)::

 from django.db import models

 class TagField(models.TextField):

     description = "Stores tags in a single database column."

     __metaclass__ = models.SubfieldBase

     def __init__(self, delimiter="|", *args, **kwargs):
         self.delimiter = delimiter
         super(TagField, self).__init__(*args, **kwargs)
    
     def to_python(self, value):
         # If it's already a list, leave it
         if isinstance(value, list):
             return value
        
         # Otherwise, split by delimiter
         return value.split(self.delimiter)
    
     def get_prep_value(self, value):
         return self.delimiter.join(value)

To tell South about a custom field, you need to tell it two things; that this
particular class is OK to use, and how to reconstruct the keyword arguments
from a Field instance.

Keyword Arguments
-----------------

South freezes fields by storing their class name and module (so it can get the
field class itself) and the keyword arguments you used for that particular
instance (for example, ``CharField(max_length=50)`` is a different database
type to ``CharField(max_length=150)``).

Since Python doesn't store the keyword arguments a class was passed, South has
to reconstruct them using the field instance. For example, we know that
``CharField``'s ``max_length`` attribute is stored as ``self.max_length``, while
``ForeignKeys`` store their ``to`` attribute (the model they point to - also the
first positional argument) as ``self.rel.to``.

South knows all these rules for the core Django fields, but you need to tell it
about your own ones. The good news is that South will trace the inheritance tree
of your field class and add on rules from parent classes it knows about - thus,
you only need tell South about extra keyword arguments you've added, not every
possible argument the field could have.

In our example, we've only specified one extra keyword: ``delimiter``. Here's
the code we'd add for South to work with our new field; I'll explain it in a
minute::

 from south.modelsinspector import add_introspection_rules
 add_introspection_rules([
     (
         [TagField], # Class(es) these apply to
         [],         # Positional arguments (not used)
         {           # Keyword argument
             "delimiter": ["delimiter", {"default": "|"}],
         },
     ),
 ], ["^southtut\.fields\.TagField"])
 
As you can see, to tell South about your new fields, you need to call the
``south.modelsinspector.add_introspection_rules`` function. You should put this
code next to the definition of your field; the last thing you want is for the
field to get imported, but for this code to not run.

``add_introspection_rules`` takes two arguments; a list of rules, and a list of
regular expressions. The regular expressions are used by South to see if a field
is allowed to be introspected; just having a rule that matches it isn't enough,
as rule inheritance means that any custom field class will have at least some
rules on it (as they will inherit from ``Field``, if not something more specific
like ``CharField``), and some custom fields can get by with only those 
inherited rules (more on that shortly).

The first argument is the list of rules. Each rule is a tuple (or list) with
three items:

 - A list of classes these rules apply to. You'll almost certainly have just
   ``[MyField]`` here.
 - Positional argument specification. This should always be left blank, as an
   empty list - ``[]``.
 - Keyword argument specification. This is a dictionary, with the key being the
   name of the keyword argument, and the value being a tuple or list of
   ``(attribute_name, options)``.
   
The attribute name says where the value of the keyword can be found - in our
case, it's ``'delimiter'``, as we stored our keyword in ``self.delimiter``. (If
this was the ``ForeignKey`` rule, we'd put ``'rel.to'`` here)

``options`` is a dictionary. You can safely leave it blank, but to make things
nicer, we can use it to specify the default value of this keyword - if the value
South finds matches this, it will leave out this keyword from the frozen
definition. This helps keep the frozen definitions shorter and more readable.

Simple Inheritance
------------------

If your field inherits directly from another Django field - say ``CharField`` -
and doesn't add any new keyword arguments, there's no need to have any rules
in your ``add_introspection_rules``; you can just tell South that the field
is alright as it is::

 class UpperCaseField(models.TextField):
     "Makes sure its content is always upper-case."
     
     def to_python(self, value):
         return value.upper()
     
     def get_prep_value(self, value):
         return value.upper()
     
 from south.modelsinspector import add_introspection_rules
 add_introspection_rules([], ["^southtut\.fields\.UpperCaseField"])
 
More Information
----------------

There's more documentation on this subject, and on all the possible options,
in the :ref:`extending-introspection` section.
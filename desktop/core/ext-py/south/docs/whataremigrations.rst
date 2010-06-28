
.. _what-are-migrations:

What are migrations?
====================

For the uninitiated, migrations (also known as 'schema evolution' or
'mutations') are a way of changing your database schema from one version into
another. Django by itself can only do this by adding new models, but nearly all
projects will find themselves changing other aspects of models - be it adding a
new field to a model, or changing a database column to have null=True.

South, and other solutions, provide a way of getting round this by giving you
the tools to easily and predictably upgrade your database schema. You write
migrations, which tell South how to upgrade from one version to the next, and by
stringing these migrations together you can move forwards (or backwards) through
the history of your database schema.

In South, the migrations also form the way of creating your database initially
- the first migration simply migrates from an empty schema to your first tables.
This way, running through all the migrations brings your database up-to-date
with the most current version of the app, and if you already have an older
version, you simply need to run through the ones that appeared since last time.

Running through the :ref:`tutorial <tutorial-part-1>` will give you a good
idea of how migrations work and how they're useful to you, with some
solid examples.
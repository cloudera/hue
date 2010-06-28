.. _about:

About South
===========

South brings migrations to Django applications. Its main objectives are to
provide a simple, stable and database-independent migration layer to prevent
all the hassle schema changes over time bring to your Django applications.

We try to make South both as easy-to-use and intuitive as possible, by making it
automate most of your schema-changing tasks, while at the same time providing a
powerful set of tools for large or complex projects; you can easily write your
own migrations by hand, or even use the database altering API directly.

While South started as a relative unknown in the Django database-schema-altering
world, it has slowly risen in popularity and is now widely regarded as the most
popular schema migration tool for Django.

Key features
------------

South has a few key features:

 - Automatic migration creation: South can see what's changed in your models.py
   file and automatically write migrations that match your changes.
 - Database independence: As far as possible, South is completely
   database-agnostic, supporting five different database backends.
 - App-savvy: South knows and works with the concept of Django apps, allowing
   you to use migrations for some of your apps and leave the rest to carry on
   using syncdb.
 - VCS-proof: South will notice if someone else commits migrations to the same
   app as you and they conflict.

A brief history
---------------

South was originally developed at `Torchbox <http://www.torchbox.com>`_ in 2008,
when no existing solution provided the workflow and features that were needed.
It was open-sourced shortly thereafter, and quickly gained steam after the
Schema Evolution panel at DjangoCon 2008.

Sometime in 2009, it became the most popular of the various migration
alternatives, and seems to have been going strong ever since. While there have
been growing calls to integrate South, or something like it, into Django itself,
such an integration has not yet been made, mostly due to the relative
immaturity of database migration solutions.

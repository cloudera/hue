===========
django-nose
===========

.. image:: https://img.shields.io/pypi/v/django-nose.svg
    :alt: The PyPI package
    :target: https://pypi.python.org/pypi/django-nose

.. image:: https://img.shields.io/travis/django-nose/django-nose/master.svg
    :alt: TravisCI Build Status
    :target: https://travis-ci.org/django-nose/django-nose

.. image:: https://img.shields.io/coveralls/django-nose/django-nose/master.svg
    :alt: Coveralls Test Coverage
    :target: https://coveralls.io/r/django-nose/django-nose?branch=master

.. Omit badges from docs

**django-nose** provides all the goodness of `nose`_ in your Django tests, like:

  * Testing just your apps by default, not all the standard ones that happen to
    be in ``INSTALLED_APPS``
  * Running the tests in one or more specific modules (or apps, or classes, or
    folders, or just running a specific test)
  * Obviating the need to import all your tests into ``tests/__init__.py``.
    This not only saves busy-work but also eliminates the possibility of
    accidentally shadowing test classes.
  * Taking advantage of all the useful `nose plugins`_

.. _nose: https://nose.readthedocs.io/en/latest/
.. _nose plugins: http://nose-plugins.jottit.com/

It also provides:

  * Fixture bundling, an optional feature which speeds up your fixture-based
    tests by a factor of 4
  * Reuse of previously created test DBs, cutting 10 seconds off startup time
  * Hygienic TransactionTestCases, which can save you a DB flush per test
  * Support for various databases. Tested with MySQL, PostgreSQL, and SQLite.
    Others should work as well.

django-nose requires nose 1.2.1 or later, and the `latest release`_ is
recommended.  It follows the `Django's support policy`_, supporting:

  * Django 1.8 (LTS) with Python 2.7, 3.4, or 3.5
  * Django 1.9 with Python 2.7, 3.4, or 3.5
  * Django 1.10 with Python 2.7, 3.4, or 3.5
  * Django 1.11 (LTS) with Python 2.7, 3.4, 3.5, or 3.6

.. _latest release: https://pypi.python.org/pypi/nose
.. _Django's support policy: https://docs.djangoproject.com/en/1.8/internals/release-process/#supported-versions

Development
-----------
:Code:   https://github.com/django-nose/django-nose
:Issues: https://github.com/django-nose/django-nose/issues?state=open
:Docs:   https://django-nose.readthedocs.io

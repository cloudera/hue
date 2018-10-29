Upgrading Django
================

Upgrading from Django <= 1.3 to Django 1.4
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In versions of Django < 1.4 the project folder was in fact a python package as
well (note the __init__.py in your project root). In Django 1.4, there is no
such file and thus the project is not a python module.

**When you upgrade your Django project to the Django 1.4 layout, you need to
remove the __init__.py file in the root of your project (and move any python
files that reside there other than the manage.py) otherwise you will get a
`ImportError: No module named urls` exception.**

This happens because Nose will intelligently try to populate your sys.path, and
in this particular case includes your parent directory if your project has a
__init__.py file (see: https://github.com/nose-devs/nose/blob/release_1.1.2/nose/importer.py#L134).

This means that even though you have set up your directory structure properly and
set your `ROOT_URLCONF='my_project.urls'` to match the new structure, when running
django-nose's test runner it will try to find your urls.py file in `'my_project.my_project.urls'`.


Upgrading from Django < 1.2
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Django 1.2 switches to a `class-based test runner`_. To use django-nose
with Django 1.2, change your ``TEST_RUNNER`` from ``django_nose.run_tests`` to
``django_nose.NoseTestSuiteRunner``.

``django_nose.run_tests`` will continue to work in Django 1.2 but will raise a
warning. In Django 1.3, it will stop working.

If you were using ``django_nose.run_gis_tests``, you should also switch to
``django_nose.NoseTestSuiteRunner`` and use one of the `spatial backends`_ in
your ``DATABASES`` settings.

.. _class-based test runner: http://docs.djangoproject.com/en/dev/releases/1.2/#function-based-test-runners
.. _spatial backends: http://docs.djangoproject.com/en/dev/ref/contrib/gis/db-api/#id1

Django 1.1
~~~~~~~~~~

If you want to use django-nose with Django 1.1, use
https://github.com/django-nose/django-nose/tree/django-1.1 or
http://pypi.python.org/pypi/django-nose/0.0.3.

Django 1.0
~~~~~~~~~~

django-nose does not support Django 1.0.

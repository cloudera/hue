django-timezone-field
=====================

.. image:: https://img.shields.io/travis/mfogel/django-timezone-field/develop.svg
   :target: https://travis-ci.org/mfogel/django-timezone-field/

.. image:: https://img.shields.io/coveralls/mfogel/django-timezone-field/develop.svg
   :target: https://coveralls.io/r/mfogel/django-timezone-field/

.. image:: https://img.shields.io/pypi/dm/django-timezone-field.svg
   :target: https://pypi.python.org/pypi/django-timezone-field/

A Django app providing database and form fields for `pytz`__ timezone objects.

Examples
--------

Database Field
~~~~~~~~~~~~~~

.. code:: python

    import pytz
    from django.db import models
    from timezone_field import TimeZoneField

    class MyModel(models.Model):
        timezone1 = TimeZoneField(default='Europe/London') # defaults supported
        timezone2 = TimeZoneField()
        timezone3 = TimeZoneField()

    my_inst = MyModel(
        timezone1='America/Los_Angeles',    # assignment of a string
        timezone2=pytz.timezone('Turkey'),  # assignment of a pytz.DstTzInfo
        timezone3=pytz.UTC,                 # assignment of pytz.UTC singleton
    )
    my_inst.full_clean()  # validates against pytz.common_timezones
    my_inst.save()        # values stored in DB as strings

    tz = my_inst.timezone1  # values retrieved as pytz objects
    repr(tz)                # "<DstTzInfo 'America/Los_Angeles' PST-1 day, 16:00:00 STD>"


Form Field
~~~~~~~~~~

.. code:: python

    from django import forms
    from timezone_field import TimeZoneFormField

    class MyForm(forms.Form):
        timezone = TimeZoneFormField()

    my_form = MyForm({
        'timezone': 'America/Los_Angeles',
    })
    my_form.full_clean()  # validates against pytz.common_timezones

    tz = my_form.cleaned_data['timezone']  # values retrieved as pytz objects
    repr(tz)                               # "<DstTzInfo 'America/Los_Angeles' PST-1 day, 16:00:00 STD>"


Installation
------------

#.  From `pypi`__ using `pip`__:

    .. code:: sh

        pip install django-timezone-field

#.  Add `timezone_field` to your `settings.INSTALLED_APPS`__:

    .. code:: python

        INSTALLED_APPS = (
            ...
            'timezone_field',
            ...
        )

Changelog
------------

*   3.0 (2018-09-15)

    *   Support django 1.11, 2.0, 2.1
    *   Add support for python 3.7
    *   Change default human-readable timezone names to exclude underscores
        (`#32`__ & `#37`__)


*   2.1 (2018-03-01)

    *   Add support for django 1.10, 1.11
    *   Add support for python 3.6
    *   Add wheel support
    *   Support bytes in DB fields (`#38`__ & `#39`__)

*   2.0 (2016-01-31)

    *   Drop support for django 1.7, add support for django 1.9
    *   Drop support for python 3.2, 3.3, add support for python 3.5
    *   Remove tests from source distribution

*   1.3 (2015-10-12)

    *   Drop support for django 1.6, add support for django 1.8
    *   Various `bug fixes`__

*   1.2 (2015-02-05)

    *   For form field, changed default list of accepted timezones from
        `pytz.all_timezones` to `pytz.common_timezones`, to match DB field
        behavior.

*   1.1 (2014-10-05)

    *   Django 1.7 compatibility
    *   Added support for formating `choices` kwarg as `[[<str>, <str>], ...]`,
        in addition to previous format of `[[<pytz.timezone>, <str>], ...]`.
    *   Changed default list of accepted timezones from `pytz.all_timezones` to
        `pytz.common_timezones`. If you have timezones in your DB that are in
        `pytz.all_timezones` but not in `pytz.common_timezones`, this is a
        backward-incompatible change. Old behavior can be restored by
        specifying `choices=[(tz, tz) for tz in pytz.all_timezones]` in your
        model definition.

*   1.0 (2013-08-04)

    *   Initial release as `timezone_field`.


Running the Tests
-----------------

#.  Install `tox`__.

#.  From the repository root, run

    .. code:: sh

        tox

    Postgres will need to be running locally, and sqlite will need to be
    installed in order for tox to do its job.

Found a Bug?
------------

To file a bug or submit a patch, please head over to `django-timezone-field on github`__.

Credits
-------

Originally adapted from `Brian Rosner's django-timezones`__. The full list of contributors is available on `github`__.


__ http://pypi.python.org/pypi/pytz/
__ http://pypi.python.org/pypi/django-timezone-field/
__ http://www.pip-installer.org/
__ https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
__ https://github.com/mfogel/django-timezone-field/issues/32
__ https://github.com/mfogel/django-timezone-field/issues/37
__ https://github.com/mfogel/django-timezone-field/issues/38
__ https://github.com/mfogel/django-timezone-field/issues/39
__ https://github.com/mfogel/django-timezone-field/issues?q=milestone%3A1.3
__ https://tox.readthedocs.org/
__ https://github.com/mfogel/django-timezone-field/
__ https://github.com/brosner/django-timezones/
__ https://github.com/mfogel/django-timezone-field/graphs/contributors

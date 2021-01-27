Changelog
=========

1.0.3 (2019-03-3)
-----------------

Packaging metadata updates:

* Update tox configuration to match Django Python support map

* Drop support for Django 1.8, 1.9 and 1.10
* Drop support for python 3.3

* Confirm support for Django 1.11, 2.0 and 2.1
* Confirm support for python 3.7

1.0.2 (2016-04-19)
------------------

* Minor fixes to test setup

* Update supported Django and Python versions, in line with Django's
  own supported versions.


1.0 (2015-02-15)
----------------

.. note::

    This app precedes Django's own AppConfig_ classes that act as
    "objects [to] store metadata for an application" inside Django's
    app loading mechanism. In other words, they solve a related but
    different use case than django-appconf and can't easily be used
    as a replacement. The similarity in name is purely coincidental.

* Dropped support of Python 2.5.

* Added support for Django 1.7 and 1.8.

* Modernized test setup.

.. _AppConfig: https://docs.djangoproject.com/en/stable/ref/applications/#django.apps.AppConfig

0.6 (2013-01-28)
----------------

* Added ``required`` attribute to ``Meta`` to be able to specify which
  settings are required to be set.

* Moved to Travis for the tests: http://travis-ci.org/jezdez/django-appconf

* Stopped support for Django 1.2.X.

* Introduced support for Python >= 3.2.

0.5 (2012-02-20)
----------------

* Install as a package instead of a module.

* Refactored tests to use `django-jenkins`_ for `enn.io`_'s `CI server`_.

.. _`django-jenkins`: https://github.com/kmmbvnr/django-jenkins
.. _`enn.io`: http://enn.io
.. _`CI server`: https://ci.enn.io/job/django-appconf/

0.4.1 (2011-09-09)
------------------

* Fixed minor issue in installation documentation.

0.4 (2011-08-24)
----------------

* Renamed ``app_label`` attribute of the inner ``Meta`` class to ``prefix``.
  The old form ``app_label`` will work in the meantime.

* Added ``holder`` attribute to the inner ``Meta`` class to be able to
  specify a custom "global" setting holder. Default: "'django.conf.settings'"

* Added ``proxy`` attribute to the inner ``Meta`` class to enable proxying
  of ``AppConf`` instances to the settings holder, e.g. the global Django
  settings.

* Fixed issues with ``configured_data`` dictionary available in the
  ``configure`` method of ``AppConf`` classes with regard to subclassing.

0.3 (2011-08-23)
----------------

* Added tests with 100% coverage.

* Added ability to subclass ``Meta`` classes.

* Fixed various bugs with subclassing and configuration in subclasses.

0.2.2 (2011-08-22)
------------------

* Fixed another issue in the ``configure()`` API.

0.2.1 (2011-08-22)
------------------

* Fixed minor issue in ``configure()`` API.

0.2 (2011-08-22)
----------------

* Added ``configure()`` API to ``AppConf`` class which is called after
  configuring each setting.

0.1 (2011-08-22)
----------------

* First public release.

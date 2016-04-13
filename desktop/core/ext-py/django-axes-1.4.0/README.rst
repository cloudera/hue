Django Axes
===========

.. image:: https://secure.travis-ci.org/django-pci/django-axes.png?branch=master
    :alt: Build Status
    :target: http://travis-ci.org/django-pci/django-axes

``django-axes`` is a very simple way for you to keep track of failed login
attempts, both for the Django admin and for the rest of your site.  The name is
sort of a geeky pun, since ``axes`` can be read interpreted as:

* "access", as in monitoring access attempts
* "axes", as in tools you can use hack (generally on wood).  In this case,
  however, the "hacking" part of it can be taken a bit further: ``django-axes``
  is intended to help you *stop* people from hacking (popular media
  definition) your website.  Hilarious, right?  That's what I thought too!


Requirements
============

``django-axes`` requires Django 1.5 or later. The application is intended to
work around the Django admin and the regular ``django.contrib.auth``
login-powered pages.


Installation
============

You can install the latest stable package running this command::

    $ pip install django-axes

Also you can install the development version running this command::

    $ pip install -e git+http://github.com/django-pci/django-axes.git#egg=django_axes-dev

Development
===========

You can contribute to this project forking it from github and sending pull requests.

Running tests
-------------

Tests can be run, after you clone the repository and having django installed, like::

    $ PYTHONPATH=$PYTHONPATH:$PWD django-admin.py test axes --settings=axes.test_settings


Configuration
=============

First of all, you must add this project to your list of ``INSTALLED_APPS`` in
``settings.py``::

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        ...
        'axes',
        ...
    )

Next, install the ``FailedLoginMiddleware`` middleware::

    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'axes.middleware.FailedLoginMiddleware'
    )

Run ``python manage.py syncdb``.  This creates the appropriate tables in your database
that are necessary for operation.

Customizing Axes
----------------

You have a couple options available to you to customize ``django-axes`` a bit.
These should be defined in your ``settings.py`` file.

* ``AXES_LOGIN_FAILURE_LIMIT``: The number of login attempts allowed before a
  record is created for the failed logins.  Default: ``3``
* ``AXES_LOCK_OUT_AT_FAILURE``: After the number of allowed login attempts
  are exceeded, should we lock out this IP (and optional user agent)?
  Default: ``True``
* ``AXES_USE_USER_AGENT``: If ``True``, lock out / log based on an IP address
  AND a user agent.  This means requests from different user agents but from
  the same IP are treated differently.  Default: ``False``
* ``AXES_COOLOFF_TIME``: If set, defines a period of inactivity after which
  old failed login attempts will be forgotten. Can be set to a python
  timedelta object or an integer. If an integer, will be interpreted as a
  number of hours.  Default: ``None``
* ``AXES_LOGGER``: If set, specifies a logging mechanism for axes to use.
  Default: ``'axes.watch_login'``
* ``AXES_LOCKOUT_TEMPLATE``: If set, specifies a template to render when a
  user is locked out. Template receives cooloff_time and failure_limit as
  context variables. Default: ``None``
* ``AXES_LOCKOUT_URL``: If set, specifies a URL to redirect to on lockout. If
  both AXES_LOCKOUT_TEMPLATE and AXES_LOCKOUT_URL are set, the template will
  be used. Default: ``None``
* ``AXES_VERBOSE``: If ``True``, you'll see slightly more logging for Axes.
  Default: ``True``
* ``AXES_USERNAME_FORM_FIELD``: the name of the form field that contains your
  users usernames. Default: ``username``

* ``AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP``: If ``True`` prevents to login
  from IP under particular user if attempts limit exceed, otherwise lock out
  based on IP.
  Default: ``False``


Usage
=====

Using ``django-axes`` is extremely simple.  Once you install the application
and the middleware, all you need to do is periodically check the Access
Attempts section of the admin.

By default, django-axes will lock out repeated attempts from the same IP
address.  You can allow this IP to attempt again by deleting the relevant
``AccessAttempt`` records in the admin.

You can also use the ``axes_reset`` management command using Django's
``manage.py``.

* ``manage.py axes_reset`` will reset all lockouts and access records.
* ``manage.py axes_reset ip`` will clear lockout/records for ip

In your code, you can use ``from axes.utils import reset``.

* ``reset()`` will reset all lockouts and access records.
* ``reset(ip=ip)`` will clear lockout/records for ip
* ``reset(username=username)`` will clear lockout/records for username

Issues
======

Not being locked out after failed attempts
------------------------------------------

You may find that Axes is not capturing your failed login attempts. It may be that you need to manually add watch_login to your login url.
For example, in your urls.py::

    ...
    from django.contrib.auth.views import login, logout, password_change
    from axes.decorators import watch_login
    ...
    urlpatterns = patterns('',
        (r'^login/$', watch_login(login), {'template_name': 'auth/login.html'}),
    ...


Locked out without reason
-------------------------

It may happen that you have suddenly become locked out without a single failed
attempt. One possible reason is that you are using some custom login form and the
username field is named something different than "username", e.g. "email". This
leads to all users attempts being lumped together. To fix this add the following
to your settings:

    AXES_USERNAME_FORM_FIELD = "email"

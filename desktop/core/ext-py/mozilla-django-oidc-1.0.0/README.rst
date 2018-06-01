===================
mozilla-django-oidc
===================

.. image:: https://badge.fury.io/py/mozilla-django-oidc.svg
   :target: https://badge.fury.io/py/mozilla-django-oidc

.. image:: https://travis-ci.org/mozilla/mozilla-django-oidc.svg?branch=master
   :target: https://travis-ci.org/mozilla/mozilla-django-oidc

.. image:: https://codecov.io/gh/mozilla/mozilla-django-oidc/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/mozilla/mozilla-django-oidc

.. image:: https://circleci.com/gh/mozilla/mozilla-django-oidc/tree/master.svg?style=svg
   :target: https://circleci.com/gh/mozilla/mozilla-django-oidc/tree/master

A lightweight authentication and access management library for integration with OpenID Connect enabled authentication services.


Documentation
-------------

The full documentation is at `<https://mozilla-django-oidc.readthedocs.io>`_.


Running Unit Tests
-------------------

Use ``tox`` to run as many different versions of Python you have. If you
don't have ``tox`` installed (and executable) already you can either
install it in your system Python or `<https://pypi.python.org/pypi/pipsi>`_.
Once installed, simply execute in the project root directory.

.. code-block:: shell

    $ tox

``tox`` will do the equivalent of installing virtual environments for every
combination mentioned in the ``tox.ini`` file. If your system, for example,
doesn't have ``python3.4`` those ``tox`` tests will be skipped.

For a faster test-rinse-repeat cycle you can run tests in a specific
environment with a specific version of Python and specific version of
Django of your choice. Here is such an example:


.. code-block:: shell

    $ virtualenv -p /path/to/bin/python3.5 venv
    $ source venv
    (venv) $ pip install Django==1.11.2
    (venv) $ pip install -r tests/requirements.txt
    (venv) $ DJANGO_SETTINGS_MODULE=tests.settings django-admin.py test

Measuring code coverage, continuing the steps above:

.. code-block:: shell

    (venv) $ pip install coverage
    (venv) $ DJANGO_SETTINGS_MODULE=tests.settings coverage run --source mozilla_django_oidc `which django-admin.py` test
    (venv) $ coverage report
    (venv) $ coverage html
    (venv) $ open htmlcov/index.html

Local development
-----------------

The local development setup is based on Docker so you need the following installed in your system:

* `docker`
* `docker-compose`

You will also need to edit your ``hosts`` file to resolve ``testrp`` and ``testprovider`` hostnames to ``127.0.0.1``.

Running test services
=====================

To run the `testrp` and `testprovider` instances run the following:

.. code-block:: shell

   (venv) $ docker-compose up -d testprovider testrp

Then visit the testing django app on: ``http://testrp:8081``.

The library source code is mounted as a docker volume and source code changes are reflected directly in.
In order to test a change you need to restart the ``testrp`` service.

.. code-block:: shell

   (venv) $ docker-compose stop testrp
   (venv) $ docker-compose up -d testrp

Running integration tests
=========================

Integration tests are mounted as a volume to the docker containers. Tests can be run using the following command:

.. code-block:: shell

   (venv) $ docker-compose run --service-ports testrunner

Linting
-------

All code is checked with `<https://pypi.python.org/pypi/flake8>`_ in
continuous integration. To make sure your code still passes all style guides
install ``flake8`` and check:

.. code-block:: shell

    $ flake8 mozilla_django_oidc tests

.. note::

    When you run ``tox`` it also does a ``flake8`` run on the main package
    files and the tests.

You can also run linting with ``tox``:

.. code-block:: shell

    $ tox -e lint


Releasing a new version
------------------------

``mozilla-django-oidc`` releases are hosted in `PyPI <https://pypi.python.org/pypi/mozilla-django-oidc>`_.
Here are the steps you need to follow in order to push a new release:

* Make sure that ``HISTORY.rst`` is up-to-date focusing mostly on backwards incompatible changes.

  Security vulnerabilities should be clearly marked in a "Security issues" section along with
  a level indicator of:

  * High: vulnerability facilitates data loss, data access, impersonation of admin, or allows access
    to other sites or components

    Users should upgrade immediately.

  * Medium: vulnerability endangers users by sending them to malicious sites or stealing browser
    data.

    Users should upgrade immediately.

  * Low: vulnerability is a nuissance to site staff and/or users

    Users should upgrade.

* Bump the project version and create a commit for the new version.

  * You can use ``bumpversion`` for that. It is a tool to automate this procedure following the `semantic versioning scheme <http://semver.org/>`_.

    * For a patch version update (eg 0.1.1 to 0.1.2) you can run ``bumpversion patch``.
    * For a minor version update (eg 0.1.0 to 0.2.0) you can run ``bumpversion minor``.
    * For a major version update (eg 0.1.0 to 1.0.0) you can run ``bumpversion major``.

* Create a `signed tag <https://git-scm.com/book/tr/v2/Git-Tools-Signing-Your-Work>`_ for that version

  Example::

      git tag -s 0.1.1 -m "Bump version: 0.1.0 to 0.1.1"

* Push the signed tag to Github

  Example::

      git push origin 0.1.1

The release is pushed automatically to PyPI using a travis deployment hook on every new tag.


License
-------

This software is licensed under the MPL 2.0 license. For more info check the LICENSE file.


Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage

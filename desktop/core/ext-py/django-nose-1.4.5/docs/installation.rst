Installation
------------

You can get django-nose from PyPI with... :

.. code-block:: shell

    $ pip install django-nose

The development version can be installed with... :

.. code-block:: shell

    $ pip install -e git://github.com/django-nose/django-nose.git#egg=django-nose

Since django-nose extends Django's built-in test command, you should add it to
your ``INSTALLED_APPS`` in ``settings.py``:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_nose',
        ...
    )

Then set ``TEST_RUNNER`` in ``settings.py``:

.. code-block:: python

    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'



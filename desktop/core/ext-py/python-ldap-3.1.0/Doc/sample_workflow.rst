.. _sample workflow:

Sample workflow for python-ldap development
-------------------------------------------

This document will guide you through the process of contributing a change
to python-ldap.

We assume that, as a user of python-ldap, you're not new to software
development in general, so these instructions are terse.
If you need additional detail, please do ask on the mailing list.

.. note::

    The following instructions are for Linux.
    If you can translate them to another system, please contribute your
    translation!


Install `Git`_, `tox`_ and the :ref:`build prerequisites`.

.. _tox: https://tox.readthedocs.io/en/latest/

Clone the repository::

    $ git clone https://github.com/python-ldap/python-ldap
    $ cd python-ldap

Create a `virtual environment`_ to ensure you in-development python-ldap won't
affect the rest of your system::

    $ python3 -m venv __venv__

(For Python 2, install `virtualenv`_ and use it instead of ``python3 -m venv``.)

.. _git: https://git-scm.com/
.. _virtual environment: https://docs.python.org/3/library/venv.html
.. _virtualenv: https://virtualenv.pypa.io/en/stable/

Activate the virtual environment::

    $ source __venv__/bin/activate

Install python-ldap to it in `editable mode`_::

    (__venv__)$ python -m pip install -e .

This way, importing a Python module from python-ldap will directly
use the code from your source tree.
If you change C code, you will still need to recompile
(using the ``pip install`` command again).

.. _editable mode: https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs

Change the code as desired.


To run tests, install and run `tox`_::

    (__venv__)$ python -m pip install tox
    (__venv__)$ tox --skip-missing-interpreters

This will run tests on all supported versions of Python that you have
installed, skipping the ones you don't.
To run a subset of test environments, run for example::

    (__venv__)$ tox -e py27,py36

In addition to ``pyXY`` environments, we have extra environments
for checking things independent of the Python version:

* ``doc`` checks syntax and spelling of the documentation
* ``coverage-report`` generates a test coverage report for Python code.
  It must be used last, e.g. ``tox -e py27,py36,coverage-report``.
* ``py2-nosasltls`` and ``py3-nosasltls`` check functionality without
  SASL and TLS bindings compiled in.


When your change is ready, commit to Git, and submit a pull request on GitHub.
You can take a look at the :ref:`committer instructions` to see what we are looking
for in a pull request.

If you don't want to open a GitHub account, please send patches as attachments
to the python-ldap mailing list.

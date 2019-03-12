.. highlight:: console

Contributing to python-ldap
***************************

Thank you for your interest in python-ldap!
If you'd like to contribute (be it code, documentation, maintenance effort,
or anything else), this guide is for you.


.. toctree::
   :hidden:

   sample_workflow.rst


Communication
=============

Always keep in mind that python-ldap is developed and maintained by volunteers.
We're happy to share our work, and to work with you to make the library better,
but (until you pay someone), there's obligation to provide assistance.

So, keep it friendly, respectful, and supportive!


Mailing list
------------

Discussion about the use and future of python-ldap occurs in
the ``python-ldap@python.org`` mailing list.

It's also the channel to use if documentation (including this guide) is not
clear to you.
Do try searching around before you ask on the list, though!

You can `subscribe or unsubscribe`_ to this list or browse the `list archive`_.

.. _subscribe or unsubscribe: https://mail.python.org/mailman/listinfo/python-ldap
.. _list archive: https://mail.python.org/pipermail/python-ldap/


Issues
------

Please report bugs, missing features and other issues to `the bug tracker`_
at GitHub. You will need a GitHub account for that.

If you prefer not to open a GitHub account, you're always welcome to use the
mailing list.


Security Contact
----------------

If you found a security issue that should not be discussed publicly,
please e-mail the maintainer at ``pviktori@redhat.com``.
If required, write to coordinate a more secure channel.

All other communication should be public.


Contributing code
=================

If you're used to open-source Python development with Git, here's the gist:

* ``git clone https://github.com/python-ldap/python-ldap``
* Use GitHub for `the bug tracker`_ and pull requests.
* Run tests with `tox`_; ignore Python interpreters you don't have locally.

.. _the bug tracker: https://github.com/python-ldap/python-ldap/issues
.. _tox: https://tox.readthedocs.io/en/latest/

Or, if you prefer to avoid closed-source services:

* ``git clone https://pagure.io/python-ldap``
* Send bug reports and patches to the mailing list.
* Run tests with `tox`_; ignore Python interpreters you don't have locally.
* Read the documentation directly at `Read the Docs`_.

.. _Read the Docs: https://python-ldap.readthedocs.io/

If you're new to some aspect of the project, you're welcome to use (or adapt)
our :ref:`sample workflow <sample workflow>`.


.. _additional tests:

Additional tests and scripts
============================

We use several specialized tools for debugging and maintenance.

Make targets
------------

Make targets currently use the ``python3`` executable.
Specify a different one using, for example::

    make PYTHON=/usr/local/bin/python

Notable targets are:

``make autoformat``
    Automatically re-formats C and Python code to conform to Python style
    guides (`PEP 7`_ and `PEP 8`_).
    Note that no backups are made – please commit any other changes before
    using this target.

    Requires the ``indent`` program and the ``autopep8`` Python module.

.. _PEP 7: https://www.python.org/dev/peps/pep-0007/
.. _PEP 8: https://www.python.org/dev/peps/pep-0008/

``make lcov lcov-open``
    Generate and view test coverage for C code.
    Requires LCOV_.

``make scan-build``
    Run static analysis. Requires ``clang``.

``make valgrind``
    Run Valgrind_ to check for memory leaks. Requires ``valgrind`` and
    a Python suppression file, which you can specify as ``PYTHON_SUPP``, e.g.::

        make valgrind PYTHON_SUPP=/your/path/to/valgrind-python.supp

    The suppression file is ``Misc/valgrind-python.supp`` in the Python
    source distribution, and it's frequently packaged together with
    Python development headers.

.. _LCOV: https://github.com/linux-test-project/lcov
.. _Valgrind: http://valgrind.org/


Reference leak tests
--------------------

Reference leak tests require a *pydebug* build of CPython and `pytest`_ with
`pytest-leaks`_ plugin. A *pydebug* build has a global reference counter, which
keeps track of all reference increments and decrements. The leak plugin runs
each test multiple times and checks if the reference count increases.

.. _pytest: https://docs.pytest.org/en/latest/
.. _pytest-leaks: https://pypi.org/project/pytest-leaks/

Download and compile the *pydebug* build::

    $ curl -O https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tar.xz
    $ tar xJf Python-3.6.3.tar.xz
    $ cd Python-3.6.3
    $ ./configure --with-pydebug
    $ make

Create a virtual environment with the *pydebug* build::

    $ ./python -m venv /tmp/refleak
    $ /tmp/refleak/bin/pip install pytest pytest-leaks

Run reference leak tests::

    $ cd path/to/python-ldap
    $ /tmp/refleak/bin/pip install --upgrade .
    $ /tmp/refleak/bin/pytest -v -R:

Run ``/tmp/refleak/bin/pip install --upgrade .`` every time a file outside
of ``Tests/`` is modified.


.. _committer instructions:

Instructions for core committers
================================

If you have the authority (and responsibility) of merging changes from others,
remember:

* All code changes need to be reviewed by someone other than the author.

* Tests must always pass. New features without tests shall *not* pass review.

* Make sure commit messages don't use GitHub-specific link syntax.
  Use the full URL, e.g. ``https://github.com/python-ldap/python-ldap/issues/50``
  instead of ``#20``.

  * Exception: it's fine to use the short form in the summary line of a merge
    commit, if the full URL appears later.
  * It's OK to use shortcuts in GitHub *discussions*, where they are not
    hashed into immutable history.

* Make a merge commit if the contribution contains several well-isolated
  separate commits with good descriptions. Use *squash-and-merge* (or
  *fast-forward* from a command line) for all other cases.

* It's OK to push small changes into a pull request. If you do this, document
  what you have done (so the contributor can learn for the future), and get
  their :abbr:`ACK (confirmation)` before merging.

* When squashing, do edit commit messages to add references to the pull request
  and relevant discussions/issues, and to conform to Git best practices.

  * Consider making the summary line suitable for the CHANGES document,
    and starting it with a prefix like ``Lib:`` or ``Tests:``.

* Push to Pagure as well.

If you have good reason to break the “rules”, go ahead and break them,
but mention why.


Instructions for release managers
=================================

If you are tasked with releasing python-ldap, remember to:

* Bump all instances of the version number.
* Go through all changes since last version, and add them to ``CHANGES``.
* Run :ref:`additional tests` as appropriate, fix any regressions.
* Change the release date in ``CHANGES``.
* Merge all that (using pull requests).
* Run ``python setup.py sdist``, and smoke-test the resulting package
  (install in a clean virtual environment, import ``ldap``).
* Create Git tag ``python-ldap-{version}``, and push it to GitHub and Pagure.
* Release the ``sdist`` on PyPI.
* Announce the release on the mailing list.
  Mention the Git hash.
* Add the release's log from ``CHANGES`` on the `GitHub release page`_.

.. _GitHub release page: https://github.com/python-ldap/python-ldap/releases

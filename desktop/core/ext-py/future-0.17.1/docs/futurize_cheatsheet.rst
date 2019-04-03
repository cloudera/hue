.. _futurize_cheatsheet:

``futurize`` quick-start guide
------------------------------

How to convert Py2 code to Py2/3 code using ``futurize``:

.. _porting-setup:

Step 0: setup
~~~~~~~~~~~~~

Step 0 goal: set up and see the tests passing on Python 2 and failing on Python 3.

a. Clone the package from github/bitbucket. Optionally rename your repo to ``package-future``. Examples: ``reportlab-future``, ``paramiko-future``, ``mezzanine-future``.
b. Create and activate a Python 2 conda environment or virtualenv. Install the package with ``python setup.py install`` and run its test suite on Py2.7 (e.g. ``python setup.py test`` or ``py.test``)
c. Optionally: if there is a ``.travis.yml`` file, add Python version 3.6 and remove any versions < 2.6.
d. Install Python 3 with e.g. ``sudo apt-get install python3``. On other platforms, an easy way is to use `Miniconda <http://repo.continuum.io/miniconda/index.html>`_. Then e.g.::

    conda create -n py36 python=3.6 pip

.. _porting-step1:

Step 1: modern Py2 code
~~~~~~~~~~~~~~~~~~~~~~~

The goal for this step is to modernize the Python 2 code without introducing any dependencies (on ``future`` or e.g. ``six``) at this stage.

**1a**. Install ``future`` into the virtualenv using::

          pip install future

**1b**. Run ``futurize --stage1 -w *.py subdir1/*.py subdir2/*.py``. Note that with
recursive globbing in ``bash`` or ``zsh``, you can apply stage 1 to all Python
source files recursively with::

        futurize --stage1 -w **/*.py

**1c**. Commit all changes

**1d**. Re-run the test suite on Py2 and fix any errors.

See :ref:`forwards-conversion-stage1` for more info.


Example error
*************

One relatively common error after conversion is::

    Traceback (most recent call last):
      ...
      File "/home/user/Install/BleedingEdge/reportlab/tests/test_encrypt.py", line 19, in <module>
        from .test_pdfencryption import parsedoc
    ValueError: Attempted relative import in non-package

If you get this error, try adding an empty ``__init__.py`` file in the package
directory. (In this example, in the tests/ directory.) If this doesn’t help,
and if this message appears for all tests, they must be invoked differently
(from the cmd line or e.g. ``setup.py``). The way to run a module inside a
package on Python 3, or on Python 2 with ``absolute_import`` in effect, is::

    python -m tests.test_platypus_xref

(For more info, see `PEP 328 <http://www.python.org/dev/peps/pep-0328/>`_ and
the `PEP 8 <http://www.python.org/dev/peps/pep-0008/>`_ section on absolute
imports.)


.. _porting-step2:

Step 2: working Py3 code that still supports Py2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The goal for this step is to get the tests passing first on Py3 and then on Py2
again with the help of the ``future`` package.

**2a**. Run::

        futurize --stage2 myfolder1/*.py myfolder2/*.py

Or, using recursive globbing with ``bash`` or ``zsh``, you can view the stage 2
changes to all Python source files recursively with::

    futurize --stage2 **/*.py

To apply the changes, add the ``-w`` argument.

This stage makes further conversions needed to support both Python 2 and 3.
These will likely require imports from ``future`` on Py2 (and sometimes on Py3),
such as::

    from future import standard_library
    standard_library.install_aliases()
    # ...
    from builtins import bytes
    from builtins import open
    from future.utils import with_metaclass

Optionally, you can use the ``--unicode-literals`` flag to add this import to
the top of each module::

    from __future__ import unicode_literals

All strings in the module would then be unicode on Py2 (as on Py3) unless
explicitly marked with a ``b''`` prefix.

If you would like ``futurize`` to import all the changed builtins to have their
Python 3 semantics on Python 2, invoke it like this::

    futurize --stage2 --all-imports myfolder/*.py


**2b**. Re-run your tests on Py3 now. Make changes until your tests pass on Python 3.

**2c**. Commit your changes! :)

**2d**. Now run your tests on Python 2 and notice the errors. Add wrappers from
``future`` to re-enable Python 2 compatibility. See the
:ref:`compatible-idioms` cheat sheet and :ref:`what-else` for more info.

After each change, re-run the tests on Py3 and Py2 to ensure they pass on both.

**2e**. You're done! Celebrate! Push your code and announce to the world! Hashtags
#python3 #python-future.

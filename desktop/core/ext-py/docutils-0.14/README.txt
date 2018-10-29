=======================
 README: Docutils 0.14
=======================

:Author: David Goodger
:Contact: goodger@python.org
:Date: $Date: 2017-08-03 11:03:32 +0200 (Do, 03 Aug 2017) $
:Web site: http://docutils.sourceforge.net/
:Copyright: This document has been placed in the public domain.

.. contents::


Quick-Start
===========

This is for those who want to get up & running quickly.

1. Docutils requires Python (version 2.4 or later), available from

     http://www.python.org/

   See Requirements_ below for details.

2. Use the latest Docutils code.  Get the code from the `Subversion
   repository`_ or from the snapshot:

     http://docutils.svn.sourceforge.net/viewvc/docutils/trunk/docutils/?view=tar

   See `Releases & Snapshots`_ below for details.

3. Unpack the tarball in a temporary directory (**not** directly in
   Python's ``site-packages``), go to the directory created by expanding
   the archive, and run ``setup.py install``. On
   Windows systems it may be sufficient to double-click ``install.py``.

   See Installation_ below for details.

4. Use the front-end scripts to convert reStructuredText documents.
   Try for example::

       rst2html.py FAQ.txt FAQ.html         (Unix)
       python tools/rst2html.py FAQ.txt FAQ.html  (Windows)

   See Usage_ below for details.


Purpose
=======

The purpose of the Docutils project is to create a set of tools for
processing plaintext documentation into useful formats, such as HTML,
XML, and LaTeX.  Support for the following sources has been
implemented:

* Standalone files.

* `PEPs (Python Enhancement Proposals)`_.

Support for the following sources is planned:

* Inline documentation from Python modules and packages, extracted
  with namespace context.

* Email (RFC-822 headers, quoted excerpts, signatures, MIME parts).

* Wikis, with global reference lookups of "wiki links".

* Compound documents, such as multiple chapter files merged into a
  book.

* And others as discovered.

.. _PEPs (Python Enhancement Proposals):
   http://www.python.org/peps/pep-0012.html


Releases & Snapshots
====================

While we are trying to follow a "release early & often" policy,
features are added frequently.  Since the code in the Subversion
repository is usually in a bug-free state, we recommend that you use
a current snapshot.

To get a snapshot, go to the code page and click the download snapshot
button:

* Docutils code, documentation, front-end tools, and tests:
  https://sourceforge.net/p/docutils/code/HEAD/tree/trunk/docutils/

* Sandbox (experimental, contributed code):
  https://sourceforge.net/p/docutils/code/HEAD/tree/trunk/sandbox/

To keep up to date on the latest developments, download fresh copies of
the snapshots regularly or use a working copy of the
`Subversion repository`_.

.. _Subversion repository: docs/dev/repository.html


Requirements
============

To run the code, Python_ must be installed.
Docutils is compatible with Python versions from 2.4 up to 2.7 and
versions 3.1 to 3.5 (cf. `Python 3 compatibility`_).

Docutils uses the following packages for enhanced functionality, if they are
installed:

* The `Python Imaging Library`_, or PIL, is used for some image
  manipulation operations.

* The `Pygments`_ syntax highlighter is used for content of `code`
  directives and roles.

.. _Python: http://www.python.org/.
.. _Python Imaging Library: http://www.pythonware.com/products/pil/
.. _Pygments: http://pygments.org/


Python 3 compatibility
----------------------

The Docutils codebase is written for Python 2 and uses "on-demand"
translation for `porting to Python 3`_.

* The `setup.py` script generates Python 3 compatible sources in
  ``build/`` and tests in ``tests3/`` sub-directories during
  installation_ with Python 3.

* The scripts in the ``tools/`` sub-directory work with all supported
  Python versions without conversion.

* To convert the sources without installing (e.g. for testing), run
  ``python3 setup.py build``.

* When editing the source, do changes on the Python 2 versions of the
  files and re-run the build command.

.. _porting to Python 3: http://docs.python.org/py3k/howto/pyporting.html


Project Files & Directories
===========================

* README.txt: You're reading it.

* COPYING.txt: Public Domain Dedication and copyright details for
  non-public-domain files (most are PD).

* FAQ.txt: Frequently Asked Questions (with answers!).

* RELEASE-NOTES.txt: Summary of the major changes in recent releases.

* HISTORY.txt: A detailed change log, for the current and all previous
  project releases.

* BUGS.txt: Known bugs, and how to report a bug.

* THANKS.txt: List of contributors.

* setup.py: Installation script.  See "Installation" below.

* install.py: Quick & dirty installation script.  Just run it.  For
  any kind of customization or help though, setup.py must be used.

* docutils: The project source directory, installed as a Python
  package.

* docs: The project documentation directory.  Read ``docs/index.txt``
  for an overview.

* docs/user: The project user documentation directory.  Contains the
  following documents, among others:

  - docs/user/tools.txt: Docutils Front-End Tools
  - docs/user/latex.txt: Docutils LaTeX Writer
  - docs/user/rst/quickstart.txt: A ReStructuredText Primer
  - docs/user/rst/quickref.html: Quick reStructuredText (HTML only)

* docs/ref: The project reference directory.
  ``docs/ref/rst/restructuredtext.txt`` is the reStructuredText
  reference.

* licenses: Directory containing copies of license files for
  non-public-domain files.

* tools: Directory for Docutils front-end tools.  See
  ``docs/user/tools.txt`` for documentation.

* test: Unit tests.  Not required to use the software, but very useful
  if you're planning to modify it.  See `Running the Test Suite`_
  below.

Generated directories when installing under Python 3:

* build: Converted sources.

* test3: Converted tests.


Installation
============

The first step is to expand the ``.tgz`` archive in a temporary
directory (**not** directly in Python's ``site-packages``).  It
contains a distutils setup file "setup.py".  OS-specific installation
instructions follow.


GNU/Linux, BSDs, Unix, Mac OS X, etc.
-------------------------------------

1. Open a shell.

2. Go to the directory created by expanding the archive::

       cd <archive_directory_path>

3. Install the package (you may need root permissions to complete this
   step)::

       su
       (enter admin password)
       python setup.py install

   If the python executable isn't on your path, you'll have to specify
   the complete path, such as ``/usr/local/bin/python``.

   To install for a specific Python version, use this version in the
   setup call, e.g. ::

       python3.1 setup.py install

   To install for different Python versions, repeat step 3 for every
   required version. The last installed version will be used in the
   `shebang line`_ of the ``rst2*.py`` wrapper scripts.

   .. _shebang line: http://en.wikipedia.org/wiki/Shebang_%28Unix%29

Windows
-------

Just double-click ``install.py``.  If this doesn't work, try the
following:

1. Open a DOS Box (Command Shell, MS-DOS Prompt, or whatever they're
   calling it these days).

2. Go to the directory created by expanding the archive::

       cd <archive_directory_path>

3. Install the package::

       <path_to_python.exe>\python setup.py install

   To install for a specific python version, specify the Python
   executable for this version.

   To install for different Python versions, repeat step 3 for every
   required version.

Optional steps:

* `running the test suite`_

* `converting the documentation`_


Usage
=====

There are many front-end tools in the unpacked "tools" subdirectory.
Installation under Unix places copies in the PATH.
You may want to begin with the "rst2html.py" front-end tool.  Most
tools take up to two arguments, the source path and destination path,
with STDIN and STDOUT being the defaults.  Use the "--help" option to
the front-end tools for details on options and arguments.  See
Docutils Front-End Tools (``docs/user/tools.txt``) for full documentation.

The package modules are continually growing and evolving.  The
``docutils.statemachine`` module is usable independently.  It contains
extensive inline documentation (in reStructuredText format of course).

Contributions are welcome!


Converting the documentation
============================

After unpacking and installing the Docutils package, the following
shell commands will generate HTML for all included documentation::

    cd <archive_directory_path>/tools
    ./buildhtml.py ../

On Windows systems, type::

    cd <archive_directory_path>\tools
    python buildhtml.py ..

The final directory name of the ``<archive_directory_path>`` is
"docutils" for snapshots.  For official releases, the directory may be
called "docutils-X.Y.Z", where "X.Y.Z" is the release version.
Alternatively::

    cd <archive_directory_path>
    tools/buildhtml.py --config=tools/docutils.conf          (Unix)
    python tools\buildhtml.py --config=tools\docutils.conf   (Windows)

Some files may generate system messages (warnings and errors).  The
``docs/user/rst/demo.txt`` file (under the archive directory) contains
five intentional errors.  (They test the error reporting mechanism!)


Running the Test Suite
======================

The test suite is documented in `Docutils Testing`_ (docs/dev/testing.txt).

To run the entire test suite, open a shell and use the following
commands::

    cd <archive_directory_path>/test
    ./alltests.py

Under Windows, type::

    cd <archive_directory_path>\test
    python alltests.py

For testing with Python 3 use the converted test suite::

    cd <archive_directory_path>/test3
    python3 alltests.py


You should see a long line of periods, one for each test, and then a
summary like this::

    Ran 1111 tests in 24.653s

    OK
    Elapsed time: 26.189 seconds

The number of tests will grow over time, and the times reported will
depend on the computer running the tests.  The difference between the
two times represents the time required to set up the tests (import
modules, create data structures, etc.).

If any of the tests fail, please `open a bug report`_ or `send an email`_
(see `Bugs <BUGS.html>`_).
Please include all relevant output, information about your operating
system, Python version, and Docutils version.  To see the Docutils
version, use one of the ``rst2*`` front ends or ``tools/quicktest.py``
with the ``--version`` option, e.g.::

    cd ../tools
    ./quicktest.py --version

Windows users type these commands::

    cd ..\tools
    python quicktest.py --version


.. _Docutils Testing: http://docutils.sourceforge.net/docs/dev/testing.html
.. _open a bug report:
   http://sourceforge.net/p/docutils/bugs/
.. _send an email: mailto:docutils-users@lists.sourceforge.net
   ?subject=Test%20suite%20failure
.. _web interface: https://sourceforge.net/p/docutils/mailman/


Getting Help
============

If you have questions or need assistance with Docutils or
reStructuredText, please post a message to the Docutils-users_ mailing
list.

.. _Docutils-users: docs/user/mailing-lists.html#docutils-users


..
   Local Variables:
   mode: indented-text
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   End:

=======================================================
Installation and Status
=======================================================

Quick installation for CPython (cffi is distributed with PyPy):

* ``pip install cffi``

* or get the source code via the `Python Package Index`__.

.. __: http://pypi.python.org/pypi/cffi

In more details:

This code has been developed on Linux, but should work on any POSIX
platform as well as on Windows 32 and 64.  (It relies occasionally on
libffi, so it depends on libffi being bug-free; this may not be fully
the case on some of the more exotic platforms.)

CFFI supports CPython 2.6, 2.7, 3.x (tested with 3.2 to 3.4); and is
distributed with PyPy (CFFI 1.0 is distributed with and requires
PyPy 2.6).

The core speed of CFFI is better than ctypes, with import times being
either lower if you use the post-1.0 features, or much higher if you
don't.  The wrapper Python code you typically need to write around the
raw CFFI interface slows things down on CPython, but not unreasonably
so.  On PyPy, this wrapper code has a minimal impact thanks to the JIT
compiler.  This makes CFFI the recommended way to interface with C
libraries on PyPy.

Requirements:

* CPython 2.6 or 2.7 or 3.x, or PyPy (PyPy 2.0 for the earliest
  versions of CFFI; or PyPy 2.6 for CFFI 1.0).

* in some cases you need to be able to compile C extension modules;
  refer to the appropriate docs for your OS.  This includes installing
  CFFI from sources; or developing code based on ``ffi.set_source()`` or
  ``ffi.verify()``; or installing such 3rd-party modules from sources.

* on CPython, on non-Windows platforms, you also need to install
  ``libffi-dev`` in order to compile CFFI itself.

* pycparser >= 2.06: https://github.com/eliben/pycparser (automatically
  tracked by ``pip install cffi``).

* `py.test`_ is needed to run the tests of CFFI itself.

.. _`py.test`: http://pypi.python.org/pypi/pytest

Download and Installation:

* http://pypi.python.org/packages/source/c/cffi/cffi-1.5.2.tar.gz

   - MD5: ...

   - SHA: ...

* Or grab the most current version from the `Bitbucket page`_:
  ``hg clone https://bitbucket.org/cffi/cffi``

* ``python setup.py install`` or ``python setup_base.py install``
  (should work out of the box on Linux or Windows; see below for
  `MacOS X`_ or `Windows 64`_.)

* running the tests: ``py.test  c/  testing/`` (if you didn't
  install cffi yet, you need first ``python setup_base.py build_ext -f
  -i``)

.. _`Bitbucket page`: https://bitbucket.org/cffi/cffi

Demos:

* The `demo`_ directory contains a number of small and large demos
  of using ``cffi``.

* The documentation below might be sketchy on details; for now the
  ultimate reference is given by the tests, notably
  `testing/cffi1/test_verify1.py`_ and `testing/cffi0/backend_tests.py`_.

.. _`demo`: https://bitbucket.org/cffi/cffi/src/default/demo
.. _`testing/cffi1/test_verify1.py`: https://bitbucket.org/cffi/cffi/src/default/testing/cffi1/test_verify1.py
.. _`testing/cffi0/backend_tests.py`: https://bitbucket.org/cffi/cffi/src/default/testing/cffi0/backend_tests.py


Platform-specific instructions
------------------------------

``libffi`` is notoriously messy to install and use --- to the point that
CPython includes its own copy to avoid relying on external packages.
CFFI does the same for Windows, but not for other platforms (which should
have their own working libffi's).
Modern Linuxes work out of the box thanks to ``pkg-config``.  Here are some
(user-supplied) instructions for other platforms.


MacOS X
+++++++

**Homebrew** (Thanks David Griffin for this)

1) Install homebrew: http://brew.sh

2) Run the following commands in a terminal

::

    brew install pkg-config libffi
    PKG_CONFIG_PATH=/usr/local/opt/libffi/lib/pkgconfig pip install cffi


Aternatively, **on OS/X 10.6** (Thanks Juraj Sukop for this)

For building libffi you can use the default install path, but then, in
``setup.py`` you need to change::

    include_dirs = []

to::

    include_dirs = ['/usr/local/lib/libffi-3.0.11/include']

Then running ``python setup.py build`` complains about "fatal error: error writing to -: Broken pipe", which can be fixed by running::

    ARCHFLAGS="-arch i386 -arch x86_64" python setup.py build

as described here_.

.. _here: http://superuser.com/questions/259278/python-2-6-1-pycrypto-2-3-pypi-package-broken-pipe-during-build


Windows (regular 32-bit)
++++++++++++++++++++++++

Win32 works and is tested at least each official release.

The recommended C compiler compatible with Python 2.7 is this one:
http://www.microsoft.com/en-us/download/details.aspx?id=44266
There is a known problem with distutils on Python 2.7, as 
explained in https://bugs.python.org/issue23246, and the same 
problem applies whenever you want to run compile() to build a dll with
this specific compiler suite download. 
``import setuptools`` might help, but YMMV

For Python 3.4 and beyond:
https://www.visualstudio.com/en-us/downloads/visual-studio-2015-ctp-vs


Windows 64
++++++++++

Win64 received very basic testing and we applied a few essential
fixes in cffi 0.7. The comment above applies for Python 2.7 on 
Windows 64 as well. Please report any other issue.

Note as usual that this is only about running the 64-bit version of
Python on the 64-bit OS.  If you're running the 32-bit version (the
common case apparently), then you're running Win32 as far as we're
concerned.

.. _`issue 9`: https://bitbucket.org/cffi/cffi/issue/9
.. _`Python issue 7546`: http://bugs.python.org/issue7546

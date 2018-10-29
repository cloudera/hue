Goals
-----

The interface is based on `LuaJIT's FFI`_, and follows a few principles:

* The goal is to call C code from Python without learning a 3rd language:
  existing alternatives require users to learn domain specific language
  (Cython_, SWIG_) or API (ctypes_). The CFFI design requires users to know
  only C and Python, minimizing the extra bits of API that need to be learned.

* Keep all the Python-related logic in Python so that you don't need to
  write much C code (unlike `CPython native C extensions`_).

* The preferred way is to work at the level of the API (Application
  Programming Interface): the C compiler is called from the declarations
  you write to validate and link to the C language constructs.
  Alternatively, it is also possible to work at the ABI level
  (Application Binary Interface), the way ctypes_ work.
  However, on non-Windows platforms, C libraries typically
  have a specified C API but not an ABI (e.g. they may
  document a "struct" as having at least these fields, but maybe more).

* Try to be complete.  For now some C99 constructs are not supported,
  but all C89 should be, including macros (and including macro "abuses",
  which you can `manually wrap`_ in saner-looking C functions).

* Attempt to support both PyPy and CPython, with a reasonable path
  for other Python implementations like IronPython and Jython.

* Note that this project is **not** about embedding executable C code in
  Python, unlike `Weave`_.  This is about calling existing C libraries
  from Python.

.. _`LuaJIT's FFI`: http://luajit.org/ext_ffi.html
.. _`Cython`: http://www.cython.org
.. _`SWIG`: http://www.swig.org/
.. _`CPython native C extensions`: http://docs.python.org/extending/extending.html
.. _`native C extensions`: http://docs.python.org/extending/extending.html
.. _`ctypes`: http://docs.python.org/library/ctypes.html
.. _`Weave`: http://wiki.scipy.org/Weave
.. _`manually wrap`: overview.html#abi-versus-api

Get started by reading `the overview`__.

.. __: overview.html


Comments and bugs
-----------------

The best way to contact us is on the IRC ``#pypy`` channel of
``irc.freenode.net``.  Feel free to discuss matters either there or in
the `mailing list`_.  Please report to the `issue tracker`_ any bugs.

As a general rule, when there is a design issue to resolve, we pick the
solution that is the "most C-like".  We hope that this module has got
everything you need to access C code and nothing more.

--- the authors, Armin Rigo and Maciej Fijalkowski

.. _`issue tracker`: https://bitbucket.org/cffi/cffi/issues
.. _`mailing list`: https://groups.google.com/forum/#!forum/python-cffi

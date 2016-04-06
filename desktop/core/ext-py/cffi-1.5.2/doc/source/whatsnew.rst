======================
What's New
======================


v1.5.2
======

* Fix 1.5.1 for Python 2.6.


v1.5.1
======

* A few installation-time tweaks (thanks Stefano!)

* Issue #245: Win32: ``__stdcall`` was never generated for
  ``extern "Python"`` functions

* Issue #246: trying to be more robust against CPython's fragile
  interpreter shutdown logic


v1.5.0
======

* Support for `using CFFI for embedding`__.

.. __: embedding.html


v1.4.2
======

Nothing changed from v1.4.1.


v1.4.1
======

* Fix the compilation failure of cffi on CPython 3.5.0.  (3.5.1 works;
  some detail changed that makes some underscore-starting macros
  disappear from view of extension modules, and I worked around it,
  thinking it changed in all 3.5 versions---but no: it was only in
  3.5.1.)


v1.4.0
======

* A `better way to do callbacks`__ has been added (faster and more
  portable, and usually cleaner).  It is a mechanism for the
  out-of-line API mode that replaces the dynamic creation of callback
  objects (i.e. C functions that invoke Python) with the static
  declaration in ``cdef()`` of which callbacks are needed.  This is
  more C-like, in that you have to structure your code around the idea
  that you get a fixed number of function pointers, instead of
  creating them on-the-fly.

* ``ffi.compile()`` now takes an optional ``verbose`` argument.  When
  ``True``, distutils prints the calls to the compiler.

* ``ffi.compile()`` used to fail if given ``sources`` with a path that
  includes ``".."``.  Fixed.

* ``ffi.init_once()`` added.  See docs__.

* ``dir(lib)`` now works on libs returned by ``ffi.dlopen()`` too.

* Cleaned up and modernized the content of the ``demo`` subdirectory
  in the sources (thanks matti!).

* ``ffi.new_handle()`` is now guaranteed to return unique ``void *``
  values, even if called twice on the same object.  Previously, in
  that case, CPython would return two ``cdata`` objects with the same
  ``void *`` value.  This change is useful to add and remove handles
  from a global dict (or set) without worrying about duplicates.
  It already used to work like that on PyPy.
  *This change can break code that used to work on CPython by relying
  on the object to be kept alive by other means than keeping the
  result of ffi.new_handle() alive.*  (The corresponding `warning in
  the docs`__ of ``ffi.new_handle()`` has been here since v0.8!)

.. __: using.html#extern-python
.. __: using.html#initonce
.. __: using.html#ffi-new-handle


v1.3.1
======

* The optional typedefs (``bool``, ``FILE`` and all Windows types) were
  not always available from out-of-line FFI objects.

* Opaque enums are phased out from the cdefs: they now give a warning,
  instead of (possibly wrongly) being assumed equal to ``unsigned int``.
  Please report if you get a reasonable use case for them.

* Some parsing details, notably ``volatile`` is passed along like
  ``const`` and ``restrict``.  Also, older versions of pycparser
  mis-parse some pointer-to-pointer types like ``char * const *``: the
  "const" ends up at the wrong place.  Added a workaround.


v1.3.0
======

* Added `ffi.memmove()`_.

* Pull request #64: out-of-line API mode: we can now declare
  floating-point types with ``typedef float... foo_t;``.  This only
  works if ``foo_t`` is a float or a double, not ``long double``.

* Issue #217: fix possible unaligned pointer manipulation, which crashes
  on some architectures (64-bit, non-x86).

* Issues #64 and #126: when using ``set_source()`` or ``verify()``,
  the ``const`` and ``restrict`` keywords are copied from the cdef
  to the generated C code; this fixes warnings by the C compiler.
  It also fixes corner cases like ``typedef const int T; T a;``
  which would previously not consider ``a`` as a constant.  (The
  cdata objects themselves are never ``const``.)

* Win32: support for ``__stdcall``.  For callbacks and function
  pointers; regular C functions still don't need to have their `calling
  convention`_ declared.

* Windows: CPython 2.7 distutils doesn't work with Microsoft's official
  Visual Studio for Python, and I'm told this is `not a bug`__.  For
  ffi.compile(), we `removed a workaround`__ that was inside cffi but
  which had unwanted side-effects.  Try saying ``import setuptools``
  first, which patches distutils...

.. _`ffi.memmove()`: using.html#memmove
.. __: https://bugs.python.org/issue23246
.. __: https://bitbucket.org/cffi/cffi/pull-requests/65/remove-_hack_at_distutils-which-imports/diff
.. _`calling convention`: using.html#windows-calling-conventions


v1.2.1
======

Nothing changed from v1.2.0.


v1.2.0
======

* Out-of-line mode: ``int a[][...];`` can be used to declare a structure
  field or global variable which is, simultaneously, of total length
  unknown to the C compiler (the ``a[]`` part) and each element is
  itself an array of N integers, where the value of N *is* known to the
  C compiler (the ``int`` and ``[...]`` parts around it).  Similarly,
  ``int a[5][...];`` is supported (but probably less useful: remember
  that in C it means ``int (a[5])[...];``).

* PyPy: the ``lib.some_function`` objects were missing the attributes
  ``__name__``, ``__module__`` and ``__doc__`` that are expected e.g. by
  some decorators-management functions from ``functools``.

* Out-of-line API mode: you can now do ``from _example.lib import x``
  to import the name ``x`` from ``_example.lib``, even though the
  ``lib`` object is not a standard module object.  (Also works in ``from
  _example.lib import *``, but this is even more of a hack and will fail
  if ``lib`` happens to declare a name called ``__all__``.  Note that
  ``*`` excludes the global variables; only the functions and constants
  make sense to import like this.)

* ``lib.__dict__`` works again and gives you a copy of the
  dict---assuming that ``lib`` has got no symbol called precisely
  ``__dict__``.  (In general, it is safer to use ``dir(lib)``.)

* Out-of-line API mode: global variables are now fetched on demand at
  every access.  It fixes issue #212 (Windows DLL variables), and also
  allows variables that are defined as dynamic macros (like ``errno``)
  or ``__thread`` -local variables.  (This change might also tighten
  the C compiler's check on the variables' type.)

* Issue #209: dereferencing NULL pointers now raises RuntimeError
  instead of segfaulting.  Meant as a debugging aid.  The check is
  only for NULL: if you dereference random or dead pointers you might
  still get segfaults.

* Issue #152: callbacks__: added an argument ``ffi.callback(...,
  onerror=...)``.  If the main callback function raises an exception
  and ``onerror`` is provided, then ``onerror(exception, exc_value,
  traceback)`` is called.  This is similar to writing a ``try:
  except:`` in the main callback function, but in some cases (e.g. a
  signal) an exception can occur at the very start of the callback
  function---before it had time to enter the ``try: except:`` block.

* Issue #115: added ``ffi.new_allocator()``, which officializes
  support for `alternative allocators`__.

.. __: using.html#callbacks
.. __: using.html#alternative-allocators


v1.1.2
======

* ``ffi.gc()``: fixed a race condition in multithreaded programs
  introduced in 1.1.1


v1.1.1
======

* Out-of-line mode: ``ffi.string()``, ``ffi.buffer()`` and
  ``ffi.getwinerror()`` didn't accept their arguments as keyword
  arguments, unlike their in-line mode equivalent.  (It worked in PyPy.)

* Out-of-line ABI mode: documented a restriction__ of ``ffi.dlopen()``
  when compared to the in-line mode.

* ``ffi.gc()``: when called several times with equal pointers, it was
  accidentally registering only the last destructor, or even none at
  all depending on details.  (It was correctly registering all of them
  only in PyPy, and only with the out-of-line FFIs.)

.. __: cdef.html#dlopen-note


v1.1.0
======

* Out-of-line API mode: we can now declare integer types with
  ``typedef int... foo_t;``.  The exact size and signedness of ``foo_t``
  is figured out by the compiler.

* Out-of-line API mode: we can now declare multidimensional arrays
  (as fields or as globals) with ``int n[...][...]``.  Before, only the
  outermost dimension would support the ``...`` syntax.

* Out-of-line ABI mode: we now support any constant declaration,
  instead of only integers whose value is given in the cdef.  Such "new"
  constants, i.e. either non-integers or without a value given in the
  cdef, must correspond to actual symbols in the lib.  At runtime they
  are looked up the first time we access them.  This is useful if the
  library defines ``extern const sometype somename;``.

* ``ffi.addressof(lib, "func_name")`` now returns a regular cdata object
  of type "pointer to function".  You can use it on any function from a
  library in API mode (in ABI mode, all functions are already regular
  cdata objects).  To support this, you need to recompile your cffi
  modules.

* Issue #198: in API mode, if you declare constants of a ``struct``
  type, what you saw from lib.CONSTANT was corrupted.

* Issue #196: ``ffi.set_source("package._ffi", None)`` would
  incorrectly generate the Python source to ``package._ffi.py`` instead
  of ``package/_ffi.py``.  Also fixed: in some cases, if the C file was
  in ``build/foo.c``, the .o file would be put in ``build/build/foo.o``.


v1.0.3
======

* Same as 1.0.2, apart from doc and test fixes on some platforms.


v1.0.2
======

* Variadic C functions (ending in a "..." argument) were not supported
  in the out-of-line ABI mode.  This was a bug---there was even a
  (non-working) example__ doing exactly that!

.. __: overview.html#out-of-line-abi-level


v1.0.1
======

* ``ffi.set_source()`` crashed if passed a ``sources=[..]`` argument.
  Fixed by chrippa on pull request #60.

* Issue #193: if we use a struct between the first cdef() where it is
  declared and another cdef() where its fields are defined, then this
  definition was ignored.

* Enums were buggy if you used too many "..." in their definition.


v1.0.0
======

* The main news item is out-of-line module generation:

  * `for ABI level`_, with ``ffi.dlopen()``

  * `for API level`_, which used to be with ``ffi.verify()``, now deprecated

* (this page will list what is new from all versions from 1.0.0
  forward.)

.. _`for ABI level`: overview.html#out-of-line-abi-level
.. _`for API level`: overview.html#out-of-line-api-level

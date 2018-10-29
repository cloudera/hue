======================
What's New
======================


v1.11.5
=======

* `Issue #357`_: fix ``ffi.emit_python_code()`` which generated a buggy
  Python file if you are using a ``struct`` with an anonymous ``union``
  field or vice-versa.

* Windows: ``ffi.dlopen()`` should now handle unicode filenames.

* ABI mode: implemented ``ffi.dlclose()`` for the in-line case (it used
  to be present only in the out-of-line case).

* Fixed a corner case for ``setup.py install --record=xx --root=yy``
  with an out-of-line ABI module.  Also fixed `Issue #345`_.

* More hacks on Windows for running CFFI's own ``setup.py``.

* `Issue #358`_: in embedding, to protect against (the rare case of)
  Python initialization from several threads in parallel, we have to use
  a spin-lock.  On CPython 3 it is worse because it might spin-lock for
  a long time (execution of ``Py_InitializeEx()``).  Sadly, recent
  changes to CPython make that solution needed on CPython 2 too.

* CPython 3 on Windows: we no longer compile with ``Py_LIMITED_API``
  by default because such modules cannot be used with virtualenv.
  `Issue #350`_ mentions a workaround if you still want that and are not
  concerned about virtualenv: pass a ``define_macros=[("Py_LIMITED_API",
  None)]`` to the ``ffibuilder.set_source()`` call.

.. _`Issue #345`: https://bitbucket.org/cffi/cffi/issues/345/
.. _`Issue #350`: https://bitbucket.org/cffi/cffi/issues/350/
.. _`Issue #358`: https://bitbucket.org/cffi/cffi/issues/358/
.. _`Issue #357`: https://bitbucket.org/cffi/cffi/issues/357/


v1.11.4
=======

* Windows: reverted linking with ``python3.dll``, because
  virtualenv does not make this DLL available to virtual environments
  for now.  See `Issue #355`_.  On Windows only, the C extension
  modules created by cffi follow for now the standard naming scheme
  ``foo.cp36-win32.pyd``, to make it clear that they are regular
  CPython modules depending on ``python36.dll``.

.. _`Issue #355`: https://bitbucket.org/cffi/cffi/issues/355/


v1.11.3
=======

* Fix on CPython 3.x: reading the attributes ``__loader__`` or
  ``__spec__`` from the cffi-generated lib modules gave a buggy
  SystemError.  (These attributes are always None, and provided only to
  help compatibility with tools that expect them in all modules.)

* More Windows fixes: workaround for MSVC not supporting large
  literal strings in C code (from
  ``ffi.embedding_init_code(large_string)``); and an issue with
  ``Py_LIMITED_API`` linking with ``python35.dll/python36.dll`` instead
  of ``python3.dll``.

* Small documentation improvements.


v1.11.2
=======

* Fix Windows issue with managing the thread-state on CPython 3.0 to 3.5


v1.11.1
=======

* Fix tests, remove deprecated C API usage

* Fix (hack) for 3.6.0/3.6.1/3.6.2 giving incompatible binary extensions
  (cpython issue `#29943`_)

* Fix for 3.7.0a1+

.. _`#29943`: https://bugs.python.org/issue29943


v1.11
=====

* Support the modern standard types ``char16_t`` and ``char32_t``.
  These work like ``wchar_t``: they represent one unicode character, or
  when used as ``charN_t *`` or ``charN_t[]`` they represent a unicode
  string.  The difference with ``wchar_t`` is that they have a known,
  fixed size.  They should work at all places that used to work with
  ``wchar_t`` (please report an issue if I missed something).  Note
  that with ``set_source()``, you need to make sure that these types are
  actually defined by the C source you provide (if used in ``cdef()``).

* Support the C99 types ``float _Complex`` and ``double _Complex``.
  Note that libffi doesn't support them, which means that in the ABI
  mode you still cannot call C functions that take complex numbers
  directly as arguments or return type.

* Fixed a rare race condition when creating multiple ``FFI`` instances
  from multiple threads.  (Note that you aren't meant to create many
  ``FFI`` instances: in inline mode, you should write ``ffi =
  cffi.FFI()`` at module level just after ``import cffi``; and in
  out-of-line mode you don't instantiate ``FFI`` explicitly at all.)

* Windows: using callbacks can be messy because the CFFI internal error
  messages show up to stderr---but stderr goes nowhere in many
  applications.  This makes it particularly hard to get started with the
  embedding mode.  (Once you get started, you can at least use
  ``@ffi.def_extern(onerror=...)`` and send the error logs where it
  makes sense for your application, or record them in log files, and so
  on.)  So what is new in CFFI is that now, on Windows CFFI will try to
  open a non-modal MessageBox (in addition to sending raw messages to
  stderr).  The MessageBox is only visible if the process stays alive:
  typically, console applications that crash close immediately, but that
  is also the situation where stderr should be visible anyway.

* Progress on support for `callbacks in NetBSD`__.

* Functions returning booleans would in some case still return 0 or 1
  instead of False or True.  Fixed.

* `ffi.gc()`__ now takes an optional third parameter, which gives an
  estimate of the size (in bytes) of the object.  So far, this is only
  used by PyPy, to make the next GC occur more quickly (`issue #320`__).
  In the future, this might have an effect on CPython too (provided
  the CPython `issue 31105`__ is addressed).

* Add a note to the documentation: the ABI mode gives function objects
  that are *slower* to call than the API mode does.  For some reason it
  is often thought to be faster.  It is not!

.. __: https://bitbucket.org/cffi/cffi/issues/321/cffi-191-segmentation-fault-during-self
.. __: ref.html#ffi-gc
.. __: https://bitbucket.org/cffi/cffi/issues/320/improve-memory_pressure-management
.. __: http://bugs.python.org/issue31105


Older Versions
==============

v1.10.1
-------

(only released inside PyPy 5.8.0)

* Fixed the line numbers reported in case of ``cdef()`` errors.
  Also, I just noticed, but pycparser always supported the preprocessor
  directive ``# 42 "foo.h"`` to mean "from the next line, we're in file
  foo.h starting from line 42", which it puts in the error messages.


v1.10
-----

* Issue #295: use calloc() directly instead of
  PyObject_Malloc()+memset() to handle ffi.new() with a default
  allocator.  Speeds up ``ffi.new(large-array)`` where most of the time
  you never touch most of the array.

* Some OS/X build fixes ("only with Xcode but without CLT").

* Improve a couple of error messages: when getting mismatched versions
  of cffi and its backend; and when calling functions which cannot be
  called with libffi because an argument is a struct that is "too
  complicated" (and not a struct *pointer*, which always works).

* Add support for some unusual compilers (non-msvc, non-gcc, non-icc,
  non-clang)

* Implemented the remaining cases for ``ffi.from_buffer``.  Now all
  buffer/memoryview objects can be passed.  The one remaining check is
  against passing unicode strings in Python 2.  (They support the buffer
  interface, but that gives the raw bytes behind the UTF16/UCS4 storage,
  which is most of the times not what you expect.  In Python 3 this has
  been fixed and the unicode strings don't support the memoryview
  interface any more.)

* The C type ``_Bool`` or ``bool`` now converts to a Python boolean
  when reading, instead of the content of the byte as an integer.  The
  potential incompatibility here is what occurs if the byte contains a
  value different from 0 and 1.  Previously, it would just return it;
  with this change, CFFI raises an exception in this case.  But this
  case means "undefined behavior" in C; if you really have to interface
  with a library relying on this, don't use ``bool`` in the CFFI side.
  Also, it is still valid to use a byte string as initializer for a
  ``bool[]``, but now it must only contain ``\x00`` or ``\x01``.  As an
  aside, ``ffi.string()`` no longer works on ``bool[]`` (but it never
  made much sense, as this function stops at the first zero).

* ``ffi.buffer`` is now the name of cffi's buffer type, and
  ``ffi.buffer()`` works like before but is the constructor of that type.

* ``ffi.addressof(lib, "name")``  now works also in in-line mode, not
  only in out-of-line mode.  This is useful for taking the address of
  global variables.

* Issue #255: ``cdata`` objects of a primitive type (integers, floats,
  char) are now compared and ordered by value.  For example, ``<cdata
  'int' 42>`` compares equal to ``42`` and ``<cdata 'char' b'A'>``
  compares equal to ``b'A'``.  Unlike C, ``<cdata 'int' -1>`` does not
  compare equal to ``ffi.cast("unsigned int", -1)``: it compares
  smaller, because ``-1 < 4294967295``.

* PyPy: ``ffi.new()`` and ``ffi.new_allocator()()`` did not record
  "memory pressure", causing the GC to run too infrequently if you call
  ``ffi.new()`` very often and/or with large arrays.  Fixed in PyPy 5.7.

* Support in ``ffi.cdef()`` for numeric expressions with ``+`` or
  ``-``.  Assumes that there is no overflow; it should be fixed first
  before we add more general support for arbitrary arithmetic on
  constants.


v1.9
----

* Structs with variable-sized arrays as their last field: now we track
  the length of the array after ``ffi.new()`` is called, just like we
  always tracked the length of ``ffi.new("int[]", 42)``.  This lets us
  detect out-of-range accesses to array items.  This also lets us
  display a better ``repr()``, and have the total size returned by
  ``ffi.sizeof()`` and ``ffi.buffer()``.  Previously both functions
  would return a result based on the size of the declared structure
  type, with an assumed empty array.  (Thanks andrew for starting this
  refactoring.)

* Add support in ``cdef()/set_source()`` for unspecified-length arrays
  in typedefs: ``typedef int foo_t[...];``.  It was already supported
  for global variables or structure fields.

* I turned in v1.8 a warning from ``cffi/model.py`` into an error:
  ``'enum xxx' has no values explicitly defined: refusing to guess which
  integer type it is meant to be (unsigned/signed, int/long)``.  Now I'm
  turning it back to a warning again; it seems that guessing that the
  enum has size ``int`` is a 99%-safe bet.  (But not 100%, so it stays
  as a warning.)

* Fix leaks in the code handling ``FILE *`` arguments.  In CPython 3
  there is a remaining issue that is hard to fix: if you pass a Python
  file object to a ``FILE *`` argument, then ``os.dup()`` is used and
  the new file descriptor is only closed when the GC reclaims the Python
  file object---and not at the earlier time when you call ``close()``,
  which only closes the original file descriptor.  If this is an issue,
  you should avoid this automatic convertion of Python file objects:
  instead, explicitly manipulate file descriptors and call ``fdopen()``
  from C (...via cffi).


v1.8.3
------

* When passing a ``void *`` argument to a function with a different
  pointer type, or vice-versa, the cast occurs automatically, like in C.
  The same occurs for initialization with ``ffi.new()`` and a few other
  places.  However, I thought that ``char *`` had the same
  property---but I was mistaken.  In C you get the usual warning if you
  try to give a ``char *`` to a ``char **`` argument, for example.
  Sorry about the confusion.  This has been fixed in CFFI by giving for
  now a warning, too.  It will turn into an error in a future version.


v1.8.2
------

* Issue #283: fixed ``ffi.new()`` on structures/unions with nested
  anonymous structures/unions, when there is at least one union in
  the mix.  When initialized with a list or a dict, it should now
  behave more closely like the ``{ }`` syntax does in GCC.


v1.8.1
------

* CPython 3.x: experimental: the generated C extension modules now use
  the "limited API", which means that, as a compiled .so/.dll, it should
  work directly on any version of CPython >= 3.2.  The name produced by
  distutils is still version-specific.  To get the version-independent
  name, you can rename it manually to ``NAME.abi3.so``, or use the very
  recent setuptools 26.

* Added ``ffi.compile(debug=...)``, similar to ``python setup.py build
  --debug`` but defaulting to True if we are running a debugging
  version of Python itself.


v1.8
----

* Removed the restriction that ``ffi.from_buffer()`` cannot be used on
  byte strings.  Now you can get a ``char *`` out of a byte string,
  which is valid as long as the string object is kept alive.  (But
  don't use it to *modify* the string object!  If you need this, use
  ``bytearray`` or other official techniques.)

* PyPy 5.4 can now pass a byte string directly to a ``char *``
  argument (in older versions, a copy would be made).  This used to be
  a CPython-only optimization.


v1.7
----

* ``ffi.gc(p, None)`` removes the destructor on an object previously
  created by another call to ``ffi.gc()``

* ``bool(ffi.cast("primitive type", x))`` now returns False if the
  value is zero (including ``-0.0``), and True otherwise.  Previously
  this would only return False for cdata objects of a pointer type when
  the pointer is NULL.

* bytearrays: ``ffi.from_buffer(bytearray-object)`` is now supported.
  (The reason it was not supported was that it was hard to do in PyPy,
  but it works since PyPy 5.3.)  To call a C function with a ``char *``
  argument from a buffer object---now including bytearrays---you write
  ``lib.foo(ffi.from_buffer(x))``.  Additionally, this is now supported:
  ``p[0:length] = bytearray-object``.  The problem with this was that a
  iterating over bytearrays gives *numbers* instead of *characters*.
  (Now it is implemented with just a memcpy, of course, not actually
  iterating over the characters.)

* C++: compiling the generated C code with C++ was supposed to work,
  but failed if you make use the ``bool`` type (because that is rendered
  as the C ``_Bool`` type, which doesn't exist in C++).

* ``help(lib)`` and ``help(lib.myfunc)`` now give useful information,
  as well as ``dir(p)`` where ``p`` is a struct or pointer-to-struct.


v1.6
----

* `ffi.list_types()`_

* `ffi.unpack()`_

* `extern "Python+C"`_

* in API mode, ``lib.foo.__doc__`` contains the C signature now.  On
  CPython you can say ``help(lib.foo)``, but for some reason
  ``help(lib)`` (or ``help(lib.foo)`` on PyPy) is still useless; I
  haven't yet figured out the hacks needed to convince ``pydoc`` to
  show more.  (You can use ``dir(lib)`` but it is not most helpful.)

* Yet another attempt at robustness of ``ffi.def_extern()`` against
  CPython's interpreter shutdown logic.

.. _`ffi.list_types()`: ref.html#ffi-list-types
.. _`ffi.unpack()`: ref.html#ffi-unpack
.. _`extern "Python+C"`: using.html#extern-python-c


v1.5.2
------

* Fix 1.5.1 for Python 2.6.


v1.5.1
------

* A few installation-time tweaks (thanks Stefano!)

* Issue #245: Win32: ``__stdcall`` was never generated for
  ``extern "Python"`` functions

* Issue #246: trying to be more robust against CPython's fragile
  interpreter shutdown logic


v1.5.0
------

* Support for `using CFFI for embedding`__.

.. __: embedding.html


v1.4.2
------

Nothing changed from v1.4.1.


v1.4.1
------

* Fix the compilation failure of cffi on CPython 3.5.0.  (3.5.1 works;
  some detail changed that makes some underscore-starting macros
  disappear from view of extension modules, and I worked around it,
  thinking it changed in all 3.5 versions---but no: it was only in
  3.5.1.)


v1.4.0
------

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
.. __: ref.html#ffi-init-once
.. __: ref.html#ffi-new-handle


v1.3.1
------

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
------

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

.. _`ffi.memmove()`: ref.html#ffi-memmove
.. __: https://bugs.python.org/issue23246
.. __: https://bitbucket.org/cffi/cffi/pull-requests/65/remove-_hack_at_distutils-which-imports/diff
.. _`calling convention`: using.html#windows-calling-conventions


v1.2.1
------

Nothing changed from v1.2.0.


v1.2.0
------

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
.. __: ref.html#ffi-new-allocator


v1.1.2
------

* ``ffi.gc()``: fixed a race condition in multithreaded programs
  introduced in 1.1.1


v1.1.1
------

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
------

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
------

* Same as 1.0.2, apart from doc and test fixes on some platforms.


v1.0.2
------

* Variadic C functions (ending in a "..." argument) were not supported
  in the out-of-line ABI mode.  This was a bug---there was even a
  (non-working) example__ doing exactly that!

.. __: overview.html#out-of-line-abi-level


v1.0.1
------

* ``ffi.set_source()`` crashed if passed a ``sources=[..]`` argument.
  Fixed by chrippa on pull request #60.

* Issue #193: if we use a struct between the first cdef() where it is
  declared and another cdef() where its fields are defined, then this
  definition was ignored.

* Enums were buggy if you used too many "..." in their definition.


v1.0.0
------

* The main news item is out-of-line module generation:

  * `for ABI level`_, with ``ffi.dlopen()``

  * `for API level`_, which used to be with ``ffi.verify()``, now deprecated

* (this page will list what is new from all versions from 1.0.0
  forward.)

.. _`for ABI level`: overview.html#out-of-line-abi-level
.. _`for API level`: overview.html#out-of-line-api-level

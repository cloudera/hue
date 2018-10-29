======================================
Preparing and Distributing modules
======================================

.. contents::

There are three or four different ways to use CFFI in a project.
In order of complexity:

* The **"in-line", "ABI mode"**:

  .. code-block:: python

    import cffi

    ffi = cffi.FFI()
    ffi.cdef("C-like declarations")
    lib = ffi.dlopen("libpath")

    # use ffi and lib here

.. _out-of-line-abi:

* The **"out-of-line",** but still **"ABI mode",** useful to organize
  the code and reduce the import time:

  .. code-block:: python

    # in a separate file "package/foo_build.py"
    import cffi

    ffibuilder = cffi.FFI()
    ffibuilder.set_source("package._foo", None)
    ffibuilder.cdef("C-like declarations")

    if __name__ == "__main__":
        ffibuilder.compile()

  Running ``python foo_build.py`` produces a file ``_foo.py``, which
  can then be imported in the main program:

  .. code-block:: python

    from package._foo import ffi
    lib = ffi.dlopen("libpath")

    # use ffi and lib here

.. _out-of-line-api:

* The **"out-of-line", "API mode"** gives you the most flexibility
  and speed to access a C library at the level of C, instead of at the
  binary level:

  .. code-block:: python

    # in a separate file "package/foo_build.py"
    import cffi

    ffibuilder = cffi.FFI()
    ffibuilder.set_source("package._foo", r"""real C code""")   # <=
    ffibuilder.cdef("C-like declarations with '...'")

    if __name__ == "__main__":
        ffibuilder.compile(verbose=True)

  Running ``python foo_build.py`` produces a file ``_foo.c`` and
  invokes the C compiler to turn it into a file ``_foo.so`` (or
  ``_foo.pyd`` or ``_foo.dylib``).  It is a C extension module which
  can be imported in the main program:

  .. code-block:: python

    from package._foo import ffi, lib
    # no ffi.dlopen()

    # use ffi and lib here

.. _distutils-setuptools:

* Finally, you can (but don't have to) use CFFI's **Distutils** or
  **Setuptools integration** when writing a ``setup.py``.  For
  Distutils (only in out-of-line API mode):

  .. code-block:: python

    # setup.py (requires CFFI to be installed first)
    from distutils.core import setup

    import foo_build   # possibly with sys.path tricks to find it

    setup(
        ...,
        ext_modules=[foo_build.ffibuilder.distutils_extension()],
    )

  For Setuptools (out-of-line, but works in ABI or API mode;
  recommended):

  .. code-block:: python

    # setup.py (with automatic dependency tracking)
    from setuptools import setup

    setup(
        ...,
        setup_requires=["cffi>=1.0.0"],
        cffi_modules=["package/foo_build.py:ffibuilder"],
        install_requires=["cffi>=1.0.0"],
    )

* Note that some bundler tools that try to find all modules used by a
  project, like PyInstaller, will miss ``_cffi_backend`` in the
  out-of-line mode because your program contains no explicit ``import
  cffi`` or ``import _cffi_backend``.  You need to add
  ``_cffi_backend`` explicitly (as a "hidden import" in PyInstaller,
  but it can also be done more generally by adding the line ``import
  _cffi_backend`` in your main program).

Note that CFFI actually contains two different ``FFI`` classes.  The
page `Using the ffi/lib objects`_ describes the common functionality.
It is what you get in the ``from package._foo import ffi`` lines above.
On the other hand, the extended ``FFI`` class is the one you get from
``import cffi; ffi_or_ffibuilder = cffi.FFI()``.  It has the same
functionality (for in-line use), but also the extra methods described
below (to prepare the FFI).  NOTE: We use the name ``ffibuilder``
instead of ``ffi`` in the out-of-line context, when the code is about
producing a ``_foo.so`` file; this is an attempt to distinguish it
from the different ``ffi`` object that you get by later saying
``from _foo import ffi``.

.. _`Using the ffi/lib objects`: using.html

The reason for this split of functionality is that a regular program
using CFFI out-of-line does not need to import the ``cffi`` pure
Python package at all.  (Internally it still needs ``_cffi_backend``,
a C extension module that comes with CFFI; this is why CFFI is also
listed in ``install_requires=..`` above.  In the future this might be
split into a different PyPI package that only installs
``_cffi_backend``.)

Note that a few small differences do exist: notably, ``from _foo import
ffi`` returns an object of a type written in C, which does not let you
add random attributes to it (nor does it have all the
underscore-prefixed internal attributes of the Python version).
Similarly, the ``lib`` objects returned by the C version are read-only,
apart from writes to global variables.  Also, ``lib.__dict__`` does
not work before version 1.2 or if ``lib`` happens to declare a name
called ``__dict__`` (use instead ``dir(lib)``).  The same is true
for ``lib.__class__``, ``lib.__all__`` and ``lib.__name__`` added
in successive versions.


.. _cdef:

ffi/ffibuilder.cdef(): declaring types and functions
----------------------------------------------------

**ffi/ffibuilder.cdef(source)**: parses the given C source.
It registers all the functions, types, constants and global variables in
the C source.  The types can be used immediately in ``ffi.new()`` and
other functions.  Before you can access the functions and global
variables, you need to give ``ffi`` another piece of information: where
they actually come from (which you do with either ``ffi.dlopen()`` or
``ffi.set_source()``).

.. _`all types listed above`:

The C source is parsed internally (using ``pycparser``).  This code
cannot contain ``#include``.  It should typically be a self-contained
piece of declarations extracted from a man page.  The only things it
can assume to exist are the standard types:

* char, short, int, long, long long (both signed and unsigned)

* float, double, long double

* intN_t, uintN_t (for N=8,16,32,64), intptr_t, uintptr_t, ptrdiff_t,
  size_t, ssize_t

* wchar_t (if supported by the backend).  *New in version 1.11:*
  char16_t and char32_t.

* _Bool and bool (equivalent).  If not directly supported by the C
  compiler, this is declared with the size of ``unsigned char``.

* FILE.  `See here.`__

* all `common Windows types`_ are defined if you run
  on Windows (``DWORD``, ``LPARAM``, etc.).  Exception:
  ``TBYTE TCHAR LPCTSTR PCTSTR LPTSTR PTSTR PTBYTE PTCHAR`` are
  not automatically defined; see `ffi.set_unicode()`_.

* the other standard integer types from
  stdint.h, like ``intmax_t``, as long as they map to integers of 1,
  2, 4 or 8 bytes.  Larger integers are not supported.

.. __: ref.html#file
.. _`common Windows types`: http://msdn.microsoft.com/en-us/library/windows/desktop/aa383751%28v=vs.85%29.aspx

The declarations can also contain "``...``" at various places; these are
placeholders that will be completed by the compiler.  More information
about it below in `Letting the C compiler fill the gaps`_.

Note that all standard type names listed above are handled as
*defaults* only (apart from the ones that are keywords in the C
language).  If your ``cdef`` contains an explicit typedef that
redefines one of the types above, then the default described above is
ignored.  (This is a bit hard to implement cleanly, so in some corner
cases it might fail, notably with the error ``Multiple type specifiers
with a type tag``.  Please report it as a bug if it does.)

Multiple calls to ``ffi.cdef()`` are possible.  Beware that it can be
slow to call ``ffi.cdef()`` a lot of times, a consideration that is
important mainly in in-line mode.

The ``ffi.cdef()`` call takes an optional
argument ``packed``: if True, then all structs declared within
this cdef are "packed".  (If you need both packed and non-packed
structs, use several cdefs in sequence.)  This
has a meaning similar to ``__attribute__((packed))`` in GCC.  It
specifies that all structure fields should have an alignment of one
byte.  (Note that the packed attribute has no effect on bit fields so
far, which mean that they may be packed differently than on GCC.
Also, this has no effect on structs declared with ``"...;"``---more
about it later in `Letting the C compiler fill the gaps`_.)

Note that you can use the type-qualifiers ``const`` and ``restrict``
(but not ``__restrict`` or ``__restrict__``) in the ``cdef()``, but
this has no effect on the cdata objects that you get at run-time (they
are never ``const``).  The effect is limited to knowing if a global
variable is meant to be a constant or not.  Also, *new in version
1.3:* when using ``set_source()`` or ``verify()``, these two
qualifiers are copied from the cdef to the generated C code; this
fixes warnings by the C compiler.

Note a trick if you copy-paste code from sources in which there are
extra macros (for example, the Windows documentation uses SAL
annotations like ``_In_`` or ``_Out_``).  These hints must be removed
in the string given to cdef(), but it can be done programmatically
like this::

    ffi.cdef(re.sub(r"\b(_In_|_Inout_|_Out_|_Outptr_)(opt_)?\b", " ",
      """
        DWORD WINAPI GetModuleFileName(
          _In_opt_ HMODULE hModule,
          _Out_    LPTSTR  lpFilename,
          _In_     DWORD   nSize
        );
      """))

Note also that pycparser, the underlying C parser, recognizes
preprocessor-like directives in the following format: ``# NUMBER
"FILE"``.  For example, if you put ``# 42 "foo.h"`` in the middle of the
string passed to ``cdef()`` and there is an error two lines later, then
it is reported with an error message that starts with ``foo.h:43:`` (the
line which is given the number 42 is the line immediately after the
directive).  *New in version 1.10.1:*  CFFI automatically puts the line
``# 1 "<cdef source string>"`` just before the string you give to
``cdef()``.


.. _`ffi.set_unicode()`:

**ffi.set_unicode(enabled_flag)**: Windows: if ``enabled_flag`` is
True, enable the ``UNICODE`` and ``_UNICODE`` defines in C, and
declare the types ``TBYTE TCHAR LPCTSTR PCTSTR LPTSTR PTSTR PTBYTE
PTCHAR`` to be (pointers to) ``wchar_t``.  If ``enabled_flag`` is
False, declare these types to be (pointers to) plain 8-bit characters.
(These types are not predeclared at all if you don't call
``set_unicode()``.)

The reason behind this method is that a lot of standard functions have
two versions, like ``MessageBoxA()`` and ``MessageBoxW()``.  The
official interface is ``MessageBox()`` with arguments like
``LPTCSTR``.  Depending on whether ``UNICODE`` is defined or not, the
standard header renames the generic function name to one of the two
specialized versions, and declares the correct (unicode or not) types.

Usually, the right thing to do is to call this method with True.  Be
aware (particularly on Python 2) that, afterwards, you need to pass unicode
strings as arguments instead of byte strings.


.. _loading-libraries:

ffi.dlopen(): loading libraries in ABI mode
-------------------------------------------

``ffi.dlopen(libpath, [flags])``: this function opens a shared library and
returns a module-like library object.  Use this when you are fine with
the limitations of ABI-level access to the system (dependency on ABI
details, getting crashes instead of C compiler errors/warnings, and
higher overhead to call the C functions).  In case of doubt, read again
`ABI versus API`_ in the overview.

.. _`ABI versus API`: overview.html#abi-versus-api

You can use the library object to call the functions previously
declared by ``ffi.cdef()``, to read constants, and to read or write
global variables.  Note that you can use a single ``cdef()`` to
declare functions from multiple libraries, as long as you load each of
them with ``dlopen()`` and access the functions from the correct one.

The ``libpath`` is the file name of the shared library, which can
contain a full path or not (in which case it is searched in standard
locations, as described in ``man dlopen``), with extensions or not.
Alternatively, if ``libpath`` is None, it returns the standard C library
(which can be used to access the functions of glibc, on Linux).  Note
that ``libpath`` `cannot be None`__ on Windows with Python 3.

.. __: http://bugs.python.org/issue23606

Let me state it again: this gives ABI-level access to the library, so
you need to have all types declared manually exactly as they were
while the library was made.  No checking is done.  Mismatches can
cause random crashes.  API-level access, on the other hand, is safer.
Speed-wise, API-level access is much faster (it is common to have
the opposite misconception about performance).

Note that only functions and global variables live in library objects;
the types exist in the ``ffi`` instance independently of library objects.
This is due to the C model: the types you declare in C are not tied to a
particular library, as long as you ``#include`` their headers; but you
cannot call functions from a library without linking it in your program,
as ``dlopen()`` does dynamically in C.

For the optional ``flags`` argument, see ``man dlopen`` (ignored on
Windows).  It defaults to ``ffi.RTLD_NOW``.

This function returns a "library" object that gets closed when it goes
out of scope.  Make sure you keep the library object around as long as
needed.  (Alternatively, the out-of-line FFIs have a method
``ffi.dlclose(lib)``.)

.. _dlopen-note:

Note: the old version of ``ffi.dlopen()`` from the in-line ABI mode
tries to use ``ctypes.util.find_library()`` if it cannot directly find
the library.  The newer out-of-line ``ffi.dlopen()`` no longer does it
automatically; it simply passes the argument it receives to the
underlying ``dlopen()`` or ``LoadLibrary()`` function.  If needed, it
is up to you to use ``ctypes.util.find_library()`` or any other way to
look for the library's filename.  This also means that
``ffi.dlopen(None)`` no longer work on Windows; try instead
``ffi.dlopen(ctypes.util.find_library('c'))``.


ffibuilder.set_source(): preparing out-of-line modules
------------------------------------------------------

**ffibuilder.set_source(module_name, c_header_source, [\*\*keywords...])**:
prepare the ffi for producing out-of-line an external module called
``module_name``.

``ffibuilder.set_source()`` by itself does not write any file, but merely
records its arguments for later.  It can therefore be called before or
after ``ffibuilder.cdef()``.

In **ABI mode,** you call ``ffibuilder.set_source(module_name, None)``.  The
argument is the name (or dotted name inside a package) of the Python
module to generate.  In this mode, no C compiler is called.

In **API mode,** the ``c_header_source`` argument is a string that
will be pasted into the .c file generated.  Typically, it is specified as
``r""" ...multiple lines of C code... """`` (the ``r`` prefix allows these
lines to contain a literal ``\n``, for example).  This piece of C code
typically contains some ``#include``, but may also contain more,
like definitions for custom "wrapper" C functions.  The goal is that
the .c file can be generated like this::

    // C file "module_name.c"
    #include <Python.h>

    ...c_header_source...

    ...magic code...

where the "magic code" is automatically generated from the ``cdef()``.
For example, if the ``cdef()`` contains ``int foo(int x);`` then the
magic code will contain logic to call the function ``foo()`` with an
integer argument, itself wrapped inside some CPython or PyPy-specific
code.

The keywords arguments to ``set_source()`` control how the C compiler
will be called.  They are passed directly to distutils_ or setuptools_
and include at least ``sources``, ``include_dirs``, ``define_macros``,
``undef_macros``, ``libraries``, ``library_dirs``, ``extra_objects``,
``extra_compile_args`` and ``extra_link_args``.  You typically need at
least ``libraries=['foo']`` in order to link with ``libfoo.so`` or
``libfoo.so.X.Y``, or ``foo.dll`` on Windows.  The ``sources`` is a
list of extra .c files compiled and linked together (the file
``module_name.c`` shown above is always generated and automatically added as the
first argument to ``sources``).  See the distutils documentations for
`more information about the other arguments`__.

.. __: http://docs.python.org/distutils/setupscript.html#library-options
.. _distutils: http://docs.python.org/distutils/setupscript.html#describing-extension-modules
.. _setuptools: https://pythonhosted.org/setuptools/setuptools.html

An extra keyword argument processed internally is
``source_extension``, defaulting to ``".c"``.  The file generated will
be actually called ``module_name + source_extension``.  Example for
C++ (but note that there are still a few known issues of C-versus-C++
compatibility):

.. code-block:: python

    ffibuilder.set_source("mymodule", r'''
    extern "C" {
        int somefunc(int somearg) { return real_cpp_func(somearg); }
    }
    ''', source_extension='.cpp')


Letting the C compiler fill the gaps
------------------------------------

If you are using a C compiler ("API mode"), then:

*  functions taking or returning integer or float-point arguments can be
   misdeclared: if e.g. a function is declared by ``cdef()`` as taking a
   ``int``, but actually takes a ``long``, then the C compiler handles the
   difference.

*  other arguments are checked: you get a compilation warning or error
   if you pass a ``int *`` argument to a function expecting a ``long *``.

*  similarly, most other things declared in the ``cdef()`` are checked,
   to the best we implemented so far; mistakes give compilation
   warnings or errors.

Moreover, you can use "``...``" (literally, dot-dot-dot) in the
``cdef()`` at various places, in order to ask the C compiler to fill
in the details.  These places are:

*  structure declarations: any ``struct { }`` that ends with "``...;``" as
   the last "field" is
   partial: it may be missing fields and/or have them declared out of order.
   This declaration will be corrected by the compiler.  (But note that you
   can only access fields that you declared, not others.)  Any ``struct``
   declaration which doesn't use "``...``" is assumed to be exact, but this is
   checked: you get an error if it is not correct.

*  integer types: the syntax "``typedef
   int... foo_t;``" declares the type ``foo_t`` as an integer type
   whose exact size and signedness is not specified.  The compiler will
   figure it out.  (Note that this requires ``set_source()``; it does
   not work with ``verify()``.)  The ``int...`` can be replaced with
   ``long...`` or ``unsigned long long...`` or any other primitive
   integer type, with no effect.  The type will always map to one of
   ``(u)int(8,16,32,64)_t`` in Python, but in the generated C code,
   only ``foo_t`` is used.

* *New in version 1.3:* floating-point types: "``typedef
  float... foo_t;``" (or equivalently "``typedef double... foo_t;``")
  declares ``foo_t`` as a-float-or-a-double; the compiler will figure
  out which it is.  Note that if the actual C type is even larger
  (``long double`` on some platforms), then compilation will fail.
  The problem is that the Python "float" type cannot be used to store
  the extra precision.  (Use the non-dot-dot-dot syntax ``typedef long
  double foo_t;`` as usual, which returns values that are not Python
  floats at all but cdata "long double" objects.)

*  unknown types: the syntax "``typedef ... foo_t;``" declares the type
   ``foo_t`` as opaque.  Useful mainly for when the API takes and returns
   ``foo_t *`` without you needing to look inside the ``foo_t``.  Also
   works with "``typedef ... *foo_p;``" which declares the pointer type
   ``foo_p`` without giving a name to the opaque type itself.  Note that
   such an opaque struct has no known size, which prevents some operations
   from working (mostly like in C).  *You cannot use this syntax to
   declare a specific type, like an integer type!  It declares opaque
   struct-like types only.*  In some cases you need to say that
   ``foo_t`` is not opaque, but just a struct where you don't know any
   field; then you would use "``typedef struct { ...; } foo_t;``".

*  array lengths: when used as structure fields or in global variables,
   arrays can have an unspecified length, as in "``int n[...];``".  The
   length is completed by the C compiler.
   This is slightly different from "``int n[];``", because the latter
   means that the length is not known even to the C compiler, and thus
   no attempt is made to complete it.  This supports
   multidimensional arrays: "``int n[...][...];``".

   *New in version 1.2:* "``int m[][...];``", i.e. ``...`` can be used
   in the innermost dimensions without being also used in the outermost
   dimension.  In the example given, the length of the ``m`` array is
   assumed not to be known to the C compiler, but the length of every
   item (like the sub-array ``m[0]``) is always known the C compiler.
   In other words, only the outermost dimension can be specified as
   ``[]``, both in C and in CFFI, but any dimension can be given as
   ``[...]`` in CFFI.

*  enums: if you don't know the exact order (or values) of the declared
   constants, then use this syntax: "``enum foo { A, B, C, ... };``"
   (with a trailing "``...``").  The C compiler will be used to figure
   out the exact values of the constants.  An alternative syntax is
   "``enum foo { A=..., B, C };``" or even
   "``enum foo { A=..., B=..., C=... };``".  Like
   with structs, an ``enum`` without "``...``" is assumed to
   be exact, and this is checked.

*  integer constants and macros: you can write in the ``cdef`` the line
   "``#define FOO ...``", with any macro name FOO but with ``...`` as
   a value.  Provided the macro
   is defined to be an integer value, this value will be available via
   an attribute of the library object.  The
   same effect can be achieved by writing a declaration
   ``static const int FOO;``.  The latter is more general because it
   supports other types than integer types (note: the C syntax is then
   to write the ``const`` together with the variable name, as in
   ``static char *const FOO;``).

Currently, it is not supported to find automatically which of the
various integer or float types you need at which place---except in the
following case: if such a type is explicitly named.  For an integer
type, use ``typedef int... the_type_name;``, or another type like
``typedef unsigned long... the_type_name;``.  Both are equivalent and
replaced by the real C type, which must be an integer type.
Similarly, for floating-point types, use ``typedef float...
the_type_name;`` or equivalently ``typedef double...  the_type_name;``.
Note that ``long double`` cannot be detected this way.

In the case of function arguments or return types, when it is a simple
integer/float type, you can simply misdeclare it.  If you misdeclare a
function ``void f(long)`` as ``void f(int)``, it still works (but you
have to call it with arguments that fit an int).  It works because the C
compiler will do the casting for us.  This C-level casting of arguments
and return types only works for regular function, and not for function
pointer types; currently, it also does not work for variadic functions.

For more complex types, you have no choice but be precise.  For example,
you cannot misdeclare a ``int *`` argument as ``long *``, or a global
array ``int a[5];`` as ``long a[5];``.  CFFI considers `all types listed
above`_ as primitive (so ``long long a[5];`` and ``int64_t a[5]`` are
different declarations).  The reason for that is detailed in `a comment
about an issue.`__

.. __: https://bitbucket.org/cffi/cffi/issues/265/cffi-doesnt-allow-creating-pointers-to#comment-28406958


ffibuilder.compile() etc.: compiling out-of-line modules
--------------------------------------------------------

You can use one of the following functions to actually generate the
.py or .c file prepared with ``ffibuilder.set_source()`` and
``ffibuilder.cdef()``.

Note that these function won't overwrite a .py/.c file with exactly
the same content, to preserve the mtime.  In some cases where you need
the mtime to be updated anyway, delete the file before calling the
functions.

*New in version 1.8:* the C code produced by ``emit_c_code()`` or
``compile()`` contains ``#define Py_LIMITED_API``.  This means that on
CPython >= 3.2, compiling this source produces a binary .so/.dll that
should work for any version of CPython >= 3.2 (as opposed to only for
the same version of CPython x.y).  However, the standard ``distutils``
package will still produce a file called e.g.
``NAME.cpython-35m-x86_64-linux-gnu.so``.  You can manually rename it to
``NAME.abi3.so``, or use setuptools version 26 or later.  Also, note
that compiling with a debug version of Python will not actually define
``Py_LIMITED_API``, as doing so makes ``Python.h`` unhappy.  Finally,
``Py_LIMITED_API`` is not defined on Windows, because this makes
modules which cannot be used with ``virtualenv`` (issues `#355`__ and
`#350`__).

.. __: https://bitbucket.org/cffi/cffi/issues/355/importerror-dll-load-failed-on-windows
.. __: https://bitbucket.org/cffi/cffi/issues/350/issue-with-py_limited_api-on-windows

**ffibuilder.compile(tmpdir='.', verbose=False, debug=None):**
explicitly generate the .py or .c file,
and (if .c) compile it.  The output file is (or are) put in the
directory given by ``tmpdir``.  In the examples given here, we use
``if __name__ == "__main__": ffibuilder.compile()`` in the build scripts---if
they are directly executed, this makes them rebuild the .py/.c file in
the current directory.  (Note: if a package is specified in the call
to ``set_source()``, then a corresponding subdirectory of the ``tmpdir``
is used.)

*New in version 1.4:* ``verbose`` argument.  If True, it prints the
usual distutils output, including the command lines that call the
compiler.  (This parameter might be changed to True by default in a
future release.)

*New in version 1.8.1:* ``debug`` argument.  If set to a bool, it
controls whether the C code is compiled in debug mode or not.  The
default None means to use the host Python's ``sys.flags.debug``.
Starting with version 1.8.1, if you are running a debug-mode Python, the
C code is thus compiled in debug mode by default (note that it is anyway
necessary to do so on Windows).

**ffibuilder.emit_python_code(filename):** generate the given .py file (same
as ``ffibuilder.compile()`` for ABI mode, with an explicitly-named file to
write).  If you choose, you can include this .py file pre-packaged in
your own distributions: it is identical for any Python version (2 or
3).

**ffibuilder.emit_c_code(filename):** generate the given .c file (for API
mode) without compiling it.  Can be used if you have some other method
to compile it, e.g. if you want to integrate with some larger build
system that will compile this file for you.  You can also distribute
the .c file: unless the build script you used depends on the OS or
platform, the .c file itself is generic (it would be exactly the same
if produced on a different OS, with a different version of CPython, or
with PyPy; it is done with generating the appropriate ``#ifdef``).

**ffibuilder.distutils_extension(tmpdir='build', verbose=True):** for
distutils-based ``setup.py`` files.  Calling this creates the .c file
if needed in the given ``tmpdir``, and returns a
``distutils.core.Extension`` instance.

For Setuptools, you use instead the line
``cffi_modules=["path/to/foo_build.py:ffibuilder"]`` in ``setup.py``.  This
line asks Setuptools to import and use a helper provided by CFFI,
which in turn executes the file ``path/to/foo_build.py`` (as with
``execfile()``) and looks up its global variable called ``ffibuilder``.  You
can also say ``cffi_modules=["path/to/foo_build.py:maker"]``, where
``maker`` names a global function; it is called with no argument and
is supposed to return a ``FFI`` object.


ffi/ffibuilder.include(): combining multiple CFFI interfaces
------------------------------------------------------------

**ffi/ffibuilder.include(other_ffi)**: includes the typedefs, structs, unions,
enums and constants defined in another FFI instance.  This is meant
for large projects where one CFFI-based interface depends on some
types declared in a different CFFI-based interface.

*Note that you should only use one ffi object per library; the intended
usage of ffi.include() is if you want to interface with several
inter-dependent libraries.*  For only one library, make one ``ffi``
object.  (You can write several ``cdef()`` calls over the same ``ffi``
from several Python files, if one file would be too large.)

For out-of-line modules, the ``ffibuilder.include(other_ffibuilder)``
line should
occur in the build script, and the ``other_ffibuilder`` argument should be
another FFI instance that comes from another build script.  When the two build
scripts are turned into generated files, say ``_ffi.so`` and
``_other_ffi.so``, then importing ``_ffi.so`` will internally cause
``_other_ffi.so`` to be imported.  At that point, the real
declarations from ``_other_ffi.so`` are combined with the real
declarations from ``_ffi.so``.

The usage of ``ffi.include()`` is the cdef-level equivalent of a
``#include`` in C, where a part of the program might include types and
functions defined in another part for its own usage.  You can see on
the ``ffi`` object (and associated ``lib`` objects on the *including*
side) the types and constants declared on the included side.  In API
mode, you can also see the functions and global variables directly.
In ABI mode, these must be accessed via the original ``other_lib``
object returned by the ``dlopen()`` method on ``other_ffi``.


ffi.cdef() limitations
----------------------

All of the ANSI C *declarations* should be supported in ``cdef()``,
and some of C99.  (This excludes any ``#include`` or ``#ifdef``.)
Known missing features that are either in C99, or are GCC or MSVC
extensions:

* Any ``__attribute__`` or ``#pragma pack(n)``

* Additional types: special-size floating and fixed
  point types, vector types, and so on.

* The C99 types ``float _Complex`` and ``double _Complex`` are supported
  by cffi since version 1.11, but not libffi: you cannot call C
  functions with complex arguments or return value, except if they are
  directly API-mode functions.  The type ``long double _Complex`` is not
  supported at all (declare and use it as if it were an array of two
  ``long double``, and write wrapper functions in C with set_source()).

* ``__restrict__`` or ``__restrict`` are extensions of, respectively,
   GCC and MSVC.  They are not recognized.  But ``restrict`` is a C
   keyword and is accepted (and ignored).

Note that declarations like ``int field[];`` in
structures are interpreted as variable-length structures.  Declarations
like ``int field[...];`` on the other hand are arrays whose length is
going to be completed by the compiler.  You can use ``int field[];``
for array fields that are not, in fact, variable-length; it works too,
but in this case, as CFFI
believes it cannot ask the C compiler for the length of the array, you
get reduced safety checks: for example, you risk overwriting the
following fields by passing too many array items in the constructor.

*New in version 1.2:*
Thread-local variables (``__thread``) can be accessed, as well as
variables defined as dynamic macros (``#define myvar  (*fetchme())``).
Before version 1.2, you need to write getter/setter functions.

Note that if you declare a variable in ``cdef()`` without using
``const``, CFFI assumes it is a read-write variable and generates two
pieces of code, one to read it and one to write it.  If the variable
cannot in fact be written to in C code, for one reason or another, it
will not compile.  In this case, you can declare it as a constant: for
example, instead of ``foo_t *myglob;`` you would use ``foo_t *const
myglob;``.  Note also that ``const foo_t *myglob;``  is a *variable;* it
contains a variable pointer to a constant ``foo_t``.


Debugging dlopen'ed C libraries
-------------------------------

A few C libraries are actually hard to use correctly in a ``dlopen()``
setting.  This is because most C libraries are intended for, and tested
with, a situation where they are *linked* with another program, using
either static linking or dynamic linking --- but from a program written
in C, at start-up, using the linker's capabilities instead of
``dlopen()``.

This can occasionally create issues.  You would have the same issues in
another setting than CFFI, like with ``ctypes`` or even plain C code that
calls ``dlopen()``.  This section contains a few generally useful
environment variables (on Linux) that can help when debugging these
issues.

**export LD_TRACE_LOADED_OBJECTS=all**

    provides a lot of information, sometimes too much depending on the
    setting.  Output verbose debugging information about the dynamic
    linker. If set to ``all`` prints all debugging information it has, if
    set to ``help`` prints a help message about which categories can be
    specified in this environment variable

**export LD_VERBOSE=1**

    (glibc since 2.1) If set to a nonempty string, output symbol
    versioning information about the program if querying information
    about the program (i.e., either ``LD_TRACE_LOADED_OBJECTS`` has been set,
    or ``--list`` or ``--verify`` options have been given to the dynamic
    linker).

**export LD_WARN=1**

    (ELF only)(glibc since 2.1.3) If set to a nonempty string, warn
    about unresolved symbols.


ffi.verify(): in-line API-mode
------------------------------

**ffi.verify()** is supported for backward compatibility, but is
deprecated.  ``ffi.verify(c_header_source, tmpdir=.., ext_package=..,
modulename=.., flags=.., **kwargs)`` makes and compiles a C file from
the ``ffi.cdef()``, like ``ffi.set_source()`` in API mode, and then
immediately loads and returns the dynamic library object.  Some
non-trivial logic is used to decide if the dynamic library must be
recompiled or not; see below for ways to control it.

The ``c_header_source`` and the extra keyword arguments have the
same meaning as in ``ffi.set_source()``.

One remaining use case for ``ffi.verify()`` would be the following
hack to find explicitly the size of any type, in bytes, and have it
available in Python immediately (e.g. because it is needed in order to
write the rest of the build script):

.. code-block:: python

    ffi = cffi.FFI()
    ffi.cdef("const int mysize;")
    lib = ffi.verify("const int mysize = sizeof(THE_TYPE);")
    print lib.mysize

Extra arguments to ``ffi.verify()``:
    
*  ``tmpdir`` controls where the C
   files are created and compiled. Unless the ``CFFI_TMPDIR`` environment
   variable is set, the default is
   ``directory_containing_the_py_file/__pycache__`` using the
   directory name of the .py file that contains the actual call to
   ``ffi.verify()``.  (This is a bit of a hack but is generally
   consistent with the location of the .pyc files for your library.
   The name ``__pycache__`` itself comes from Python 3.)

*  ``ext_package`` controls in which package the
   compiled extension module should be looked from.  This is
   only useful after distributing ffi.verify()-based modules.

*  The ``tag`` argument gives an extra string inserted in the
   middle of the extension module's name: ``_cffi_<tag>_<hash>``.
   Useful to give a bit more context, e.g. when debugging.

*  The ``modulename`` argument can be used to force a specific module
   name, overriding the name ``_cffi_<tag>_<hash>``.  Use with care,
   e.g. if you are passing variable information to ``verify()`` but
   still want the module name to be always the same (e.g. absolute
   paths to local files).  In this case, no hash is computed and if
   the module name already exists it will be reused without further
   check.  Be sure to have other means of clearing the ``tmpdir``
   whenever you change your sources.

* ``source_extension`` has the same meaning as in ``ffibuilder.set_source()``.

*  The optional ``flags`` argument (ignored on Windows) defaults to
   ``ffi.RTLD_NOW``; see ``man dlopen``.  (With
   ``ffibuilder.set_source()``, you would use ``sys.setdlopenflags()``.)

*  The optional ``relative_to`` argument is useful if you need to list
   local files passed to the C compiler::

     ext = ffi.verify(..., sources=['foo.c'], relative_to=__file__)

   The line above is roughly the same as::

     ext = ffi.verify(..., sources=['/path/to/this/file/foo.c'])

   except that the default name of the produced library is built from
   the CRC checkum of the argument ``sources``, as well as most other
   arguments you give to ``ffi.verify()`` -- but not ``relative_to``.
   So if you used the second line, it would stop finding the
   already-compiled library after your project is installed, because
   the ``'/path/to/this/file'`` suddenly changed.  The first line does
   not have this problem.

Note that during development, every time you change the C sources that
you pass to ``cdef()`` or ``verify()``, then the latter will create a
new module file name, based on two CRC32 hashes computed from these
strings.  This creates more and more files in the ``__pycache__``
directory.  It is recommended that you clean it up from time to time.
A nice way to do that is to add, in your test suite, a call to
``cffi.verifier.cleanup_tmpdir()``.  Alternatively, you can manually
remove the whole ``__pycache__`` directory.

An alternative cache directory can be given as the ``tmpdir`` argument
to ``verify()``, via the environment variable ``CFFI_TMPDIR``, or by
calling ``cffi.verifier.set_tmpdir(path)`` prior to calling
``verify``.


Upgrading from CFFI 0.9 to CFFI 1.0
-----------------------------------

CFFI 1.0 is backward-compatible, but it is still a good idea to
consider moving to the out-of-line approach new in 1.0.  Here are the
steps.

**ABI mode** if your CFFI project uses ``ffi.dlopen()``:

.. code-block:: python

    import cffi

    ffi = cffi.FFI()
    ffi.cdef("stuff")
    lib = ffi.dlopen("libpath")

and *if* the "stuff" part is big enough that import time is a concern,
then rewrite it as described in `the out-of-line but still ABI mode`__
above.  Optionally, see also the `setuptools integration`__ paragraph.

.. __: out-of-line-abi_
.. __: distutils-setuptools_


**API mode** if your CFFI project uses ``ffi.verify()``:

.. code-block:: python

    import cffi

    ffi = cffi.FFI()
    ffi.cdef("stuff")
    lib = ffi.verify("real C code")

then you should really rewrite it as described in `the out-of-line,
API mode`__ above.  It avoids a number of issues that have caused
``ffi.verify()`` to grow a number of extra arguments over time.  Then
see the `distutils or setuptools`__ paragraph.  Also, remember to
remove the ``ext_package=".."`` from your ``setup.py``, which was
sometimes needed with ``verify()`` but is just creating confusion with
``set_source()``.

.. __: out-of-line-api_
.. __: distutils-setuptools_

The following example should work both with old (pre-1.0) and new
versions of CFFI---supporting both is important to run on old
versions of PyPy (CFFI 1.0 does not work in PyPy < 2.6):

.. code-block:: python

    # in a separate file "package/foo_build.py"
    import cffi

    ffi = cffi.FFI()
    C_HEADER_SRC = r'''
        #include "somelib.h"
    '''
    C_KEYWORDS = dict(libraries=['somelib'])

    if hasattr(ffi, 'set_source'):
        ffi.set_source("package._foo", C_HEADER_SRC, **C_KEYWORDS)

    ffi.cdef('''
        int foo(int);
    ''')

    if __name__ == "__main__":
        ffi.compile()

And in the main program:

.. code-block:: python

    try:
        from package._foo import ffi, lib
    except ImportError:
        from package.foo_build import ffi, C_HEADER_SRC, C_KEYWORDS
        lib = ffi.verify(C_HEADER_SRC, **C_KEYWORDS)

(FWIW, this latest trick can be used more generally to allow the
import to "work" even if the ``_foo`` module was not generated.)

Writing a ``setup.py`` script that works both with CFFI 0.9 and 1.0
requires explicitly checking the version of CFFI that we can have---it
is hard-coded as a built-in module in PyPy:

.. code-block:: python

    if '_cffi_backend' in sys.builtin_module_names:   # PyPy
        import _cffi_backend
        requires_cffi = "cffi==" + _cffi_backend.__version__
    else:
        requires_cffi = "cffi>=1.0.0"

Then we use the ``requires_cffi`` variable to give different arguments to
``setup()`` as needed, e.g.:

.. code-block:: python

    if requires_cffi.startswith("cffi==0."):
        # backward compatibility: we have "cffi==0.*"
        from package.foo_build import ffi
        extra_args = dict(
            ext_modules=[ffi.verifier.get_extension()],
            ext_package="...",    # if needed
        )
    else:
        extra_args = dict(
            setup_requires=[requires_cffi],
            cffi_modules=['package/foo_build.py:ffi'],
        )
    setup(
        name=...,
        ...,
        install_requires=[requires_cffi],
        **extra_args
    )

=======================================================
Overview
=======================================================

.. contents::
   

The first section presents a simple working
example of using CFFI to call a C function in a compiled shared object
(DLL) from Python. CFFI is
flexible and covers several other use cases presented in the second
section. The third section shows how to export Python functions
to a Python interpreter embedded in a C or C++ application. The last
two sections delve deeper in the CFFI library.

Make sure you have `cffi installed`__.

.. __: installation.html

.. _out-of-line-api-level:
.. _real-example:


Main mode of usage
------------------

The main way to use CFFI is as an interface to some already-compiled
shared object which is provided by other means.  Imagine that you have a
system-installed shared object called ``piapprox.dll`` (Windows) or
``libpiapprox.so`` (Linux and others) or ``libpiapprox.dylib`` (OS X),
exporting a function ``float pi_approx(int n);`` that computes some
approximation of pi given a number of iterations. You want to call
this function from Python. Note this method works equally well with a
static library ``piapprox.lib`` (Windows) or ``libpiapprox.a``.

Create the file ``piapprox_build.py``:

.. code-block:: python

      from cffi import FFI
      ffibuilder = FFI()

      # cdef() expects a single string declaring the C types, functions and
      # globals needed to use the shared object. It must be in valid C syntax.
      ffibuilder.cdef("""
          float pi_approx(int n);
      """)

      # set_source() gives the name of the python extension module to
      # produce, and some C source code as a string.  This C code needs
      # to make the declarated functions, types and globals available,
      # so it is often just the "#include".
      ffibuilder.set_source("_pi_cffi",
      """
      	   #include "pi.h"   // the C header of the library
      """,
      	   libraries=['piapprox'])   # library name, for the linker

      if __name__ == "__main__":
          ffibuilder.compile(verbose=True)

Execute this script.  If everything is OK, it should produce
``_pi_cffi.c``, and then invoke the compiler on it.  The produced
``_pi_cffi.c`` contains a copy of the string given in ``set_source()``,
in this example the ``#include "pi.h"``. Afterwards, it contains glue code
for all the functions, types and globals declared in the ``cdef()`` above.

At runtime, you use the extension module like this:

.. code-block:: python

    from _pi_cffi import ffi, lib
    print(lib.pi_approx(5000))

That's all!  In the rest of this page, we describe some more advanced
examples and other CFFI modes.  In particular, there is a complete
example `if you don't have an already-installed C library to call`_.

For more information about the ``cdef()`` and ``set_source()`` methods
of the ``FFI`` class, see `Preparing and Distributing modules`__.

.. __: cdef.html

When your example works, a common alternative to running the build
script manually is to have it run as part of a ``setup.py``.  Here is
an example using the Setuptools distribution:

.. code-block:: python

    from setuptools import setup

    setup(
        ...
        setup_requires=["cffi>=1.0.0"],
        cffi_modules=["piapprox_build:ffibuilder"], # "filename:global"
        install_requires=["cffi>=1.0.0"],
    )


Other CFFI modes
----------------

CFFI can be used in one of four modes: "ABI" versus "API" level,
each with "in-line" or "out-of-line" preparation (or compilation).

The **ABI mode** accesses libraries at the binary level, whereas the
faster **API mode** accesses them with a C compiler.  We explain the
difference in more details below__.

.. __: `abi-versus-api`_

In the **in-line mode,** everything is set up every time you import
your Python code.  In the **out-of-line mode,** you have a separate
step of preparation (and possibly C compilation) that produces a
module which your main program can then import.


Simple example (ABI level, in-line)
+++++++++++++++++++++++++++++++++++

May look familiar to those who have used ctypes_.

.. code-block:: python

    >>> from cffi import FFI
    >>> ffi = FFI()
    >>> ffi.cdef("""
    ...     int printf(const char *format, ...);   // copy-pasted from the man page
    ... """)                                  
    >>> C = ffi.dlopen(None)                     # loads the entire C namespace
    >>> arg = ffi.new("char[]", b"world")        # equivalent to C code: char arg[] = "world";
    >>> C.printf(b"hi there, %s.\n", arg)        # call printf
    hi there, world.
    17                                           # this is the return value
    >>>

Note that ``char *`` arguments expect a ``bytes`` object.  If you have a
``str`` (or a ``unicode`` on Python 2) you need to encode it explicitly
with ``somestring.encode(myencoding)``.

*Python 3 on Windows:* ``ffi.dlopen(None)`` does not work.  This problem
is messy and not really fixable.  The problem does not occur if you try
to call a function from a specific DLL that exists on your system: then
you use ``ffi.dlopen("path.dll")``.

*This example does not call any C compiler.  It works in the so-called
ABI mode, which means that it will crash if you call some function or
access some fields of a structure that was slightly misdeclared in the
cdef().*

If using a C compiler to install your module is an option, it is highly
recommended to use the API mode instead.  (It is also faster.)


Struct/Array Example (minimal, in-line)
+++++++++++++++++++++++++++++++++++++++

.. code-block:: python

    from cffi import FFI
    ffi = FFI()
    ffi.cdef("""
        typedef struct {
            unsigned char r, g, b;
        } pixel_t;
    """)
    image = ffi.new("pixel_t[]", 800*600)

    f = open('data', 'rb')     # binary mode -- important
    f.readinto(ffi.buffer(image))
    f.close()

    image[100].r = 255
    image[100].g = 192
    image[100].b = 128

    f = open('data', 'wb')
    f.write(ffi.buffer(image))
    f.close()

This can be used as a more flexible replacement of the struct_ and
array_ modules, and replaces ctypes_.  You could also call ``ffi.new("pixel_t[600][800]")``
and get a two-dimensional array.

.. _struct: http://docs.python.org/library/struct.html
.. _array: http://docs.python.org/library/array.html
.. _ctypes: http://docs.python.org/library/ctypes.html

*This example does not call any C compiler.*

This example also admits an out-of-line equivalent.  It is similar to
the first example `Main mode of usage`_ above,
but passing ``None`` as the second argument to
``ffibuilder.set_source()``.  Then in the main program you write
``from _simple_example import ffi`` and then the same content as the
in-line example above starting from the line ``image =
ffi.new("pixel_t[]", 800*600)``.


API Mode, calling the C standard library
++++++++++++++++++++++++++++++++++++++++

.. code-block:: python

    # file "example_build.py"

    # Note: we instantiate the same 'cffi.FFI' class as in the previous
    # example, but call the result 'ffibuilder' now instead of 'ffi';
    # this is to avoid confusion with the other 'ffi' object you get below

    from cffi import FFI
    ffibuilder = FFI()

    ffibuilder.set_source("_example",
       r""" // passed to the real C compiler,
            // contains implementation of things declared in cdef()
            #include <sys/types.h>
            #include <pwd.h>

            // We can also define custom wrappers or other functions
            // here (this is an example only):
            static struct passwd *get_pw_for_root(void) {
                return getpwuid(0);
            }
        """,
        libraries=[])   # or a list of libraries to link with
        # (more arguments like setup.py's Extension class:
        # include_dirs=[..], extra_objects=[..], and so on)

    ffibuilder.cdef("""
        // declarations that are shared between Python and C
        struct passwd {
            char *pw_name;
            ...;     // literally dot-dot-dot
        };
        struct passwd *getpwuid(int uid);     // defined in <pwd.h>
        struct passwd *get_pw_for_root(void); // defined in set_source()
    """)

    if __name__ == "__main__":
        ffibuilder.compile(verbose=True)

You need to run the ``example_build.py`` script once to generate
"source code" into the file ``_example.c`` and compile this to a
regular C extension module.  (CFFI selects either Python or C for the
module to generate based on whether the second argument to
``set_source()`` is ``None`` or not.)

*You need a C compiler for this single step.  It produces a file called
e.g. _example.so or _example.pyd.  If needed, it can be distributed in
precompiled form like any other extension module.*

Then, in your main program, you use:

.. code-block:: python

    from _example import ffi, lib

    p = lib.getpwuid(0)
    assert ffi.string(p.pw_name) == b'root'
    p = lib.get_pw_for_root()
    assert ffi.string(p.pw_name) == b'root'

Note that this works independently of the exact C layout of ``struct
passwd`` (it is "API level", as opposed to "ABI level").  It requires
a C compiler in order to run ``example_build.py``, but it is much more
portable than trying to get the details of the fields of ``struct
passwd`` exactly right.  Similarly, in the ``cdef()`` we declared
``getpwuid()`` as taking an ``int`` argument; on some platforms this
might be slightly incorrect---but it does not matter.

Note also that at runtime, the API mode is faster than the ABI mode.

To integrate it inside a ``setup.py`` distribution with Setuptools:

.. code-block:: python

    from setuptools import setup

    setup(
        ...
        setup_requires=["cffi>=1.0.0"],
        cffi_modules=["example_build.py:ffibuilder"],
        install_requires=["cffi>=1.0.0"],
    )


.. _`if you don't have an already-installed C library to call`:

API Mode, calling C sources instead of a compiled library
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++

If you want to call some library that is not precompiled, but for which
you have C sources, then the easiest solution is to make a single
extension module that is compiled from both the C sources of this
library, and the additional CFFI wrappers.  For example, say you start
with the files ``pi.c`` and ``pi.h``:

   .. code-block:: C

      /* filename: pi.c*/
      # include <stdlib.h>
      # include <math.h>
       
      /* Returns a very crude approximation of Pi
         given a int: a number of iteration */
      float pi_approx(int n){
      
        double i,x,y,sum=0;
      
        for(i=0;i<n;i++){
      
          x=rand();
          y=rand();
      
          if (sqrt(x*x+y*y) < sqrt((double)RAND_MAX*RAND_MAX))
            sum++; }
      
        return 4*(float)sum/(float)n; }

   .. code-block:: C

      /* filename: pi.h*/
      float pi_approx(int n);
      
Create a script named ``pi_extension_build.py``, building
the C extension:

   .. code-block:: python

      from cffi import FFI
      ffibuilder = FFI()
      
      ffibuilder.cdef("float pi_approx(int n);")
   
      ffibuilder.set_source("_pi",  # name of the output C extension
      """
          #include "pi.h"
      """,
          sources=['pi.c'],   # includes pi.c as additional sources
          libraries=['m'])    # on Unix, link with the math library
   
      if __name__ == "__main__":
          ffibuilder.compile(verbose=True)

Build the extension:
   
   .. code-block:: shell

      python pi_extension_build.py

Observe, in the working directory, the generated output files:
``_pi.c``, ``_pi.o`` and the compiled C extension (called ``_pi.so`` on
Linux for example).  It can be called from Python:

   .. code-block:: python
   
       from _pi.lib import pi_approx
   
       approx = pi_approx(10)
       assert str(approx).startswith("3.")
   
       approx = pi_approx(10000)
       assert str(approx).startswith("3.1")  


.. _performance:

Purely for performance (API level, out-of-line)
+++++++++++++++++++++++++++++++++++++++++++++++

A variant of the `section above`__ where the goal is not to call an
existing C library, but to compile and call some C function written
directly in the build script:

.. __: real-example_

.. code-block:: python

    # file "example_build.py"

    from cffi import FFI
    ffibuilder = FFI()

    ffibuilder.cdef("int foo(int *, int *, int);")

    ffibuilder.set_source("_example",
    r"""
        static int foo(int *buffer_in, int *buffer_out, int x)
        {
            /* some algorithm that is seriously faster in C than in Python */
        }
    """)

    if __name__ == "__main__":
        ffibuilder.compile(verbose=True)

.. code-block:: python

    # file "example.py"

    from _example import ffi, lib

    buffer_in = ffi.new("int[]", 1000)
    # initialize buffer_in here...

    # easier to do all buffer allocations in Python and pass them to C,
    # even for output-only arguments
    buffer_out = ffi.new("int[]", 1000)

    result = lib.foo(buffer_in, buffer_out, 1000)

*You need a C compiler to run example_build.py, once.  It produces a
file called e.g. _example.so or _example.pyd.  If needed, it can be
distributed in precompiled form like any other extension module.*


.. _out-of-line-abi-level:

Out-of-line, ABI level
++++++++++++++++++++++

The out-of-line ABI mode is a mixture of the regular (API) out-of-line
mode and the in-line ABI mode.  It lets you use the ABI mode, with its
advantages (not requiring a C compiler) and problems (crashes more
easily).

This mixture mode lets you massively reduces the import times, because
it is slow to parse a large C header.  It also allows you to do more
detailed checkings during build-time without worrying about performance
(e.g. calling ``cdef()`` many times with small pieces of declarations,
based on the version of libraries detected on the system).

.. code-block:: python

    # file "simple_example_build.py"

    from cffi import FFI

    ffibuilder = FFI()
    # Note that the actual source is None
    ffibuilder.set_source("_simple_example", None)
    ffibuilder.cdef("""
        int printf(const char *format, ...);
    """)

    if __name__ == "__main__":
        ffibuilder.compile(verbose=True)

Running it once produces ``_simple_example.py``.  Your main program
only imports this generated module, not ``simple_example_build.py``
any more:

.. code-block:: python

    from _simple_example import ffi

    lib = ffi.dlopen(None)      # Unix: open the standard C library
    #import ctypes.util         # or, try this on Windows:
    #lib = ffi.dlopen(ctypes.util.find_library("c"))

    lib.printf(b"hi there, number %d\n", ffi.cast("int", 2))

Note that this ``ffi.dlopen()``, unlike the one from in-line mode,
does not invoke any additional magic to locate the library: it must be
a path name (with or without a directory), as required by the C
``dlopen()`` or ``LoadLibrary()`` functions.  This means that
``ffi.dlopen("libfoo.so")`` is ok, but ``ffi.dlopen("foo")`` is not.
In the latter case, you could replace it with
``ffi.dlopen(ctypes.util.find_library("foo"))``.  Also, None is only
recognized on Unix to open the standard C library.

For distribution purposes, remember that there is a new
``_simple_example.py`` file generated.  You can either include it
statically within your project's source files, or, with Setuptools,
you can say in the ``setup.py``:

.. code-block:: python

    from setuptools import setup

    setup(
        ...
        setup_requires=["cffi>=1.0.0"],
        cffi_modules=["simple_example_build.py:ffibuilder"],
        install_requires=["cffi>=1.0.0"],
    )

In summary, this mode is useful when you wish to declare many C structures but
do not need fast interaction with a shared object. It is useful for parsing
binary files, for instance.


In-line, API level
++++++++++++++++++

The "API level + in-line" mode combination exists but is long
deprecated.  It used to be done with ``lib = ffi.verify("C header")``.
The out-of-line variant with ``set_source("modname", "C header")`` is
preferred and avoids a number of problems when the project grows in
size.


.. _embedding:

Embedding
---------

*New in version 1.5.*

CFFI can be used for embedding__: creating a standard
dynamically-linked library (``.dll`` under Windows, ``.so`` elsewhere)
which can be used from a C application.

.. code-block:: python

    import cffi
    ffibuilder = cffi.FFI()

    ffibuilder.embedding_api("""
        int do_stuff(int, int);
    """)

    ffibuilder.set_source("my_plugin", "")

    ffibuilder.embedding_init_code("""
        from my_plugin import ffi

        @ffi.def_extern()
        def do_stuff(x, y):
            print("adding %d and %d" % (x, y))
            return x + y
    """)

    ffibuilder.compile(target="plugin-1.5.*", verbose=True)

This simple example creates ``plugin-1.5.dll`` or ``plugin-1.5.so`` as
a DLL with a single exported function, ``do_stuff()``.  You execute
the script above once, with the interpreter you want to have
internally used; it can be CPython 2.x or 3.x or PyPy.  This DLL can
then be used "as usual" from an application; the application doesn't
need to know that it is talking with a library made with Python and
CFFI.  At runtime, when the application calls ``int do_stuff(int,
int)``, the Python interpreter is automatically initialized and ``def
do_stuff(x, y):`` gets called.  `See the details in the documentation
about embedding.`__

.. __: embedding.html
.. __: embedding.html


What actually happened?
-----------------------

The CFFI interface operates on the same level as C - you declare types
and functions using the same syntax as you would define them in C.  This
means that most of the documentation or examples can be copied straight
from the man pages.

The declarations can contain **types, functions, constants**
and **global variables.** What you pass to the ``cdef()`` must not
contain more than that; in particular, ``#ifdef`` or ``#include``
directives are not supported.  The cdef in the above examples are just
that - they declared "there is a function in the C level with this
given signature", or "there is a struct type with this shape".

In the ABI examples, the ``dlopen()`` calls load libraries manually.
At the binary level, a program is split into multiple namespaces---a
global one (on some platforms), plus one namespace per library.  So
``dlopen()`` returns a ``<FFILibrary>`` object, and this object has
got as attributes all function, constant and variable symbols that are
coming from this library and that have been declared in the
``cdef()``.  If you have several interdependent libraries to load,
you would call ``cdef()`` only once but ``dlopen()`` several times.

By opposition, the API mode works more closely like a C program: the C
linker (static or dynamic) is responsible for finding any symbol used.
You name the libraries in the ``libraries`` keyword argument to
``set_source()``, but never need to say which symbol comes
from which library.
Other common arguments to ``set_source()`` include ``library_dirs`` and
``include_dirs``; all these arguments are passed to the standard
distutils/setuptools.

The ``ffi.new()`` lines allocate C objects.  They are filled
with zeroes initially, unless the optional second argument is used.
If specified, this argument gives an "initializer", like you can use
with C code to initialize global variables.

The actual ``lib.*()`` function calls should be obvious: it's like C.


.. _abi-versus-api:

ABI versus API
--------------

Accessing the C library at the binary level ("ABI") is fraught
with problems, particularly on non-Windows platforms.

The most immediate drawback of the ABI level is that calling functions
needs to go through the very general *libffi* library, which is slow
(and not always perfectly tested on non-standard platforms).  The API
mode instead compiles a CPython C wrapper that directly invokes the
target function.  It can be massively faster (and works
better than libffi ever will).

The more fundamental reason to prefer the API mode is that *the C
libraries are typically meant to be used with a C compiler.* You are not
supposed to do things like guess where fields are in the structures.
The "real example" above shows how CFFI uses a C compiler under the
hood: this example uses ``set_source(..., "C source...")`` and never
``dlopen()``.  When using this approach,
we have the advantage that we can use literally "``...``" at various places in
the ``cdef()``, and the missing information will be completed with the
help of the C compiler.  CFFI will turn this into a single C source file,
which contains the "C source" part unmodified, followed by some
"magic" C code and declarations derived from the ``cdef()``.  When
this C file is compiled, the resulting C extension module will contain
all the information we need---or the C compiler will give warnings or
errors, as usual e.g. if we misdeclare some function's signature.

Note that the "C source" part from ``set_source()`` can contain
arbitrary C code.  You can use this to declare some
more helper functions written in C.  To export
these helpers to Python, put their signature in the ``cdef()`` too.
(You can use the ``static`` C keyword in the "C source" part,
as in ``static int myhelper(int x) { return x * 42; }``,
because these helpers are only
referenced from the "magic" C code that is generated afterwards in the
same C file.)

This can be used for example to wrap "crazy" macros into more standard
C functions.  The extra layer of C can be useful for other reasons
too, like calling functions that expect some complicated argument
structures that you prefer to build in C rather than in Python.  (On
the other hand, if all you need is to call "function-like" macros,
then you can directly declare them in the ``cdef()`` as if they were
functions.)

The generated piece of C code should be the same independently on the
platform on which you run it (or the Python version), so in simple cases
you can directly distribute the pre-generated C code and treat it as a
regular C extension module (which depends on the ``_cffi_backend``
module, on CPython).  The special Setuptools lines in the `example
above`__ are meant for the more complicated cases where we need to
regenerate the C sources as well---e.g. because the Python script that
regenerates this file will itself look around the system to know what it
should include or not.

.. __: real-example_

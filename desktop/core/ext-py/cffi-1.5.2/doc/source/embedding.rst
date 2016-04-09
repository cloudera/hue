================================
Using CFFI for embedding
================================

.. contents::

You can use CFFI to generate a ``.so/.dll/.dylib`` which exports the
API of your choice to any C application that wants to link with this
``.so/.dll/.dylib``.

The general idea is as follows:

* You write and execute a Python script, which produces a
  ``.so/.dll/.dylib`` file with the API of your choice.  The script
  also gives some Python code to be "frozen" inside the ``.so``.

* At runtime, the C application loads this ``.so/.dll/.dylib`` without
  having to know that it was produced by Python and CFFI.

* The first time a C function is called, Python is initialized and
  the frozen Python code is executed.

* The frozen Python code attaches Python functions that implement the
  C functions of your API, which are then used for all subsequent C
  function calls.

One of the goals of this approach is to be entirely independent from
the CPython C API: no ``Py_Initialize()`` nor ``PyRun_SimpleString()``
nor even ``PyObject``.  It works identically on CPython and PyPy.

.. note:: PyPy release 4.0.1 contains CFFI 1.4 only.

This is entirely *new in version 1.5.*


Usage
-----

.. __: overview.html#embedding

See the `paragraph in the overview page`__ for a quick introduction.
In this section, we explain every step in more details.  We will use
here this slightly expanded example:

.. code-block:: c

    /* file plugin.h */
    typedef struct { int x, y; } point_t;
    extern int do_stuff(point_t *);

.. code-block:: python

    # file plugin_build.py
    import cffi
    ffi = cffi.FFI()

    with open('plugin.h') as f:
        ffi.embedding_api(f.read())

    ffi.set_source("my_plugin", '''
        #include "plugin.h"
    ''')

    ffi.embedding_init_code("""
        from my_plugin import ffi

        @ffi.def_extern()
        def do_stuff(p):
            print("adding %d and %d" % (p.x, p.y))
            return p.x + p.y
    """)

    ffi.compile(target="plugin-1.5.*", verbose=True)

Running the code above produces a *DLL*, i,e, a dynamically-loadable
library.  It is a file with the extension ``.dll`` on Windows,
``.dylib`` on Mac OS/X, or ``.so`` on other platforms.  As usual, it
is produced by generating some intermediate ``.c`` code and then
calling the regular platform-specific C compiler.

Here are some details about the methods used above:

* **ffi.embedding_api(source):** parses the given C source, which
  declares functions that you want to be exported by the DLL.  It can
  also declare types, constants and global variables that are part of
  the C-level API of your DLL.

  The functions that are found in ``source`` will be automatically
  defined in the ``.c`` file: they will contain code that initializes
  the Python interpreter the first time any of them is called,
  followed by code to call the attached Python function (with
  ``@ffi.def_extern()``, see next point).

  The global variables, on the other hand, are not automatically
  produced.  You have to write their definition explicitly in
  ``ffi.set_source()``, as regular C code (see the point after next).

* **ffi.embedding_init_code(python_code):** this gives
  initialization-time Python source code.  This code is copied
  ("frozen") inside the DLL.  At runtime, the code is executed when
  the DLL is first initialized, just after Python itself is
  initialized.  This newly initialized Python interpreter has got an
  extra "built-in" module that can be loaded magically without
  accessing any files, with a line like "``from my_plugin import ffi,
  lib``".  The name ``my_plugin`` comes from the first argument to
  ``ffi.set_source()``.  This module represents "the caller's C world"
  from the point of view of Python.

  The initialization-time Python code can import other modules or
  packages as usual.  You may have typical Python issues like needing
  to set up ``sys.path`` somehow manually first.

  For every function declared within ``ffi.embedding_api()``, the
  initialization-time Python code or one of the modules it imports
  should use the decorator ``@ffi.def_extern()`` to attach a
  corresponding Python function to it.

  If the initialization-time Python code fails with an exception, then
  you get a traceback printed to stderr, along with more information
  to help you identify problems like wrong ``sys.path``.  If some
  function remains unattached at the time where the C code tries to
  call it, an error message is also printed to stderr and the function
  returns zero/null.

  Note that the CFFI module never calls ``exit()``, but CPython itself
  contains code that calls ``exit()``, for example if importing
  ``site`` fails.  This may be worked around in the future.

* **ffi.set_source(c_module_name, c_code):** set the name of the
  module from Python's point of view.  It also gives more C code which
  will be included in the generated C code.  In trivial examples it
  can be an empty string.  It is where you would ``#include`` some
  other files, define global variables, and so on.  The macro
  ``CFFI_DLLEXPORT`` is available to this C code: it expands to the
  platform-specific way of saying "the following declaration should be
  exported from the DLL".  For example, you would put "``extern int
  my_glob;``" in ``ffi.embedding_api()`` and "``CFFI_DLLEXPORT int
  my_glob = 42;``" in ``ffi.set_source()``.

  Currently, any *type* declared in ``ffi.embedding_api()`` must also
  be present in the ``c_code``.  This is automatic if this code
  contains a line like ``#include "plugin.h"`` in the example above.

* **ffi.compile([target=...] [, verbose=True]):** make the C code and
  compile it.  By default, it produces a file called
  ``c_module_name.dll``, ``c_module_name.dylib`` or
  ``c_module_name.so``, but the default can be changed with the
  optional ``target`` keyword argument.  You can use
  ``target="foo.*"`` with a literal ``*`` to ask for a file called
  ``foo.dll`` on Windows, ``foo.dylib`` on OS/X and ``foo.so``
  elsewhere.  One reason for specifying an alternate ``target`` is to
  include characters not usually allowed in Python module names, like
  "``plugin-1.5.*``".

  For more complicated cases, you can call instead
  ``ffi.emit_c_code("foo.c")`` and compile the resulting ``foo.c``
  file using other means.  CFFI's compilation logic is based on the
  standard library ``distutils`` package, which is really developed
  and tested for the purpose of making CPython extension modules, not
  other DLLs.


More reading
------------

If you're reading this page about embedding and you are not familiar
with CFFI already, here are a few pointers to what you could read
next:

* For the ``@ffi.def_extern()`` functions, integer C types are passed
  simply as Python integers; and simple pointers-to-struct and basic
  arrays are all straightforward enough.  However, sooner or later you
  will need to read about this topic in more details here__.

* ``@ffi.def_extern()``: see `documentation here,`__ notably on what
  happens if the Python function raises an exception.

* To create Python objects attached to C data, one common solution is
  to use ``ffi.new_handle()``.  See documentation here__.

* In embedding mode, the major direction is C code that calls Python
  functions.  This is the opposite of the regular extending mode of
  CFFI, in which the major direction is Python code calling C.  That's
  why the page `Using the ffi/lib objects`_ talks first about the
  latter, and why the direction "C code that calls Python" is
  generally referred to as "callbacks" in that page.  If you also
  need to have your Python code call C code, read more about
  `Embedding and Extending`_ below.

* ``ffi.embedding_api(source)``: follows the same syntax as
  ``ffi.cdef()``, `documented here.`__  You can use the "``...``"
  syntax as well, although in practice it may be less useful than it
  is for ``cdef()``.  On the other hand, it is expected that often the
  C sources that you need to give to ``ffi.embedding_api()`` would be
  exactly the same as the content of some ``.h`` file that you want to
  give to users of your DLL.  That's why the example above does this::

      with open('foo.h') as f:
          ffi.embedding_api(f.read())

  Note that a drawback of this approach is that ``ffi.embedding_api()``
  doesn't support ``#ifdef`` directives.  You may have to use a more
  convoluted expression like::

      with open('foo.h') as f:
          lines = [line for line in f if not line.startswith('#')]
          ffi.embedding_api(''.join(lines))

  As in the example above, you can also use the same ``foo.h`` from
  ``ffi.set_source()``::

      ffi.set_source('module_name', '#include "foo.h"')


.. __: using.html#working
.. __: using.html#def-extern
.. __: using.html#ffi-new_handle
.. __: cdef.html#cdef

.. _`Using the ffi/lib objects`: using.html


Troubleshooting
---------------

The error message

    cffi extension module 'c_module_name' has unknown version 0x2701

means that the running Python interpreter located a CFFI version older
than 1.5.  CFFI 1.5 or newer must be installed in the running Python.


Using multiple CFFI-made DLLs
-----------------------------

Multiple CFFI-made DLLs can be used by the same process.

Note that all CFFI-made DLLs in a process share a single Python
interpreter.  The effect is the same as the one you get by trying to
build a large Python application by assembling a lot of unrelated
packages.  Some of these might be libraries that monkey-patch some
functions from the standard library, for example, which might be
unexpected from other parts.


Multithreading
--------------

Multithreading should work transparently, based on Python's standard
Global Interpreter Lock.

If two threads both try to call a C function when Python is not yet
initialized, then locking occurs.  One thread proceeds with
initialization and blocks the other thread.  The other thread will be
allowed to continue only when the execution of the initialization-time
Python code is done.

If the two threads call two *different* CFFI-made DLLs, the Python
initialization itself will still be serialized, but the two pieces of
initialization-time Python code will not.  The idea is that there is a
priori no reason for one DLL to wait for initialization of the other
DLL to be complete.

After initialization, Python's standard Global Interpreter Lock kicks
in.  The end result is that when one CPU progresses on executing
Python code, no other CPU can progress on executing more Python code
from another thread of the same process.  At regular intervals, the
lock switches to a different thread, so that no single thread should
appear to block indefinitely.


Testing
-------

For testing purposes, a CFFI-made DLL can be imported in a running
Python interpreter instead of being loaded like a C shared library.

You might have some issues with the file name: for example, on
Windows, Python expects the file to be called ``c_module_name.pyd``,
but the CFFI-made DLL is called ``target.dll`` instead.  The base name
``target`` is the one specified in ``ffi.compile()``, and on Windows
the extension is ``.dll`` instead of ``.pyd``.  You have to rename or
copy the file, or on POSIX use a symlink.

The module then works like a regular CFFI extension module.  It is
imported with "``from c_module_name import ffi, lib``" and exposes on
the ``lib`` object all C functions.  You can test it by calling these
C functions.  The initialization-time Python code frozen inside the
DLL is executed the first time such a call is done.


Embedding and Extending
-----------------------

The embedding mode is not incompatible with the non-embedding mode of
CFFI.

You can use *both* ``ffi.embedding_api()`` and ``ffi.cdef()`` in the
same build script.  You put in the former the declarations you want to
be exported by the DLL; you put in the latter only the C functions and
types that you want to share between C and Python, but not export from
the DLL.

As an example of that, consider the case where you would like to have
a DLL-exported C function written in C directly, maybe to handle some
cases before calling Python functions.  To do that, you must *not* put
the function's signature in ``ffi.embedding_api()``.  (Note that this
requires more hacks if you use ``ffi.embedding_api(f.read())``.)  You must
only write the custom function definition in ``ffi.set_source()``, and
prefix it with the macro CFFI_DLLEXPORT:

.. code-block:: c

    CFFI_DLLEXPORT int myfunc(int a, int b)
    {
        /* implementation here */
    }

This function can, if it wants, invoke Python functions using the
general mechanism of "callbacks"---called this way because it is a
call from C to Python, although in this case it is not calling
anything back:

.. code-block:: python

    ffi.cdef("""
        extern "Python" int mycb(int);
    """)

    ffi.set_source("my_plugin", """

        static int mycb(int);   /* the callback: forward declaration, to make
                                   it accessible from the C code that follows */

        CFFI_DLLEXPORT int myfunc(int a, int b)
        {
            int product = a * b;   /* some custom C code */
            return mycb(product);
        }
    """)

and then the Python initialization code needs to contain the lines:

.. code-block:: python

    @ffi.def_extern()
    def mycb(x):
        print "hi, I'm called with x =", x
        return x * 10

This ``@ffi.def_extern`` is attaching a Python function to the C
callback ``mycb()``, which in this case is not exported from the DLL.
Nevertheless, the automatic initialization of Python occurs when
``mycb()`` is called, if it happens to be the first function called
from C.  More precisely, it does not happen when ``myfunc()`` is
called: this is just a C function, with no extra code magically
inserted around it.  It only happens when ``myfunc()`` calls
``mycb()``.

As the above explanation hints, this is how ``ffi.embedding_api()``
actually implements function calls that directly invoke Python code;
here, we have merely decomposed it explicitly, in order to add some
custom C code in the middle.

In case you need to force, from C code, Python to be initialized
before the first ``@ffi.def_extern()`` is called, you can do so by
calling the C function ``cffi_start_python()`` with no argument.  It
returns an integer, 0 or -1, to tell if the initialization succeeded
or not.  Currently there is no way to prevent a failing initialization
from also dumping a traceback and more information to stderr.

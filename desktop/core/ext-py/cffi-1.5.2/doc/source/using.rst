================================
Using the ffi/lib objects
================================

.. contents::

Keep this page under your pillow.


.. _working:

Working with pointers, structures and arrays
--------------------------------------------

The C code's integers and floating-point values are mapped to Python's
regular ``int``, ``long`` and ``float``.  Moreover, the C type ``char``
corresponds to single-character strings in Python.  (If you want it to
map to small integers, use either ``signed char`` or ``unsigned char``.)

Similarly, the C type ``wchar_t`` corresponds to single-character
unicode strings.  Note that in some situations (a narrow Python build
with an underlying 4-bytes wchar_t type), a single wchar_t character
may correspond to a pair of surrogates, which is represented as a
unicode string of length 2.  If you need to convert such a 2-chars
unicode string to an integer, ``ord(x)`` does not work; use instead
``int(ffi.cast('wchar_t', x))``.

Pointers, structures and arrays are more complex: they don't have an
obvious Python equivalent.  Thus, they correspond to objects of type
``cdata``, which are printed for example as
``<cdata 'struct foo_s *' 0xa3290d8>``.

``ffi.new(ctype, [initializer])``: this function builds and returns a
new cdata object of the given ``ctype``.  The ctype is usually some
constant string describing the C type.  It must be a pointer or array
type.  If it is a pointer, e.g. ``"int *"`` or ``struct foo *``, then
it allocates the memory for one ``int`` or ``struct foo``.  If it is
an array, e.g. ``int[10]``, then it allocates the memory for ten
``int``.  In both cases the returned cdata is of type ``ctype``.

The memory is initially filled with zeros.  An initializer can be given
too, as described later.

Example::

    >>> ffi.new("int *")
    <cdata 'int *' owning 4 bytes>
    >>> ffi.new("int[10]")
    <cdata 'int[10]' owning 40 bytes>

    >>> ffi.new("char *")          # allocates only one char---not a C string!
    <cdata 'char *' owning 1 bytes>
    >>> ffi.new("char[]", "foobar")  # this allocates a C string, ending in \0
    <cdata 'char[]' owning 7 bytes>

Unlike C, the returned pointer object has *ownership* on the allocated
memory: when this exact object is garbage-collected, then the memory is
freed.  If, at the level of C, you store a pointer to the memory
somewhere else, then make sure you also keep the object alive for as
long as needed.  (This also applies if you immediately cast the returned
pointer to a pointer of a different type: only the original object has
ownership, so you must keep it alive.  As soon as you forget it, then
the casted pointer will point to garbage!  In other words, the ownership
rules are attached to the *wrapper* cdata objects: they are not, and
cannot, be attached to the underlying raw memory.)  Example:

.. code-block:: python

    global_weakkeydict = weakref.WeakKeyDictionary()

    def make_foo():
        s1   = ffi.new("struct foo *")
        fld1 = ffi.new("struct bar *")
        fld2 = ffi.new("struct bar *")
        s1.thefield1 = fld1
        s1.thefield2 = fld2
        # here the 'fld1' and 'fld2' object must not go away,
        # otherwise 's1.thefield1/2' will point to garbage!
        global_weakkeydict[s1] = (fld1, fld2)
        # now 's1' keeps alive 'fld1' and 'fld2'.  When 's1' goes
        # away, then the weak dictionary entry will be removed.
        return s1

The cdata objects support mostly the same operations as in C: you can
read or write from pointers, arrays and structures.  Dereferencing a
pointer is done usually in C with the syntax ``*p``, which is not valid
Python, so instead you have to use the alternative syntax ``p[0]``
(which is also valid C).  Additionally, the ``p.x`` and ``p->x``
syntaxes in C both become ``p.x`` in Python.

We have ``ffi.NULL`` to use in the same places as the C ``NULL``.
Like the latter, it is actually defined to be ``ffi.cast("void *",
0)``.  For example, reading a NULL pointer returns a ``<cdata 'type *'
NULL>``, which you can check for e.g. by comparing it with
``ffi.NULL``.

There is no general equivalent to the ``&`` operator in C (because it
would not fit nicely in the model, and it does not seem to be needed
here).  But see `ffi.addressof()`_.

Any operation that would in C return a pointer or array or struct type
gives you a fresh cdata object.  Unlike the "original" one, these fresh
cdata objects don't have ownership: they are merely references to
existing memory.

As an exception to the above rule, dereferencing a pointer that owns a
*struct* or *union* object returns a cdata struct or union object
that "co-owns" the same memory.  Thus in this case there are two
objects that can keep the same memory alive.  This is done for cases where
you really want to have a struct object but don't have any convenient
place to keep alive the original pointer object (returned by
``ffi.new()``).

Example:

.. code-block:: python

    # void somefunction(int *);

    x = ffi.new("int *")      # allocate one int, and return a pointer to it
    x[0] = 42                 # fill it
    lib.somefunction(x)       # call the C function
    print x[0]                # read the possibly-changed value

The equivalent of C casts are provided with ``ffi.cast("type", value)``.
They should work in the same cases as they do in C.  Additionally, this
is the only way to get cdata objects of integer or floating-point type::

    >>> x = ffi.cast("int", 42)
    >>> x
    <cdata 'int' 42>
    >>> int(x)
    42

To cast a pointer to an int, cast it to ``intptr_t`` or ``uintptr_t``,
which are defined by C to be large enough integer types (example on 32
bits)::

    >>> int(ffi.cast("intptr_t", pointer_cdata))    # signed
    -1340782304
    >>> int(ffi.cast("uintptr_t", pointer_cdata))   # unsigned
    2954184992L

The initializer given as the optional second argument to ``ffi.new()``
can be mostly anything that you would use as an initializer for C code,
with lists or tuples instead of using the C syntax ``{ .., .., .. }``.
Example::

    typedef struct { int x, y; } foo_t;

    foo_t v = { 1, 2 };            // C syntax
    v = ffi.new("foo_t *", [1, 2]) # CFFI equivalent

    foo_t v = { .y=1, .x=2 };                // C99 syntax
    v = ffi.new("foo_t *", {'y': 1, 'x': 2}) # CFFI equivalent

Like C, arrays of chars can also be initialized from a string, in
which case a terminating null character is appended implicitly::

    >>> x = ffi.new("char[]", "hello")
    >>> x
    <cdata 'char[]' owning 6 bytes>
    >>> len(x)        # the actual size of the array
    6
    >>> x[5]          # the last item in the array
    '\x00'
    >>> x[0] = 'H'    # change the first item
    >>> ffi.string(x) # interpret 'x' as a regular null-terminated string
    'Hello'

Similarly, arrays of wchar_t can be initialized from a unicode string,
and calling ``ffi.string()`` on the cdata object returns the current unicode
string stored in the wchar_t array (adding surrogates if necessary).

Note that unlike Python lists or tuples, but like C, you *cannot* index in
a C array from the end using negative numbers.

More generally, the C array types can have their length unspecified in C
types, as long as their length can be derived from the initializer, like
in C::

    int array[] = { 1, 2, 3, 4 };           // C syntax
    array = ffi.new("int[]", [1, 2, 3, 4])  # CFFI equivalent

As an extension, the initializer can also be just a number, giving
the length (in case you just want zero-initialization)::

    int array[1000];                  // C syntax
    array = ffi.new("int[1000]")      # CFFI 1st equivalent
    array = ffi.new("int[]", 1000)    # CFFI 2nd equivalent

This is useful if the length is not actually a constant, to avoid things
like ``ffi.new("int[%d]" % x)``.  Indeed, this is not recommended:
``ffi`` normally caches the string ``"int[]"`` to not need to re-parse
it all the time.

The C99 variable-sized structures are supported too, as long as the
initializer says how long the array should be:

.. code-block:: python

    # typedef struct { int x; int y[]; } foo_t;

    p = ffi.new("foo_t *", [5, [6, 7, 8]]) # length 3
    p = ffi.new("foo_t *", [5, 3])         # length 3 with 0 in the array
    p = ffi.new("foo_t *", {'y': 3})       # length 3 with 0 everywhere

Finally, note that any Python object used as initializer can also be
used directly without ``ffi.new()`` in assignments to array items or
struct fields.  In fact, ``p = ffi.new("T*", initializer)`` is
equivalent to ``p = ffi.new("T*"); p[0] = initializer``.  Examples:

.. code-block:: python

    # if 'p' is a <cdata 'int[5][5]'>
    p[2] = [10, 20]             # writes to p[2][0] and p[2][1]

    # if 'p' is a <cdata 'foo_t *'>, and foo_t has fields x, y and z
    p[0] = {'x': 10, 'z': 20}   # writes to p.x and p.z; p.y unmodified

    # if, on the other hand, foo_t has a field 'char a[5]':
    p.a = "abc"                 # writes 'a', 'b', 'c' and '\0'; p.a[4] unmodified

In function calls, when passing arguments, these rules can be used too;
see `Function calls`_.


Python 3 support
----------------

Python 3 is supported, but the main point to note is that the ``char`` C
type corresponds to the ``bytes`` Python type, and not ``str``.  It is
your responsibility to encode/decode all Python strings to bytes when
passing them to or receiving them from CFFI.

This only concerns the ``char`` type and derivative types; other parts
of the API that accept strings in Python 2 continue to accept strings in
Python 3.


An example of calling a main-like thing
---------------------------------------

Imagine we have something like this:

.. code-block:: python

   from cffi import FFI
   ffi = FFI()
   ffi.cdef("""
      int main_like(int argv, char *argv[]);
   """)
   lib = ffi.dlopen("some_library.so")

Now, everything is simple, except, how do we create the ``char**`` argument
here?
The first idea:

.. code-block:: python

   lib.main_like(2, ["arg0", "arg1"])

does not work, because the initializer receives two Python ``str`` objects
where it was expecting ``<cdata 'char *'>`` objects.  You need to use
``ffi.new()`` explicitly to make these objects:

.. code-block:: python

   lib.main_like(2, [ffi.new("char[]", "arg0"),
                     ffi.new("char[]", "arg1")])

Note that the two ``<cdata 'char[]'>`` objects are kept alive for the
duration of the call: they are only freed when the list itself is freed,
and the list is only freed when the call returns.

If you want instead to build an "argv" variable that you want to reuse,
then more care is needed:

.. code-block:: python

   # DOES NOT WORK!
   argv = ffi.new("char *[]", [ffi.new("char[]", "arg0"),
                               ffi.new("char[]", "arg1")])

In the above example, the inner "arg0" string is deallocated as soon
as "argv" is built.  You have to make sure that you keep a reference
to the inner "char[]" objects, either directly or by keeping the list
alive like this:

.. code-block:: python

   argv_keepalive = [ffi.new("char[]", "arg0"),
                     ffi.new("char[]", "arg1")]
   argv = ffi.new("char *[]", argv_keepalive)


Function calls
--------------

When calling C functions, passing arguments follows mostly the same
rules as assigning to structure fields, and the return value follows the
same rules as reading a structure field.  For example:

.. code-block:: python

    # int foo(short a, int b);

    n = lib.foo(2, 3)     # returns a normal integer
    lib.foo(40000, 3)     # raises OverflowError

You can pass to ``char *`` arguments a normal Python string (but don't
pass a normal Python string to functions that take a ``char *``
argument and may mutate it!):

.. code-block:: python

    # size_t strlen(const char *);

    assert lib.strlen("hello") == 5

You can also pass unicode strings as ``wchar_t *`` arguments.  Note that
in general, there is no difference between C argument declarations that
use ``type *`` or ``type[]``.  For example, ``int *`` is fully
equivalent to ``int[]`` (or even ``int[5]``; the 5 is ignored).  So you
can pass an ``int *`` as a list of integers:

.. code-block:: python

    # void do_something_with_array(int *array);

    lib.do_something_with_array([1, 2, 3, 4, 5])

See `Reference: conversions`_ for a similar way to pass ``struct foo_s
*`` arguments---but in general, it is clearer to simply pass
``ffi.new('struct foo_s *', initializer)``.

CFFI supports passing and returning structs to functions and callbacks.
Example:

.. code-block:: python

    # struct foo_s { int a, b; };
    # struct foo_s function_returning_a_struct(void);

    myfoo = lib.function_returning_a_struct()
    # `myfoo`: <cdata 'struct foo_s' owning 8 bytes>

There are a few (obscure) limitations to the argument types and return
type.  You cannot pass directly as argument a union (but a *pointer*
to a union is fine), nor a struct which uses bitfields (but a
*pointer* to such a struct is fine).  If you pass a struct (not a
*pointer* to a struct), the struct type cannot have been declared with
"``...;``" in the ``cdef()``; you need to declare it completely in
``cdef()``.  You can work around these limitations by writing a C
function with a simpler signature in the C header code passed to
``ffi.set_source()``, and have this C function call the real one.

Aside from these limitations, functions and callbacks can receive and
return structs.

For performance, API-level functions are not returned as ``<cdata>``
objects, but as a different type (on CPython, ``<built-in
function>``).  This means you cannot e.g. pass them to some other C
function expecting a function pointer argument.  Only ``ffi.typeof()``
works on them.  To get a cdata containing a regular function pointer,
use ``ffi.addressof(lib, "name")`` (new in version 1.1).

Before version 1.1 (or with the deprecated ``ffi.verify()``), if you
really need a cdata pointer to the function, use the following
workaround:

.. code-block:: python
  
    ffi.cdef(""" int (*foo)(int a, int b); """)

i.e. declare them as pointer-to-function in the cdef (even if they are
regular functions in the C code).


Variadic function calls
-----------------------

Variadic functions in C (which end with "``...``" as their last
argument) can be declared and called normally, with the exception that
all the arguments passed in the variable part *must* be cdata objects.
This is because it would not be possible to guess, if you wrote this::

    lib.printf("hello, %d\n", 42)   # doesn't work!

that you really meant the 42 to be passed as a C ``int``, and not a
``long`` or ``long long``.  The same issue occurs with ``float`` versus
``double``.  So you have to force cdata objects of the C type you want,
if necessary with ``ffi.cast()``:

.. code-block:: python
  
    lib.printf("hello, %d\n", ffi.cast("int", 42))
    lib.printf("hello, %ld\n", ffi.cast("long", 42))
    lib.printf("hello, %f\n", ffi.cast("double", 42))

But of course:

.. code-block:: python

    lib.printf("hello, %s\n", ffi.new("char[]", "world"))

Note that if you are using ``dlopen()``, the function declaration in the
``cdef()`` must match the original one in C exactly, as usual --- in
particular, if this function is variadic in C, then its ``cdef()``
declaration must also be variadic.  You cannot declare it in the
``cdef()`` with fixed arguments instead, even if you plan to only call
it with these argument types.  The reason is that some architectures
have a different calling convention depending on whether the function
signature is fixed or not.  (On x86-64, the difference can sometimes be
seen in PyPy's JIT-generated code if some arguments are ``double``.)

Note that the function signature ``int foo();`` is interpreted by CFFI
as equivalent to ``int foo(void);``.  This differs from the C standard,
in which ``int foo();`` is really like ``int foo(...);`` and can be
called with any arguments.  (This feature of C is a pre-C89 relic: the
arguments cannot be accessed at all in the body of ``foo()`` without
relying on compiler-specific extensions.  Nowadays virtually all code
with ``int foo();`` really means ``int foo(void);``.)


.. _extern-python:
.. _`extern "Python"`:

Extern "Python" (new-style callbacks)
-------------------------------------

When the C code needs a pointer to a function which invokes back a
Python function of your choice, here is how you do it in the
out-of-line API mode.  The next section about Callbacks_ describes the
ABI-mode solution.

This is *new in version 1.4.*  Use old-style Callbacks_ if backward
compatibility is an issue.  (The original callbacks are slower to
invoke and have the same issue as libffi's callbacks; notably, see the
warning__.  The new style described in the present section does not
use libffi's callbacks at all.)

.. __: Callbacks_

In the builder script, declare in the cdef a function prefixed with
``extern "Python"``::

    ffi.cdef("""
        extern "Python" int my_callback(int, int);

        void library_function(int(*callback)(int, int));
    """)
    ffi.set_source("_my_example", """
        #include <some_library.h>
    """)

The function ``my_callback()`` is then implemented in Python inside
your application's code::

    from _my_example import ffi, lib

    @ffi.def_extern()
    def my_callback(x, y):
        return 42

You obtain a ``<cdata>`` pointer-to-function object by getting
``lib.my_callback``.  This ``<cdata>`` can be passed to C code and
then works like a callback: when the C code calls this function
pointer, the Python function ``my_callback`` is called.  (You need
to pass ``lib.my_callback`` to C code, and not ``my_callback``: the
latter is just the Python function above, which cannot be passed to C.)

CFFI implements this by defining ``my_callback`` as a static C
function, written after the ``set_source()`` code.  The ``<cdata>``
then points to this function.  What this function does is invoke the
Python function object that is, at runtime, attached with
``@ffi.def_extern()``.

The ``@ffi.def_extern()`` decorator should be applied to **global
functions,** one for each ``extern "Python"`` function of the same
name.

To support some corner cases, it is possible to redefine the attached
Python function by calling ``@ffi.def_extern()`` again for the same
name---but this is not recommended!  Better attach a single global
Python function for this name, and write it more flexibly in the first
place.  This is because each ``extern "Python"`` function turns into
only one C function.  Calling ``@ffi.def_extern()`` again changes this
function's C logic to call the new Python function; the old Python
function is not callable any more.  The C function pointer you get
from ``lib.my_function`` is always this C function's address, i.e. it
remains the same.

Extern "Python" and ``void *`` arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As described just before, you cannot use ``extern "Python"`` to make a
variable number of C function pointers.  However, achieving that
result is not possible in pure C code either.  For this reason, it is
usual for C to define callbacks with a ``void *data`` argument.  You
can use ``ffi.new_handle()`` and ``ffi.from_handle()`` to pass a
Python object through this ``void *`` argument.  For example, if the C
type of the callbacks is::

    typedef void (*event_cb_t)(event_t *evt, void *userdata);

and you register events by calling this function::

    void event_cb_register(event_cb_t cb, void *userdata);

Then you would write this in the build script::

    ffi.cdef("""
        typedef ... event_t;
        typedef void (*event_cb_t)(event_t *evt, void *userdata);
        void event_cb_register(event_cb_t cb, void *userdata);

        extern "Python" void my_event_callback(event_t *, void *);
    """)
    ffi.set_source("_demo_cffi", """
        #include <the_event_library.h>
    """)

and in your main application you register events like this::

    from _demo_cffi import ffi, lib

    class Widget(object):
        def __init__(self):
            userdata = ffi.new_handle(self)
            self._userdata = userdata     # must keep this alive!
            lib.event_cb_register(lib.my_event_callback, userdata)

        def process_event(self, evt):
            ...

    @ffi.def_extern()
    def my_event_callback(evt, userdata):
        widget = ffi.from_handle(userdata)
        widget.process_event(evt)

Some other libraries don't have an explicit ``void *`` argument, but
let you attach the ``void *`` to an existing structure.  For example,
the library might say that ``widget->userdata`` is a generic field
reserved for the application.  If the event's signature is now this::

    typedef void (*event_cb_t)(widget_t *w, event_t *evt);

Then you can use the ``void *`` field in the low-level
``widget_t *`` like this::

    from _demo_cffi import ffi, lib

    class Widget(object):
        def __init__(self):
            ll_widget = lib.new_widget(500, 500)
            self.ll_widget = ll_widget       # <cdata 'struct widget *'>
            userdata = ffi.new_handle(self)
            self._userdata = userdata        # must still keep this alive!
            ll_widget.userdata = userdata    # this makes a copy of the "void *"
            lib.event_cb_register(ll_widget, lib.my_event_callback)

        def process_event(self, evt):
            ...

    @ffi.def_extern()
    def my_event_callback(ll_widget, evt):
        widget = ffi.from_handle(ll_widget.userdata)
        widget.process_event(evt)

Extern "Python" accessed from C directly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In case you want to access some ``extern "Python"`` function directly
from the C code written in ``set_source()``, you need to write a
forward static declaration.  The real implementation of this function
is added by CFFI *after* the C code---this is needed because the
declaration might use types defined by ``set_source()``
(e.g. ``event_t`` above, from the ``#include``), so it cannot be
generated before.

::

    ffi.set_source("_demo_cffi", """
        #include <the_event_library.h>

        static void my_event_callback(widget_t *, event_t *);

        /* here you can write C code which uses '&my_event_callback' */
    """)

This can also be used to write custom C code which calls Python
directly.  Here is an example (inefficient in this case, but might be
useful if the logic in ``my_algo()`` is much more complex)::

    ffi.cdef("""
        extern "Python" int f(int);
        int my_algo(int);
    """)
    ffi.set_source("_example_cffi", """
        static int f(int);   /* the forward declaration */

        static int my_algo(int n) {
            int i, sum = 0;
            for (i = 0; i < n; i++)
                sum += f(i);     /* call f() here */
            return sum;
        }
    """)


Extern "Python": reference
~~~~~~~~~~~~~~~~~~~~~~~~~~

``extern "Python"`` must appear in the cdef().  Like the C++ ``extern
"C"`` syntax, it can also be used with braces around a group of
functions::

    extern "Python" {
        int foo(int);
        int bar(int);
    }

The ``extern "Python"`` functions cannot be variadic for now.  This
may be implemented in the future.  (`This demo`__ shows how to do it
anyway, but it is a bit lengthy.)

.. __: https://bitbucket.org/cffi/cffi/src/default/demo/extern_python_varargs.py

Each corresponding Python callback function is defined with the
``@ffi.def_extern()`` decorator.  Be careful when writing this
function: if it raises an exception, or tries to return an object of
the wrong type, then the exception cannot be propagated.  Instead, the
exception is printed to stderr and the C-level callback is made to
return a default value.  This can be controlled with ``error`` and
``onerror``, described below.

.. _def-extern:

The ``@ffi.def_extern()`` decorator takes these optional arguments:

* ``name``: the name of the function as written in the cdef.  By default
  it is taken from the name of the Python function you decorate.

.. _error_onerror:

* ``error``: the returned value in case the Python function raises an
  exception.  It is 0 or null by default.  The exception is still
  printed to stderr, so this should be used only as a last-resort
  solution.

* ``onerror``: if you want to be sure to catch all exceptions, use
  ``@ffi.def_extern(onerror=my_handler)``.  If an exception occurs and
  ``onerror`` is specified, then ``onerror(exception, exc_value,
  traceback)`` is called.  This is useful in some situations where you
  cannot simply write ``try: except:`` in the main callback function,
  because it might not catch exceptions raised by signal handlers: if
  a signal occurs while in C, the Python signal handler is called as
  soon as possible, which is after entering the callback function but
  *before* executing even the ``try:``.  If the signal handler raises,
  we are not in the ``try: except:`` yet.

  If ``onerror`` is called and returns normally, then it is assumed
  that it handled the exception on its own and nothing is printed to
  stderr.  If ``onerror`` raises, then both tracebacks are printed.
  Finally, ``onerror`` can itself provide the result value of the
  callback in C, but doesn't have to: if it simply returns None---or
  if ``onerror`` itself fails---then the value of ``error`` will be
  used, if any.

  Note the following hack: in ``onerror``, you can access the original
  callback arguments as follows.  First check if ``traceback`` is not
  None (it is None e.g. if the whole function ran successfully but
  there was an error converting the value returned: this occurs after
  the call).  If ``traceback`` is not None, then
  ``traceback.tb_frame`` is the frame of the outermost function,
  i.e. directly the frame of the function decorated with
  ``@ffi.def_extern()``.  So you can get the value of ``argname`` in
  that frame by reading ``traceback.tb_frame.f_locals['argname']``.


.. _Callbacks:

Callbacks (old style)
---------------------

Here is how to make a new ``<cdata>`` object that contains a pointer
to a function, where that function invokes back a Python function of
your choice::

    >>> @ffi.callback("int(int, int)")
    >>> def myfunc(x, y):
    ...    return x + y
    ...
    >>> myfunc
    <cdata 'int(*)(int, int)' calling <function myfunc at 0xf757bbc4>>

Note that ``"int(*)(int, int)"`` is a C *function pointer* type, whereas
``"int(int, int)"`` is a C *function* type.  Either can be specified to
ffi.callback() and the result is the same.

.. warning::

    Callbacks are provided for the ABI mode or for backward
    compatibility.  If you are using the out-of-line API mode, it is
    recommended to use the `extern "Python"`_ mechanism instead of
    callbacks: it gives faster and cleaner code.  It also avoids a
    SELinux issue whereby the setting of ``deny_execmem`` must be left
    to ``off`` in order to use callbacks.  (A fix in cffi was
    attempted---see the ``ffi_closure_alloc`` branch---but was not
    merged because it creates potential memory corruption with
    ``fork()``.  For more information, `see here.`__)

.. __: https://bugzilla.redhat.com/show_bug.cgi?id=1249685

Warning: like ffi.new(), ffi.callback() returns a cdata that has
ownership of its C data.  (In this case, the necessary C data contains
the libffi data structures to do a callback.)  This means that the
callback can only be invoked as long as this cdata object is alive.
If you store the function pointer into C code, then make sure you also
keep this object alive for as long as the callback may be invoked.
The easiest way to do that is to always use ``@ffi.callback()`` at
module-level only, and to pass "context" information around with
`ffi.new_handle()`_, if possible.  Example:

.. code-block:: python

    # a good way to use this decorator is once at global level
    @ffi.callback("int(int, void *)")
    def my_global_callback(x, handle):
        return ffi.from_handle(handle).some_method(x)


    class Foo(object):

        def __init__(self):
            handle = ffi.new_handle(self)
            self._handle = handle   # must be kept alive
            lib.register_stuff_with_callback_and_voidp_arg(my_global_callback, handle)

        def some_method(self, x):
            ...

(See also the section about `extern "Python"`_ above, where the same
general style is used.)

Note that callbacks of a variadic function type are not supported.  A
workaround is to add custom C code.  In the following example, a
callback gets a first argument that counts how many extra ``int``
arguments are passed:

.. code-block:: python

    # file "example_build.py"

    import cffi

    ffi = cffi.FFI()
    ffi.cdef("""
        int (*python_callback)(int how_many, int *values);
        void *const c_callback;   /* pass this const ptr to C routines */
    """)
    lib = ffi.set_source("_example", """
        #include <stdarg.h>
        #include <alloca.h>
        static int (*python_callback)(int how_many, int *values);
        static int c_callback(int how_many, ...) {
            va_list ap;
            /* collect the "..." arguments into the values[] array */
            int i, *values = alloca(how_many * sizeof(int));
            va_start(ap, how_many);
            for (i=0; i<how_many; i++)
                values[i] = va_arg(ap, int);
            va_end(ap);
            return python_callback(how_many, values);
        }
    """)

.. code-block:: python
    
    # file "example.py"

    from _example import ffi, lib

    @ffi.callback("int(int, int *)")
    def python_callback(how_many, values):
        print values     # a list
        return 0
    lib.python_callback = python_callback

Deprecated: you can also use ``ffi.callback()`` not as a decorator but
directly as ``ffi.callback("int(int, int)", myfunc)``.  This is
discouraged: using this a style, we are more likely to forget the
callback object too early, when it is still in use.

The ``ffi.callback()`` decorator also accepts the optional argument
``error``, and from CFFI version 1.2 the optional argument ``onerror``.
These two work in the same way as `described above for extern "Python".`__

.. __: error_onerror_



Windows: calling conventions
----------------------------

On Win32, functions can have two main calling conventions: either
"cdecl" (the default), or "stdcall" (also known as "WINAPI").  There
are also other rare calling conventions, but these are not supported.
*New in version 1.3.*

When you issue calls from Python to C, the implementation is such that
it works with any of these two main calling conventions; you don't
have to specify it.  However, if you manipulate variables of type
"function pointer" or declare callbacks, then the calling convention
must be correct.  This is done by writing ``__cdecl`` or ``__stdcall``
in the type, like in C::

    @ffi.callback("int __stdcall(int, int)")
    def AddNumbers(x, y):
        return x + y

or::

    ffi.cdef("""
        struct foo_s {
            int (__stdcall *MyFuncPtr)(int, int);
        };
    """)

``__cdecl`` is supported but is always the default so it can be left
out.  In the ``cdef()``, you can also use ``WINAPI`` as equivalent to
``__stdcall``.  As mentioned above, it is not needed (but doesn't
hurt) to say ``WINAPI`` or ``__stdcall`` when declaring a plain
function in the ``cdef()``.  (The difference can still be seen if you
take explicitly a pointer to this function with ``ffi.addressof()``,
or if the function is ``extern "Python"``.)

These calling convention specifiers are accepted but ignored on any
platform other than 32-bit Windows.

In CFFI versions before 1.3, the calling convention specifiers are not
recognized.  In API mode, you could work around it by using an
indirection, like in the example in the section about Callbacks_
(``"example_build.py"``).  There was no way to use stdcall callbacks
in ABI mode.


FFI Interface
-------------

**ffi.new(cdecl, init=None)**:
allocate an instance according to the specified C type and return a
pointer to it.  The specified C type must be either a pointer or an
array: ``new('X *')`` allocates an X and returns a pointer to it,
whereas ``new('X[n]')`` allocates an array of n X'es and returns an
array referencing it (which works mostly like a pointer, like in C).
You can also use ``new('X[]', n)`` to allocate an array of a
non-constant length n.  See above__ for other valid initializers.

.. __: working_

When the returned ``<cdata>`` object goes out of scope, the memory is
freed.  In other words the returned ``<cdata>`` object has ownership of
the value of type ``cdecl`` that it points to.  This means that the raw
data can be used as long as this object is kept alive, but must not be
used for a longer time.  Be careful about that when copying the
pointer to the memory somewhere else, e.g. into another structure.

**ffi.cast("C type", value)**: similar to a C cast: returns an
instance of the named C type initialized with the given value.  The
value is casted between integers or pointers of any type.

**ffi.error**: the Python exception raised in various cases.  (Don't
confuse it with ``ffi.errno``.)
        
**ffi.errno**: the value of ``errno`` received from the most recent C call
in this thread, and passed to the following C call.  (This is a read-write
property.)

**ffi.getwinerror(code=-1)**: on Windows, in addition to ``errno`` we
also save and restore the ``GetLastError()`` value across function
calls.  This function returns this error code as a tuple ``(code,
message)``, adding a readable message like Python does when raising
WindowsError.  If the argument ``code`` is given, format that code into
a message instead of using ``GetLastError()``.
(Note that it is also possible to declare and call the ``GetLastError()``
function as usual.)

**ffi.string(cdata, [maxlen])**: return a Python string (or unicode
string) from the 'cdata'.

- If 'cdata' is a pointer or array of characters or bytes, returns the
  null-terminated string.  The returned string extends until the first
  null character, or at most 'maxlen' characters.  If 'cdata' is an
  array then 'maxlen' defaults to its length.  See ``ffi.buffer()`` below
  for a way to continue past the first null character.  *Python 3:* this
  returns a ``bytes``, not a ``str``.

- If 'cdata' is a pointer or array of wchar_t, returns a unicode string
  following the same rules.

- If 'cdata' is a single character or byte or a wchar_t, returns it as a
  byte string or unicode string.  (Note that in some situation a single
  wchar_t may require a Python unicode string of length 2.)

- If 'cdata' is an enum, returns the value of the enumerator as a string.
  If the value is out of range, it is simply returned as the stringified
  integer.


**ffi.buffer(cdata, [size])**: return a buffer object that references
the raw C data pointed to by the given 'cdata', of 'size' bytes.  The
'cdata' must be a pointer or an array.  If unspecified, the size of the
buffer is either the size of what ``cdata`` points to, or the whole size
of the array.  Getting a buffer is useful because you can read from it
without an extra copy, or write into it to change the original value.

Here are a few examples of where buffer() would be useful:

-  use ``file.write()`` and ``file.readinto()`` with
   such a buffer (for files opened in binary mode)

-  use ``ffi.buffer(mystruct[0])[:] = socket.recv(len(buffer))`` to read
   into a struct over a socket, rewriting the contents of mystruct[0]

Remember that like in C, you can use ``array + index`` to get the pointer
to the index'th item of an array.

The returned object is not a built-in buffer nor memoryview object,
because these objects' API changes too much across Python versions.
Instead it has the following Python API (a subset of Python 2's
``buffer``):

- ``buf[:]`` or ``bytes(buf)``: fetch a copy as a regular byte string (or
  ``buf[start:end]`` for a part)

- ``buf[:] = newstr``: change the original content (or ``buf[start:end]
  = newstr``)

- ``len(buf), buf[index], buf[index] = newchar``: access as a sequence
  of characters.

The buffer object returned by ``ffi.buffer(cdata)`` keeps alive the
``cdata`` object: if it was originally an owning cdata, then its
owned memory will not be freed as long as the buffer is alive.

Python 2/3 compatibility note: you should avoid using ``str(buf)``,
because it gives inconsistent results between Python 2 and Python 3.
(This is similar to how ``str()`` gives inconsistent results on regular
byte strings).  Use ``buf[:]`` instead.

**ffi.from_buffer(python_buffer)**: return a ``<cdata 'char[]'>`` that
points to the data of the given Python object, which must support the
buffer interface.  This is the opposite of ``ffi.buffer()``.  It gives
a reference to the existing data, not a copy; for this
reason, and for PyPy compatibility, it does not work with the built-in
types str or unicode or bytearray (or buffers/memoryviews on them).
It is meant to be used on objects
containing large quantities of raw data, like ``array.array`` or numpy
arrays.  It supports both the old buffer API (in Python 2.x) and the
new memoryview API.  Note that if you pass a read-only buffer object,
you still get a regular ``<cdata 'char[]'>``; it is your responsibility
not to write there if the original buffer doesn't expect you to.
The original object is kept alive (and, in case
of memoryview, locked) as long as the cdata object returned by
``ffi.from_buffer()`` is alive.  *New in version 0.9.*


.. _memmove:

**ffi.memmove(dest, src, n)**: copy ``n`` bytes from memory area
``src`` to memory area ``dest``.  See examples below.  Inspired by the
C functions ``memcpy()`` and ``memmove()``---like the latter, the
areas can overlap.  Each of ``dest`` and ``src`` can be either a cdata
pointer or a Python object supporting the buffer/memoryview interface.
In the case of ``dest``, the buffer/memoryview must be writable.
Unlike ``ffi.from_buffer()``, there are no restrictions on the type of
buffer.  *New in version 1.3.*  Examples:

* ``ffi.memmove(myptr, b"hello", 5)`` copies the 5 bytes of
  ``b"hello"`` to the area that ``myptr`` points to.

* ``ba = bytearray(100); ffi.memmove(ba, myptr, 100)`` copies 100
  bytes from ``myptr`` into the bytearray ``ba``.

* ``ffi.memmove(myptr + 1, myptr, 100)`` shifts 100 bytes from
  the memory at ``myptr`` to the memory at ``myptr + 1``.


**ffi.typeof("C type" or cdata object)**: return an object of type
``<ctype>`` corresponding to the parsed string, or to the C type of the
cdata instance.  Usually you don't need to call this function or to
explicitly manipulate ``<ctype>`` objects in your code: any place that
accepts a C type can receive either a string or a pre-parsed ``ctype``
object (and because of caching of the string, there is no real
performance difference).  It can still be useful in writing typechecks,
e.g.:

.. code-block:: python
  
    def myfunction(ptr):
        assert ffi.typeof(ptr) is ffi.typeof("foo_t*")
        ...

Note also that the mapping from strings like ``"foo_t*"`` to the
``<ctype>`` objects is stored in some internal dictionary.  This
guarantees that there is only one ``<ctype 'foo_t *'>`` object, so you
can use the ``is`` operator to compare it.  The downside is that the
dictionary entries are immortal for now.  In the future, we may add
transparent reclamation of old, unused entries.  In the meantime, note
that using strings like ``"int[%d]" % length`` to name a type will
create many immortal cached entries if called with many different
lengths.

**ffi.CData, ffi.CType**: the Python type of the objects referred to
as ``<cdata>`` and ``<ctype>`` in the rest of this document.  Note
that some cdata objects may be actually of a subclass of
``ffi.CData``, and similarly with ctype, so you should check with
``if isinstance(x, ffi.CData)``.  Also, ``<ctype>`` objects have
a number of attributes for introspection: ``kind`` and ``cname`` are
always present, and depending on the kind they may also have
``item``, ``length``, ``fields``, ``args``, ``result``, ``ellipsis``,
``abi``, ``elements`` and ``relements``.

**ffi.NULL**: a constant NULL of type ``<cdata 'void *'>``.

**ffi.sizeof("C type" or cdata object)**: return the size of the
argument in bytes.  The argument can be either a C type, or a cdata object,
like in the equivalent ``sizeof`` operator in C.

**ffi.alignof("C type")**: return the natural alignment size in bytes of
the argument.  Corresponds to the ``__alignof__`` operator in GCC.


**ffi.offsetof("C struct or array type", \*fields_or_indexes)**: return the
offset within the struct of the given field.  Corresponds to ``offsetof()``
in C.

*New in version 0.9:*
You can give several field names in case of nested structures.  You
can also give numeric values which correspond to array items, in case
of a pointer or array type.  For example, ``ffi.offsetof("int[5]", 2)``
is equal to the size of two integers, as is ``ffi.offsetof("int *", 2)``.


**ffi.getctype("C type" or <ctype>, extra="")**: return the string
representation of the given C type.  If non-empty, the "extra" string is
appended (or inserted at the right place in more complicated cases); it
can be the name of a variable to declare, or an extra part of the type
like ``"*"`` or ``"[5]"``.  For example
``ffi.getctype(ffi.typeof(x), "*")`` returns the string representation
of the C type "pointer to the same type than x"; and
``ffi.getctype("char[80]", "a") == "char a[80]"``.


**ffi.gc(cdata, destructor)**: return a new cdata object that points to the
same data.  Later, when this new cdata object is garbage-collected,
``destructor(old_cdata_object)`` will be called.  Example of usage:
``ptr = ffi.gc(lib.malloc(42), lib.free)``.  Note that like objects
returned by ``ffi.new()``, the returned pointer objects have *ownership*,
which means the destructor is called as soon as *this* exact returned
object is garbage-collected.

Note that this should be avoided for large memory allocations or
for limited resources.  This is particularly true on PyPy: its GC does
not know how much memory or how many resources the returned ``ptr``
holds.  It will only run its GC when enough memory it knows about has
been allocated (and thus run the destructor possibly later than you
would expect).  Moreover, the destructor is called in whatever thread
PyPy is at that moment, which might be a problem for some C libraries.
In these cases, consider writing a wrapper class with custom ``__enter__()``
and ``__exit__()`` methods, allocating and freeing the C data at known
points in time, and using it in a ``with`` statement.


.. _ffi-new_handle:
.. _`ffi.new_handle()`:

**ffi.new_handle(python_object)**: return a non-NULL cdata of type
``void *`` that contains an opaque reference to ``python_object``.  You
can pass it around to C functions or store it into C structures.  Later,
you can use **ffi.from_handle(p)** to retrieve the original
``python_object`` from a value with the same ``void *`` pointer.
*Calling ffi.from_handle(p) is invalid and will likely crash if
the cdata object returned by new_handle() is not kept alive!*

(In case you are wondering, this ``void *`` is not the ``PyObject *``
pointer.  This wouldn't make sense on PyPy anyway.)

The ``ffi.new_handle()/from_handle()`` functions *conceptually* work
like this:

* ``new_handle()`` returns cdata objects that contains references to
  the Python objects; we call them collectively the "handle" cdata
  objects.  The ``void *`` value in these handle cdata objects are
  random but unique.

* ``from_handle(p)`` searches all live "handle" cdata objects for the
  one that has the same value ``p`` as its ``void *`` value.  It then
  returns the Python object referenced by that handle cdata object.
  If none is found, you get "undefined behavior" (i.e. crashes).

The "handle" cdata object keeps the Python object alive, similar to
how ``ffi.new()`` returns a cdata object that keeps a piece of memory
alive.  If the handle cdata object *itself* is not alive any more,
then the association ``void * -> python_object`` is dead and
``from_handle()`` will crash.

*New in version 1.4:* two calls to ``new_handle(x)`` are guaranteed to
return cdata objects with different ``void *`` values, even with the
same ``x``.  This is a useful feature that avoids issues with unexpected
duplicates in the following trick: if you need to keep alive the
"handle" until explicitly asked to free it, but don't have a natural
Python-side place to attach it to, then the easiest is to ``add()`` it
to a global set.  It can later be removed from the set by
``global_set.discard(p)``, with ``p`` any cdata object whose ``void *``
value compares equal.


.. _`ffi.addressof()`:

**ffi.addressof(cdata, \*fields_or_indexes)**: limited equivalent to
the '&' operator in C:

1. ``ffi.addressof(<cdata 'struct-or-union'>)`` returns a cdata that
is a pointer to this struct or union.  The returned pointer is only
valid as long as the original ``cdata`` object is; be sure to keep it
alive if it was obtained directly from ``ffi.new()``.

2. ``ffi.addressof(<cdata>, field-or-index...)`` returns the address
of a field or array item inside the given structure or array.  In case
of nested structures or arrays, you can give more than one field or
index to look recursively.  Note that ``ffi.addressof(array, index)``
can also be expressed as ``array + index``: this is true both in CFFI
and in C, where ``&array[index]`` is just ``array + index``.

3. ``ffi.addressof(<library>, "name")`` returns the address of the
named function or global variable from the given library object.
*New in version 1.1:* for functions, it returns a regular cdata
object containing a pointer to the function.

Note that the case 1. cannot be used to take the address of a
primitive or pointer, but only a struct or union.  It would be
difficult to implement because only structs and unions are internally
stored as an indirect pointer to the data.  If you need a C int whose
address can be taken, use ``ffi.new("int[1]")`` in the first place;
similarly, for a pointer, use ``ffi.new("foo_t *[1]")``.


**ffi.dlopen(libpath, [flags])**: opens and returns a "handle" to a
dynamic library, as a ``<lib>`` object.  See `Preparing and
Distributing modules`_.

**ffi.dlclose(lib)**: explicitly closes a ``<lib>`` object returned
by ``ffi.dlopen()``.

**ffi.RLTD_...**: constants: flags for ``ffi.dlopen()``.


.. _`alternative allocators`:

**ffi.new_allocator(alloc=None, free=None, should_clear_after_alloc=True)**:
returns a new allocator.  An "allocator" is a callable that behaves like
``ffi.new()`` but uses the provided low-level ``alloc`` and ``free``
functions.  *New in version 1.2.*

``alloc()`` is invoked with the size as sole argument.  If it returns
NULL, a MemoryError is raised.  Later, if ``free`` is not None, it will
be called with the result of ``alloc()`` as argument.  Both can be either
Python function or directly C functions.  If only ``free`` is None, then no
free function is called.  If both ``alloc`` and ``free`` are None, the
default alloc/free combination is used.  (In other words, the call
``ffi.new(*args)`` is equivalent to ``ffi.new_allocator()(*args)``.)

If ``should_clear_after_alloc`` is set to False, then the memory
returned by ``alloc()`` is assumed to be already cleared (or you are
fine with garbage); otherwise CFFI will clear it.

.. _initonce:

**ffi.init_once(function, tag)**: run ``function()`` once.  The
``tag`` should be a primitive object, like a string, that identifies
the function: ``function()`` is only called the first time we see the
``tag``.  The return value of ``function()`` is remembered and
returned by the current and all future ``init_once()`` with the same
tag.  If ``init_once()`` is called from multiple threads in parallel,
all calls block until the execution of ``function()`` is done.  If
``function()`` raises an exception, it is propagated and nothing is
cached (i.e. ``function()`` will be called again, in case we catch the
exception and try ``init_once()`` again).  *New in version 1.4.*

Example::

    from _xyz_cffi import ffi, lib

    def initlib():
        lib.init_my_library()

    def make_new_foo():
        ffi.init_once(initlib, "init")
        return lib.make_foo()

``init_once()`` is optimized to run very quickly if ``function()`` has
already been called.  (On PyPy, the cost is zero---the JIT usually
removes everything in the machine code it produces.)

*Note:* one motivation__ for ``init_once()`` is the CPython notion of
"subinterpreters" in the embedded case.  If you are using the
out-of-line API mode, ``function()`` is called only once even in the
presence of multiple subinterpreters, and its return value is shared
among all subinterpreters.  The goal is to mimic the way traditional
CPython C extension modules have their init code executed only once in
total even if there are subinterpreters.  In the example above, the C
function ``init_my_library()`` is called once in total, not once per
subinterpreter.  For this reason, avoid Python-level side-effects in
``function()`` (as they will only be applied in the first
subinterpreter to run); instead, return a value, as in the following
example::

   def init_get_max():
       return lib.initialize_once_and_get_some_maximum_number()

   def process(i):
       if i > ffi.init_once(init_get_max, "max"):
           raise IndexError("index too large!")
       ...

.. __: https://bitbucket.org/cffi/cffi/issues/233/


.. _`Preparing and Distributing modules`: cdef.html#loading-libraries


Reference: conversions
----------------------

This section documents all the conversions that are allowed when
*writing into* a C data structure (or passing arguments to a function
call), and *reading from* a C data structure (or getting the result of a
function call).  The last column gives the type-specific operations
allowed.

+---------------+------------------------+------------------+----------------+
|    C type     |   writing into         | reading from     |other operations|
+===============+========================+==================+================+
|   integers    | an integer or anything | a Python int or  | int()          |
|   and enums   | on which int() works   | long, depending  |                |
|   `(*****)`   | (but not a float!).    | on the type      |                |
|               | Must be within range.  |                  |                |
+---------------+------------------------+------------------+----------------+
|   ``char``    | a string of length 1   | a string of      | int()          |
|               | or another <cdata char>| length 1         |                |
+---------------+------------------------+------------------+----------------+
|  ``wchar_t``  | a unicode of length 1  | a unicode of     |                |
|               | (or maybe 2 if         | length 1         | int()          |
|               | surrogates) or         | (or maybe 2 if   |                |
|               | another <cdata wchar_t>| surrogates)      |                |
+---------------+------------------------+------------------+----------------+
|  ``float``,   | a float or anything on | a Python float   | float(), int() |
|  ``double``   | which float() works    |                  |                |
+---------------+------------------------+------------------+----------------+
|``long double``| another <cdata> with   | a <cdata>, to    | float(), int() |
|               | a ``long double``, or  | avoid loosing    |                |
|               | anything on which      | precision `(***)`|                |
|               | float() works          |                  |                |
+---------------+------------------------+------------------+----------------+
|  pointers     | another <cdata> with   | a <cdata>        |``[]`` `(****)`,|
|               | a compatible type (i.e.|                  |``+``, ``-``,   |
|               | same type or ``char*`` |                  |bool()          |
|               | or ``void*``, or as an |                  |                |
|               | array instead) `(*)`   |                  |                |
+---------------+------------------------+                  |                |
|  ``void *``,  | another <cdata> with   |                  |                |
|  ``char *``   | any pointer or array   |                  |                |
|               | type                   |                  |                |
+---------------+------------------------+                  +----------------+
|  pointers to  | same as pointers       |                  | ``[]``, ``+``, |
|  structure or |                        |                  | ``-``, bool(), |
|  union        |                        |                  | and read/write |
|               |                        |                  | struct fields  |
+---------------+------------------------+                  +----------------+
| function      | same as pointers       |                  | bool(),        |
| pointers      |                        |                  | call `(**)`    |
+---------------+------------------------+------------------+----------------+
|  arrays       | a list or tuple of     | a <cdata>        |len(), iter(),  |
|               | items                  |                  |``[]`` `(****)`,|
|               |                        |                  |``+``, ``-``    |
+---------------+------------------------+                  +----------------+
|  ``char[]``   | same as arrays, or a   |                  | len(), iter(), |
|               | Python string          |                  | ``[]``, ``+``, |
|               |                        |                  | ``-``          |
+---------------+------------------------+                  +----------------+
| ``wchar_t[]`` | same as arrays, or a   |                  | len(), iter(), |
|               | Python unicode         |                  | ``[]``,        |
|               |                        |                  | ``+``, ``-``   |
|               |                        |                  |                |
+---------------+------------------------+------------------+----------------+
| structure     | a list or tuple or     | a <cdata>        | read/write     |
|               | dict of the field      |                  | fields         |
|               | values, or a same-type |                  |                |
|               | <cdata>                |                  |                |
+---------------+------------------------+                  +----------------+
| union         | same as struct, but    |                  | read/write     |
|               | with at most one field |                  | fields         |
+---------------+------------------------+------------------+----------------+

`(*)` ``item *`` is ``item[]`` in function arguments:

   In a function declaration, as per the C standard, a ``item *``
   argument is identical to a ``item[]`` argument (and ``ffi.cdef()``
   doesn't record the difference).  So when you call such a function,
   you can pass an argument that is accepted by either C type, like
   for example passing a Python string to a ``char *`` argument
   (because it works for ``char[]`` arguments) or a list of integers
   to a ``int *`` argument (it works for ``int[]`` arguments).  Note
   that even if you want to pass a single ``item``, you need to
   specify it in a list of length 1; for example, a ``struct point_s
   *`` argument might be passed as ``[[x, y]]`` or ``[{'x': 5, 'y':
   10}]``.

   As an optimization, the CPython version of CFFI assumes that a
   function with a ``char *`` argument to which you pass a Python
   string will not actually modify the array of characters passed in,
   and so passes directly a pointer inside the Python string object.
   (PyPy might in the future do the same, but it is harder because
   strings are not naturally zero-terminated in PyPy.)

`(**)` C function calls are done with the GIL released.

   Note that we assume that the called functions are *not* using the
   Python API from Python.h.  For example, we don't check afterwards
   if they set a Python exception.  You may work around it, but mixing
   CFFI with ``Python.h`` is not recommended.  (If you do that, on
   PyPy and on some platforms like Windows, you may need to explicitly
   link to ``libpypy-c.dll`` to access the CPython C API compatibility
   layer; indeed, CFFI-generated modules on PyPy don't link to
   ``libpypy-c.dll`` on their own.  But really, don't do that in the
   first place.)

`(***)` ``long double`` support:

   We keep ``long double`` values inside a cdata object to avoid
   loosing precision.  Normal Python floating-point numbers only
   contain enough precision for a ``double``.  If you really want to
   convert such an object to a regular Python float (i.e. a C
   ``double``), call ``float()``.  If you need to do arithmetic on
   such numbers without any precision loss, you need instead to define
   and use a family of C functions like ``long double add(long double
   a, long double b);``.

`(****)` Slicing with ``x[start:stop]``:

   Slicing is allowed, as long as you specify explicitly both ``start``
   and ``stop`` (and don't give any ``step``).  It gives a cdata
   object that is a "view" of all items from ``start`` to ``stop``.
   It is a cdata of type "array" (so e.g. passing it as an argument to a
   C function would just convert it to a pointer to the ``start`` item).
   As with indexing, negative bounds mean really negative indices, like in
   C.  As for slice assignment, it accepts any iterable, including a list
   of items or another array-like cdata object, but the length must match.
   (Note that this behavior differs from initialization: e.g. you can
   say ``chararray[10:15] = "hello"``, but the assigned string must be of
   exactly the correct length; no implicit null character is added.)

`(*****)` Enums are handled like ints:

   Like C, enum types are mostly int types (unsigned or signed, int or
   long; note that GCC's first choice is unsigned).  Reading an enum
   field of a structure, for example, returns you an integer.  To
   compare their value symbolically, use code like ``if x.field ==
   lib.FOO``.  If you really want to get their value as a string, use
   ``ffi.string(ffi.cast("the_enum_type", x.field))``.

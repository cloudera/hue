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

*New in version 1.11:* in addition to ``wchar_t``, the C types
``char16_t`` and ``char32_t`` work the same but with a known fixed size.
In previous versions, this could be achieved using ``uint16_t`` and
``int32_t`` but without automatic conversion to Python unicodes.

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

Usually you don't need a weak dict: for example, to call a function with
a ``char * *`` argument that contains a pointer to a ``char *`` pointer,
it is enough to do this:

.. code-block:: python

    p = ffi.new("char[]", "hello, world")    # p is a 'char *'
    q = ffi.new("char **", p)                # q is a 'char **'
    lib.myfunction(q)
    # p is alive at least until here, so that's fine

However, this is always wrong (usage of freed memory):

.. code-block:: python

    p = ffi.new("char **", ffi.new("char[]", "hello, world"))
    # WRONG!  as soon as p is built, the inner ffi.new() gets freed!

This is wrong too, for the same reason:

.. code-block:: python

    p = ffi.new("struct my_stuff")
    p.foo = ffi.new("char[]", "hello, world")
    # WRONG!  as soon as p.foo is set, the ffi.new() gets freed!


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
here).  There is `ffi.addressof()`__, but only for some cases.  You
cannot take the "address" of a number in Python, for example; similarly,
you cannot take the address of a CFFI pointer.  If you have this kind
of C code::

    int x, y;
    fetch_size(&x, &y);

    opaque_t *handle;      // some opaque pointer
    init_stuff(&handle);   // initializes the variable 'handle'
    more_stuff(handle);    // pass the handle around to more functions

then you need to rewrite it like this, replacing the variables in C
with what is logically pointers to the variables:

.. code-block:: python

    px = ffi.new("int *")
    py = ffi.new("int *")              arr = ffi.new("int[2]")
    lib.fetch_size(px, py)    -OR-     lib.fetch_size(arr, arr + 1)
    x = px[0]                          x = arr[0]
    y = py[0]                          y = arr[1]

    p_handle = ffi.new("opaque_t **")
    lib.init_stuff(p_handle)   # pass the pointer to the 'handle' pointer
    handle = p_handle[0]       # now we can read 'handle' out of 'p_handle'
    lib.more_stuff(handle)

.. __: ref.html#ffi-addressof


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

Similarly, arrays of wchar_t or char16_t or char32_t can be initialized
from a unicode string,
and calling ``ffi.string()`` on the cdata object returns the current unicode
string stored in the source array (adding surrogates if necessary).
See the `Unicode character types`__ section for more details.

.. __: ref.html#unichar

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

You can also pass unicode strings as ``wchar_t *`` or ``char16_t *`` or
``char32_t *`` arguments.  Note that
the C language makes no difference between argument declarations that
use ``type *`` or ``type[]``.  For example, ``int *`` is fully
equivalent to ``int[]`` (or even ``int[5]``; the 5 is ignored).  For CFFI,
this means that you can always pass arguments that can be converted to
either ``int *`` or ``int[]``.  For example:

.. code-block:: python

    # void do_something_with_array(int *array);

    lib.do_something_with_array([1, 2, 3, 4, 5])    # works for int[]

See `Reference: conversions`__ for a similar way to pass ``struct foo_s
*`` arguments---but in general, it is clearer in this case to pass
``ffi.new('struct foo_s *', initializer)``.

__ ref.html#conversions

CFFI supports passing and returning structs and unions to functions and
callbacks.  Example:

.. code-block:: python

    # struct foo_s { int a, b; };
    # struct foo_s function_returning_a_struct(void);

    myfoo = lib.function_returning_a_struct()
    # `myfoo`: <cdata 'struct foo_s' owning 8 bytes>

For performance, non-variadic API-level functions that you get by
writing ``lib.some_function`` are not ``<cdata>``
objects, but an object of a different type (on CPython, ``<built-in
function>``).  This means you cannot pass them directly to some other C
function expecting a function pointer argument.  Only ``ffi.typeof()``
works on them.  To get a cdata containing a regular function pointer,
use ``ffi.addressof(lib, "name")``.

There are a few (obscure) limitations to the supported argument and
return types.  These limitations come from libffi and apply only to
calling ``<cdata>`` function pointers; in other words, they don't
apply to non-variadic ``cdef()``-declared functions if you are using
the API mode.  The limitations are that you cannot pass directly as
argument or return type:

* a union (but a *pointer* to a union is fine);

* a struct which uses bitfields (but a *pointer* to such a struct is
  fine);

* a struct that was declared with "``...``" in the ``cdef()``.

In API mode, you can work around these limitations: for example, if you
need to call such a function pointer from Python, you can instead write
a custom C function that accepts the function pointer and the real
arguments and that does the call from C.  Then declare that custom C
function in the ``cdef()`` and use it from Python.


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


Memory pressure (PyPy)
----------------------

This paragraph applies only to PyPy, because its garbage collector (GC)
is different from CPython's.  It is very common in C code to have pairs
of functions, one which performs memory allocations or acquires other
resources, and the other which frees them again.  Depending on how you
structure your Python code, the freeing function is only called when the
GC decides a particular (Python) object can be freed.  This occurs
notably in these cases:

* If you use a ``__del__()`` method to call the freeing function.

* If you use ``ffi.gc()``.

* This does not occur if you call the freeing function at a
  deterministic time, like in a regular ``try: finally:`` block.  It
  does however occur *inside a generator---* if the generator is not
  explicitly exhausted but forgotten at a ``yield`` point, then the code
  in the enclosing ``finally`` block is only invoked at the next GC.

In these cases, you may have to use the built-in function
``__pypy__.add_memory_pressure(n)``.  Its argument ``n`` is an estimate
of how much memory pressure to add.  For example, if the pair of C
functions that we are talking about is ``malloc(n)`` and ``free()`` or
similar, you would call ``__pypy__.add_memory_pressure(n)`` after
``malloc(n)``.  Doing so is not always a complete answer to the problem,
but it makes the next GC occur earlier, which is often enough.

The same applies if the memory allocations are indirect, e.g. the C
function allocates some internal data structures.  In that case, call
``__pypy__.add_memory_pressure(n)`` with an argument ``n`` that is an
rough estimation.  Knowing the exact size is not important, and memory
pressure doesn't have to be manually brought down again after calling
the freeing function.  If you are writing wrappers for the allocating /
freeing pair of functions, you should probably call
``__pypy__.add_memory_pressure()`` in the former even if the user may
invoke the latter at a known point with a ``finally:`` block.

In case this solution is not sufficient, or if the acquired resource is
not memory but something else more limited (like file descriptors), then
there is no better way than restructuring your code to make sure the
freeing function is called at a known point and not indirectly by the
GC.

Note that in PyPy <= 5.6 the discussion above also applies to
``ffi.new()``.  In more recent versions of PyPy, both ``ffi.new()`` and
``ffi.new_allocator()()`` automatically account for the memory pressure
they create.  (In case you need to support both older and newer PyPy's,
try calling ``__pypy__.add_memory_pressure()`` anyway; it is better to
overestimate than not account for the memory pressure.)


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

    ffibuilder.cdef("""
        extern "Python" int my_callback(int, int);

        void library_function(int(*callback)(int, int));
    """)
    ffibuilder.set_source("_my_example", r"""
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

    ffibuilder.cdef("""
        typedef ... event_t;
        typedef void (*event_cb_t)(event_t *evt, void *userdata);
        void event_cb_register(event_cb_t cb, void *userdata);

        extern "Python" void my_event_callback(event_t *, void *);
    """)
    ffibuilder.set_source("_demo_cffi", r"""
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
            print "got event!"

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
            print "got event!"

    @ffi.def_extern()
    def my_event_callback(ll_widget, evt):
        widget = ffi.from_handle(ll_widget.userdata)
        widget.process_event(evt)

Extern "Python" accessed from C directly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In case you want to access some ``extern "Python"`` function directly
from the C code written in ``set_source()``, you need to write a
forward declaration.  (By default it needs to be static, but see
`next paragraph`__.)  The real implementation of this function
is added by CFFI *after* the C code---this is needed because the
declaration might use types defined by ``set_source()``
(e.g. ``event_t`` above, from the ``#include``), so it cannot be
generated before.

.. __: `extern-python-c`_

::

    ffibuilder.set_source("_demo_cffi", r"""
        #include <the_event_library.h>

        static void my_event_callback(widget_t *, event_t *);

        /* here you can write C code which uses '&my_event_callback' */
    """)

This can also be used to write custom C code which calls Python
directly.  Here is an example (inefficient in this case, but might be
useful if the logic in ``my_algo()`` is much more complex)::

    ffibuilder.cdef("""
        extern "Python" int f(int);
        int my_algo(int);
    """)
    ffibuilder.set_source("_example_cffi", r"""
        static int f(int);   /* the forward declaration */

        static int my_algo(int n) {
            int i, sum = 0;
            for (i = 0; i < n; i++)
                sum += f(i);     /* call f() here */
            return sum;
        }
    """)

.. _extern-python-c:

Extern "Python+C"
~~~~~~~~~~~~~~~~~

Functions declared with ``extern "Python"`` are generated as
``static`` functions in the C source.  However, in some cases it is
convenient to make them non-static, typically when you want to make
them directly callable from other C source files.  To do that, you can
say ``extern "Python+C"`` instead of just ``extern "Python"``.  *New
in version 1.6.*

+------------------------------------+--------------------------------------+
| if the cdef contains               | then CFFI generates                  |
+------------------------------------+--------------------------------------+
| ``extern "Python" int f(int);``    | ``static int f(int) { /* code */ }`` |
+------------------------------------+--------------------------------------+
| ``extern "Python+C" int f(int);``  | ``int f(int) { /* code */ }``        |
+------------------------------------+--------------------------------------+

The name ``extern "Python+C"`` comes from the fact that we want an
extern function in both senses: as an ``extern "Python"``, and as a
C function that is not static.

You cannot make CFFI generate additional macros or other
compiler-specific stuff like the GCC ``__attribute__``.  You can only
control whether the function should be ``static`` or not.  But often,
these attributes must be written alongside the function *header*, and
it is fine if the function *implementation* does not repeat them::

    ffibuilder.cdef("""
        extern "Python+C" int f(int);      /* not static */
    """)
    ffibuilder.set_source("_example_cffi", r"""
        /* the forward declaration, setting a gcc attribute
           (this line could also be in some .h file, to be included
           both here and in the other C files of the project) */
        int f(int) __attribute__((visibility("hidden")));
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
    callbacks: it gives faster and cleaner code.  It also avoids several
    issues with old-style callbacks:

    - On less common architecture, libffi is more likely to crash on
      callbacks (`e.g. on NetBSD`__);

    - On hardened systems like PAX and SELinux, the extra memory
      protections can interfere (for example, on SELinux you need to
      run with ``deny_execmem`` set to ``off``).

    Note also that a cffi fix for the latter issue was attempted---see
    the ``ffi_closure_alloc`` branch---but was not merged because it
    creates potential `memory corruption`__ with ``fork()``.

.. __: https://github.com/pyca/pyopenssl/issues/596
.. __: https://bugzilla.redhat.com/show_bug.cgi?id=1249685

Warning: like ffi.new(), ffi.callback() returns a cdata that has
ownership of its C data.  (In this case, the necessary C data contains
the libffi data structures to do a callback.)  This means that the
callback can only be invoked as long as this cdata object is alive.
If you store the function pointer into C code, then make sure you also
keep this object alive for as long as the callback may be invoked.
The easiest way to do that is to always use ``@ffi.callback()`` at
module-level only, and to pass "context" information around with
`ffi.new_handle()`__, if possible.  Example:

.. __: ref.html#new-handle

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
            print "method called!"

(See also the section about `extern "Python"`_ above, where the same
general style is used.)

Note that callbacks of a variadic function type are not supported.  A
workaround is to add custom C code.  In the following example, a
callback gets a first argument that counts how many extra ``int``
arguments are passed:

.. code-block:: python

    # file "example_build.py"

    import cffi

    ffibuilder = cffi.FFI()
    ffibuilder.cdef("""
        int (*python_callback)(int how_many, int *values);
        void *const c_callback;   /* pass this const ptr to C routines */
    """)
    ffibuilder.set_source("_example", r"""
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
    ffibuilder.compile(verbose=True)

.. code-block:: python
    
    # file "example.py"

    from _example import ffi, lib

    @ffi.callback("int(int, int *)")
    def python_callback(how_many, values):
        print ffi.unpack(values, how_many)
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

    ffibuilder.cdef("""
        struct foo_s {
            int (__stdcall *MyFuncPtr)(int, int);
        };
    """)

``__cdecl`` is supported but is always the default so it can be left
out.  In the ``cdef()``, you can also use ``WINAPI`` as equivalent to
``__stdcall``.  As mentioned above, it is mostly not needed (but doesn't
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

(The reference for the FFI interface has been moved to the `next page`__.)

.. __: ref.html

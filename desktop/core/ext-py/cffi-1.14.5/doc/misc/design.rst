================
Design decisions
================

* Generally follow LuaJIT's ffi: http://luajit.org/ext_ffi.html

* Be explicit: almost no automatic conversions.  Here is the set
  of automatic conversions: the various C integer types are
  automatically wrapped and unwrapped to regular applevel integers.  The
  type ``char`` might correspond to single-character strings instead;
  for integer correspondance you would use ``signed char`` or ``unsigned
  char``.  We might also decide that ``const char *`` automatically maps
  to strings; for cases where you don't want that, use ``char *``.

* Integers are not automatically converted when passed as vararg
  arguments.  You have to use explicitly ``ffi.new("int", 42)`` or
  ``ffi.new("long", 42)`` to resolve the ambiguity.  Floats would be
  fine (varargs in C can only accept ``double``, not ``float``), but
  there is again ambiguity between characters and strings.  Even with
  floats the result is a bit strange because passing a float works
  but passing an integer not.  I would fix this once and for all by
  saying that varargs must *always* be a cdata (from ``ffi.new()``).
  The possibly acceptable exception would be None (for ``NULL``).

* The internal class ``blob`` is used for raw-malloced data.  You only
  get a class that has internally a ``blob`` instance (or maybe is a
  subclass of ``blob``) by calling ``ffi.new(struct-or-array-type)``.
  The other cases, namely the cases where the type is a pointer or a
  primitive, don't need a blob because it's not possible to take their
  raw address.

* It would be possible to add a debug mode: when we cast ``struct foo``
  to ``struct foo *`` or store it in some other struct, then we would
  additionally record a weakref to the original ``struct foo`` blob.
  If later we try to access the ``struct foo *`` but the weakref shows
  that the blob was freed, we complain.  This is a difference with
  ctypes, which in these cases would store a strong reference and
  keep the blob alive.  "Explicit is better than implicit", so we ask
  the user to keep a reference to the original blob alive as long as
  it may be used (instead of doing the right things in 90% of the cases
  but still crashing in the remaining 10%).

* LuaJIT uses ``struct foo &`` for a number of things, like for ``p[0]``
  if ``p`` is a ``struct foo *``.  I suppose it's not a bad idea at least
  to have internally such types, even if you can't specify them through
  pycparser.  Basically ``struct foo &`` is a type that doesn't own a
  blob, whereas ``struct foo`` is the type that does.

* LuaJIT uses ``int[?]`` which pycparser doesn't accept.  I propose
  instead to use ``int[]`` for the same purpose (its use is anyway quite
  close to the C standard's use of ``int[]``).

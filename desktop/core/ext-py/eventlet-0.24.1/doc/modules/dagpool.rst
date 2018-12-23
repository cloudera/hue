:mod:`dagpool` -- Dependency-Driven Greenthreads
================================================

Rationale
*********

The dagpool module provides the :class:`DAGPool <eventlet.dagpool.DAGPool>`
class, which addresses situations in which the value produced by one
greenthread might be consumed by several others -- while at the same time a
consuming greenthread might depend on the output from several different
greenthreads.

If you have a tree with strict many-to-one dependencies -- each producer
greenthread provides results to exactly one consumer, though a given consumer
may depend on multiple producers -- that could be addressed by recursively
constructing a :class:`GreenPool <eventlet.greenpool.GreenPool>` of producers
for each consumer, then :meth:`waiting <eventlet.greenpool.GreenPool.waitall>`
for all producers.

If you have a tree with strict one-to-many dependencies -- each consumer
greenthread depends on exactly one producer, though a given producer may
provide results to multiple consumers -- that could be addressed by causing
each producer to finish by launching a :class:`GreenPool
<eventlet.greenpool.GreenPool>` of consumers.

But when you have many-to-many dependencies, a tree doesn't suffice. This is
known as a
`Directed Acyclic Graph <https://en.wikipedia.org/wiki/Directed_acyclic_graph>`_,
or DAG.

You might consider sorting the greenthreads into dependency order
(`topological sort <https://en.wikipedia.org/wiki/Topological_sorting>`_) and
launching them in a GreenPool. But the concurrency of the GreenPool must be
strictly constrained to ensure that no greenthread is launched before all its
upstream producers have completed -- and the appropriate pool size is
data-dependent. Only a pool of size 1 (serializing all the greenthreads)
guarantees that a topological sort will produce correct results.

Even if you do serialize all the greenthreads, how do you pass results from
each producer to all its consumers, which might start at very different points
in time?

One answer is to associate each greenthread with a distinct key, and store its
result in a common dict. Then each consumer greenthread can identify its
direct upstream producers by their keys, and find their results in that dict.

This is the essence of DAGPool.

A DAGPool instance owns a dict, and stores greenthread results in that dict.
You :meth:`spawn <eventlet.dagpool.DAGPool.spawn>` *all* greenthreads in the
DAG, specifying for each its own key -- the key with which its result will be
stored on completion -- plus the keys of the upstream producer greenthreads on
whose results it directly depends.

Keys need only be unique within the DAGPool instance; they need not be UUIDs.
A key can be any type that can be used as a dict key. String keys make it
easier to reason about a DAGPool's behavior, but are by no means required.

The DAGPool passes to each greenthread an iterable of (key, value) pairs.
The key in each pair is the key of one of the greenthread's specified upstream
producers; the value is the value returned by that producer greenthread. Pairs
are delivered in the order results become available; the consuming greenthread
blocks until the next result can be delivered.

Tutorial
*******
Example
-------

Consider a couple of programs in some compiled language that depend on a set
of precompiled libraries. Suppose every such build requires as input the
specific set of library builds on which it directly depends.

::

    a  zlib
    | /  |
    |/   |
    b    c
    |   /|
    |  / |
    | /  |
    |/   |
    d    e

We can't run the build for program d until we have the build results for both
b and c. We can't run the build for library b until we have build results for
a and zlib. We can, however, immediately run the builds for a and zlib.

So we can use a DAGPool instance to spawn greenthreads running a function such
as this:

::

    def builder(key, upstream):
        for libname, product in upstream:
            # ... configure build for 'key' to use 'product' for 'libname'
        # all upstream builds have completed
        # ... run build for 'key'
        return build_product_for_key

:meth:`spawn <eventlet.dagpool.DAGPool.spawn>` all these greenthreads:

::

    pool = DAGPool()
    # the upstream producer keys passed to spawn() can be from any iterable,
    # including a generator
    pool.spawn("d", ("b", "c"), builder)
    pool.spawn("e", ["c"], builder)
    pool.spawn("b", ("a", "zlib"), builder)
    pool.spawn("c", ["zlib"], builder)
    pool.spawn("a", (), builder)

As with :func:`eventlet.spawn() <eventlet.spawn>`, if you need to pass special
build flags to some set of builds, these can be passed as either positional or
keyword arguments:

::

    def builder(key, upstream, cflags="", linkflags=""):
        ...

    pool.spawn("d", ("b", "c"), builder, "-o2")
    pool.spawn("e", ["c"], builder, linkflags="-pie")

However, if the arguments to each builder() call are uniform (as in the
original example), you could alternatively build a dict of the dependencies
and call :meth:`spawn_many() <eventlet.dagpool.DAGPool.spawn_many>`:

::

    deps = dict(d=("b", "c"),
                e=["c"],
                b=("a", "zlib"),
                c=["zlib"],
                a=())
    pool.spawn_many(deps, builder)

From outside the DAGPool, you can obtain the results for d and e (or in fact
for any of the build greenthreads) in any of several ways.

:meth:`pool.waitall() <eventlet.dagpool.DAGPool.waitall>` waits until the last of the spawned
greenthreads has completed, and returns a dict containing results for *all* of
them:

::

    final = pool.waitall()
    print("for d: {0}".format(final["d"]))
    print("for e: {0}".format(final["e"]))

waitall() is an alias for :meth:`wait() <eventlet.dagpool.DAGPool.wait>` with no arguments:

::

    final = pool.wait()
    print("for d: {0}".format(final["d"]))
    print("for e: {0}".format(final["e"]))

Or you can specifically wait for only the final programs:

::

    final = pool.wait(["d", "e"])

The returned dict will contain only the specified keys. The keys may be passed
into wait() from any iterable, including a generator.

You can wait for any specified set of greenthreads; they need not be
topologically last:

::

    # returns as soon as both a and zlib have returned results, regardless of
    # what else is still running
    leaves = pool.wait(["a", "zlib"])

Suppose you want to wait specifically for just *one* of the final programs:

::

    final = pool.wait(["d"])
    dprog = final["d"]

The above wait() call will return as soon as greenthread d returns a result --
regardless of whether greenthread e has finished.

:meth:`__getitem()__ <eventlet.dagpool.DAGPool.__getitem__>` is shorthand for
obtaining a single result:

::

    # waits until greenthread d returns its result
    dprog = pool["d"]

In contrast, :meth:`get() <eventlet.dagpool.DAGPool.get>` returns immediately,
whether or not a result is ready:

::

    # returns immediately
    if pool.get("d") is None:
        ...

Of course, your greenthread might not include an explicit return statement and
hence might implicitly return None. You might have to test some other value.

::

    # returns immediately
    if pool.get("d", "notdone") == "notdone":
        ...

Suppose you want to process each of the final programs in some way (upload
it?), but you don't want to have to wait until they've both finished. You
don't have to poll get() calls -- use :meth:`wait_each()
<eventlet.dagpool.DAGPool.wait_each>`:

::

    for key, result in pool.wait_each(["d", "e"]):
        # key will be d or e, in completion order
        # process result...

As with :meth:`wait() <eventlet.dagpool.DAGPool.wait>`, if you omit the
argument to wait_each(), it delivers results for all the greenthreads of which
it's aware:

::

    for key, result in pool.wait_each():
        # key will be a, zlib, b, c, d, e, in whatever order each completes
        # process its result...

Introspection
-------------

Let's say you have set up a :class:`DAGPool <eventlet.dagpool.DAGPool>` with
the dependencies shown above. To your consternation, your :meth:`waitall()
<eventlet.dagpool.DAGPool.waitall>` call does not return! The DAGPool instance
is stuck!

You could change waitall() to :meth:`wait_each()
<eventlet.dagpool.DAGPool.wait_each>`, and print each key as it becomes
available:

::

    for key, result in pool.wait_each():
        print("got result for {0}".format(key))
        # ... process ...

Once the build for a has completed, this produces:

::

    got result for a

and then stops. Hmm!

You can check the number of :meth:`running <eventlet.dagpool.DAGPool.running>`
greenthreads:

::

    >>> print(pool.running())
    4

and the number of :meth:`waiting <eventlet.dagpool.DAGPool.waiting>`
greenthreads:

::

    >>> print(pool.waiting())
    4

It's often more informative to ask *which* greenthreads are :meth:`still
running <eventlet.dagpool.DAGPool.running_keys>`:

::

    >>> print(pool.running_keys())
    ('c', 'b', 'e', 'd')

but in this case, we already know a has completed.

We can ask for all available results:

::

    >>> print(pool.keys())
    ('a',)
    >>> print(pool.items())
    (('a', result_from_a),)

The :meth:`keys() <eventlet.dagpool.DAGPool.keys>` and :meth:`items()
<eventlet.dagpool.DAGPool.items>` methods only return keys and items for
which results are actually available, reflecting the underlying dict.

But what's blocking the works? What are we :meth:`waiting for
<eventlet.dagpool.DAGPool.waiting_for>`?

::

    >>> print(pool.waiting_for("d"))
    set(['c', 'b'])

(waiting_for()'s optional argument is a *single* key.)

That doesn't help much yet...

::

    >>> print(pool.waiting_for("b"))
    set(['zlib'])
    >>> print(pool.waiting_for("zlib"))
    KeyError: 'zlib'

Aha! We forgot to even include the zlib build when we were originally
configuring this DAGPool!

(For non-interactive use, it would be more informative to omit waiting_for()'s
argument. This usage returns a dict indicating, for each greenthread key,
which other keys it's waiting for.)

::

    from pprint import pprint
    pprint(pool.waiting_for())

    {'b': set(['zlib']), 'c': set(['zlib']), 'd': set(['b', 'c']), 'e': set(['c'])}

In this case, a reasonable fix would be to spawn the zlib greenthread:

::

    pool.spawn("zlib", (), builder)

Even if this is the last method call on this DAGPool instance, it should
unblock all the rest of the DAGPool greenthreads.

Posting
-------

If we happen to have zlib build results in hand already, though, we could
instead :meth:`post() <eventlet.dagpool.DAGPool.post>` that result instead of
rebuilding the library:

::

    pool.post("zlib", result_from_zlib)

This, too, should unblock the rest of the DAGPool greenthreads.

Preloading
----------

If rebuilding takes nontrivial realtime, it might be useful to record partial
results, so that in case of interruption you can restart from where you left
off rather than having to rebuild everything prior to that point.

You could iteratively :meth:`post() <eventlet.dagpool.DAGPool.post>` those
prior results into a new DAGPool instance; alternatively you can
:meth:`preload <eventlet.dagpool.DAGPool.__init__>` the :class:`DAGPool
<eventlet.dagpool.DAGPool>` from an existing dict:

::

    pool = DAGPool(dict(a=result_from_a, zlib=result_from_zlib))

Any DAGPool greenthreads that depend on either a or zlib can immediately
consume those results.

It also works to construct DAGPool with an iterable of (key, result) pairs.

Exception Propagation
---------------------

But what if we spawn a zlib build that fails? Suppose the zlib greenthread
terminates with an exception? In that case none of b, c, d or e can proceed!
Nor do we want to wait forever for them.

::

    dprog = pool["d"]
    eventlet.dagpool.PropagateError: PropagateError(d): PropagateError: PropagateError(c): PropagateError: PropagateError(zlib): OriginalError

DAGPool provides a :class:`PropagateError <eventlet.dagpool.PropagateError>`
exception specifically to wrap such failures. If a DAGPool greenthread
terminates with an Exception subclass, the DAGPool wraps that exception in a
PropagateError instance whose *key* attribute is the key of the failing
greenthread and whose *exc* attribute is the exception that terminated it.
This PropagateError is stored as the result from that greenthread.

Attempting to consume the result from a greenthread for which a PropagateError
was stored raises that PropagateError.

::

    pool["zlib"]
    eventlet.dagpool.PropagateError: PropagateError(zlib): OriginalError

Thus, when greenthread c attempts to consume the result from zlib, the
PropagateError for zlib is raised. Unless the builder function for greenthread
c handles that PropagateError exception, that greenthread will itself
terminate. That PropagateError will be wrapped in another PropagateError whose
*key* attribute is c and whose *exc* attribute is the PropagateError for zlib.

Similarly, when greenthread d attempts to consume the result from c, the
PropagateError for c is raised. This in turn is wrapped in a PropagateError
whose *key* is d and whose *exc* is the PropagateError for c.

When someone attempts to consume the result from d, as shown above, the
PropagateError for d is raised.

You can programmatically chase the failure path to determine the original
failure if desired:

::

    orig_err = err
    key = "unknown"
    while isinstance(orig_err, PropagateError):
        key = orig_err.key
        orig_err = orig_err.exc

Scanning for Success / Exceptions
---------------------------------

Exception propagation means that we neither perform useless builds nor wait for
results that will never arrive.

However, it does make it difficult to obtain *partial* results for builds that
*did* succeed.

For that you can call :meth:`wait_each_success()
<eventlet.dagpool.DAGPool.wait_each_success>`:

::

    for key, result in pool.wait_each_success():
        print("{0} succeeded".format(key))
        # ... process result ...

    a succeeded

Another problem is that although five different greenthreads failed in the
example, we only see one chain of failures. You can enumerate the bad news
with :meth:`wait_each_exception() <eventlet.dagpool.DAGPool.wait_each_exception>`:

::

    for key, err in pool.wait_each_exception():
        print("{0} failed with {1}".format(key, err.exc.__class__.__name__))

    c failed with PropagateError
    b failed with PropagateError
    e failed with PropagateError
    d failed with PropagateError
    zlib failed with OriginalError

wait_each_exception() yields each PropagateError wrapper as if it were the
result, rather than raising it as an exception.

Notice that we print :code:`err.exc.__class__.__name__` because
:code:`err.__class__.__name__` is always PropagateError.

Both wait_each_success() and wait_each_exception() can accept an iterable of
keys to report:

::

    for key, result in pool.wait_each_success(["d", "e"]):
        print("{0} succeeded".format(key))

    (no output)

    for key, err in pool.wait_each_exception(["d", "e"]):
        print("{0} failed with {1}".format(key, err.exc.__class__.__name__))

    e failed with PropagateError
    d failed with PropagateError

Both wait_each_success() and wait_each_exception() must wait until the
greenthreads for all specified keys (or all keys) have terminated, one way or
the other, because of course we can't know until then how to categorize each.

Module Contents
===============

.. automodule:: eventlet.dagpool
	:members:

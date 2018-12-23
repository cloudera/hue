"""\
@file   dagpool_test.py
@author Nat Goodspeed
@date   2016-08-26
@brief  Test DAGPool class
"""

from nose.tools import *
import eventlet
from eventlet.dagpool import DAGPool, Collision, PropagateError
import six
from contextlib import contextmanager
import itertools


# Not all versions of nose.tools.assert_raises() support the usage in this
# module, but it's straightforward enough to code that explicitly.
@contextmanager
def assert_raises(exc):
    """exc is an exception class"""
    try:
        yield
    except exc:
        pass
    else:
        raise AssertionError("failed to raise expected exception {0}"
                             .format(exc.__class__.__name__))


def assert_in(sought, container):
    assert sought in container, "{0} not in {1}".format(sought, container)


# ****************************************************************************
#   Verify that a given operation returns without suspending
# ****************************************************************************
# module-scope counter allows us to verify when the main greenthread running
# the test does or does not suspend
counter = None


def incrementer():
    """
    This function runs as a background greenthread. Every time it regains
    control, it increments 'counter' and relinquishes control again. The point
    is that by testing 'counter' before and after a particular operation, a
    test can determine whether other greenthreads were allowed to run during
    that operation -- in other words, whether that operation suspended.
    """
    global counter
    # suspend_checker() initializes counter to 0, so the first time we get
    # control, set it to 1
    for counter in itertools.count(1):
        eventlet.sleep(0)


@contextmanager
def suspend_checker():
    """
    This context manager enables check_no_suspend() support. It runs the
    incrementer() function as a background greenthread, then kills it off when
    you exit the block.
    """
    global counter
    # make counter not None to enable check_no_suspend()
    counter = 0
    coro = eventlet.spawn(incrementer)
    yield
    coro.kill()
    # set counter back to None to disable check_no_suspend()
    counter = None


@contextmanager
def check_no_suspend():
    """
    Within a 'with suspend_checker()' block, use 'with check_no_suspend()' to
    verify that a particular operation does not suspend the calling
    greenthread. If it does suspend, incrementer() will have regained control
    and incremented the global 'counter'.
    """
    global counter
    # It would be an easy mistake to use check_no_suspend() outside of a
    # suspend_checker() block. Without the incrementer() greenthread running,
    # 'counter' will never be incremented, therefore check_no_suspend() will
    # always be satisfied, possibly masking bugs.
    assert counter is not None, "Use 'with suspend_checker():' to enable check_no_suspend()"
    current = counter
    yield
    assert counter == current, "Operation suspended {0} times".format(counter - current)


def test_check_no_suspend():
    with assert_raises(AssertionError):
        # We WANT this to raise AssertionError because it's outside of a
        # suspend_checker() block -- that is, we have no incrementer()
        # greenthread.
        with check_no_suspend():
            pass

    # Here we use check_no_suspend() the right way, inside 'with
    # suspend_checker()'. Does it really do what we claim it should?
    with suspend_checker():
        with assert_raises(AssertionError):
            with check_no_suspend():
                # suspend, so we know if check_no_suspend() asserts
                eventlet.sleep(0)


# ****************************************************************************
#   Verify that the expected things happened in the expected order
# ****************************************************************************
class Capture(object):
    """
    This class is intended to capture a sequence (of string messages) to
    verify that all expected events occurred, and in the expected order. The
    tricky part is that certain subsequences can occur in arbitrary order and
    still be correct.

    Specifically, when posting a particular value to a DAGPool instance
    unblocks several waiting greenthreads, it is indeterminate which
    greenthread will first receive the new value.

    Similarly, when several values for which a particular greenthread is
    waiting become available at (effectively) the same time, it is
    indeterminate in which order they will be delivered.

    This is addressed by building a list of sets. Each set contains messages
    that can occur in indeterminate order, therefore comparing that set to any
    other ordering of the same messages should succeed. However, it's
    important that each set of messages that occur 'at the same time' should
    itself be properly sequenced with respect to all other such sets.
    """
    def __init__(self):
        self.sequence = [set()]

    def add(self, message):
        self.sequence[-1].add(message)

    def step(self):
        self.sequence.append(set())

    def validate(self, sequence):
        # Let caller pass any sequence of grouped items. For comparison
        # purposes, turn them into the specific form we store: a list of sets.
        setlist = []
        for subseq in sequence:
            if isinstance(subseq, six.string_types):
                # If this item is a plain string (which Python regards as an
                # iterable of characters) rather than a list or tuple or set
                # of strings, treat it as atomic. Make a set containing only
                # that string.
                setlist.append(set([subseq]))
            else:
                try:
                    iter(subseq)
                except TypeError:
                    # subseq is a scalar of some other kind. Make a set
                    # containing only that item.
                    setlist.append(set([subseq]))
                else:
                    # subseq is, as we expect, an iterable -- possibly already
                    # a set. Make a set containing its elements.
                    setlist.append(set(subseq))
        # Now that we've massaged 'sequence' into 'setlist', compare.
        assert_equal(self.sequence, setlist)


# ****************************************************************************
#   Canonical DAGPool greenthread function
# ****************************************************************************
def observe(key, results, capture, event):
    for k, v in results:
        capture.add("{0} got {1}".format(key, k))
    result = event.wait()
    capture.add("{0} returning {1}".format(key, result))
    return result


# ****************************************************************************
#   DAGPool test functions
# ****************************************************************************
def test_init():
    with suspend_checker():
        # no preload data, just so we know it doesn't blow up
        pool = DAGPool()

        # preload dict
        pool = DAGPool(dict(a=1, b=2, c=3))
        # this must not hang
        with check_no_suspend():
            results = pool.waitall()
        # with no spawn() or post(), waitall() returns preload data
        assert_equals(results, dict(a=1, b=2, c=3))

        # preload sequence of pairs
        pool = DAGPool([("d", 4), ("e", 5), ("f", 6)])
        # this must not hang
        with check_no_suspend():
            results = pool.waitall()
        assert_equals(results, dict(d=4, e=5, f=6))


def test_wait_each_empty():
    pool = DAGPool()
    with suspend_checker():
        with check_no_suspend():
            for k, v in pool.wait_each(()):
                # shouldn't yield anything
                raise AssertionError("empty wait_each() returned ({0}, {1})".format(k, v))


def test_wait_each_preload():
    pool = DAGPool(dict(a=1, b=2, c=3))
    with suspend_checker():
        with check_no_suspend():
            # wait_each() may deliver in arbitrary order; collect into a dict
            # for comparison
            assert_equals(dict(pool.wait_each("abc")), dict(a=1, b=2, c=3))

            # while we're at it, test wait() for preloaded keys
            assert_equals(pool.wait("bc"), dict(b=2, c=3))


def post_each(pool, capture):
    # distinguish the results wait_each() can retrieve immediately from those
    # it must wait for us to post()
    eventlet.sleep(0)
    capture.step()
    pool.post('g', 'gval')
    pool.post('f', 'fval')
    eventlet.sleep(0)
    capture.step()
    pool.post('e', 'eval')
    pool.post('d', 'dval')


def test_wait_each_posted():
    capture = Capture()
    pool = DAGPool(dict(a=1, b=2, c=3))
    eventlet.spawn(post_each, pool, capture)
    # use a string as a convenient iterable of single-letter keys
    for k, v in pool.wait_each("bcdefg"):
        capture.add("got ({0}, {1})".format(k, v))

    capture.validate([
        ["got (b, 2)", "got (c, 3)"],
        ["got (f, fval)", "got (g, gval)"],
        ["got (d, dval)", "got (e, eval)"],
    ])


def test_wait_posted():
    # same as test_wait_each_posted(), but calling wait()
    capture = Capture()
    pool = DAGPool(dict(a=1, b=2, c=3))
    eventlet.spawn(post_each, pool, capture)
    gotten = pool.wait("bcdefg")
    capture.add("got all")
    assert_equals(gotten,
                  dict(b=2, c=3,
                       d="dval", e="eval",
                       f="fval", g="gval"))
    capture.validate([
        [],
        [],
        ["got all"],
    ])


def test_spawn_collision_preload():
    pool = DAGPool([("a", 1)])
    with assert_raises(Collision):
        pool.spawn("a", (), lambda key, results: None)


def test_spawn_collision_post():
    pool = DAGPool()
    pool.post("a", "aval")
    with assert_raises(Collision):
        pool.spawn("a", (), lambda key, results: None)


def test_spawn_collision_spawn():
    pool = DAGPool()
    pool.spawn("a", (), lambda key, results: "aval")
    # hasn't yet even started
    assert_equals(pool.get("a"), None)
    with assert_raises(Collision):
        # Attempting to spawn again with same key should collide even if the
        # first spawned greenthread hasn't yet had a chance to run.
        pool.spawn("a", (), lambda key, results: "bad")
    # now let the spawned eventlet run
    eventlet.sleep(0)
    # should have finished
    assert_equals(pool.get("a"), "aval")
    with assert_raises(Collision):
        # Attempting to spawn with same key collides even when the greenthread
        # has completed.
        pool.spawn("a", (), lambda key, results: "badagain")


def spin():
    # Let all pending greenthreads run until they're blocked
    for x in range(10):
        eventlet.sleep(0)


def test_spawn_multiple():
    capture = Capture()
    pool = DAGPool(dict(a=1, b=2, c=3))
    events = {}
    for k in "defg":
        events[k] = eventlet.event.Event()
        pool.spawn(k, (), observe, capture, events[k])
    # Now for a greenthread that depends on ALL the above.
    events["h"] = eventlet.event.Event()
    # trigger the last event right away: we only care about dependencies
    events["h"].send("hval")
    pool.spawn("h", "bcdefg", observe, capture, events["h"])

    # let all the spawned greenthreads get as far as they can
    spin()
    capture.step()
    # but none of them has yet produced a result
    for k in "defgh":
        assert_equals(pool.get(k), None)
    assert_equals(set(pool.keys()), set("abc"))
    assert_equals(dict(pool.items()), dict(a=1, b=2, c=3))
    assert_equals(pool.running(), 5)
    assert_equals(set(pool.running_keys()), set("defgh"))
    assert_equals(pool.waiting(), 1)
    assert_equals(pool.waiting_for(), dict(h=set("defg")))
    assert_equals(pool.waiting_for("d"), set())
    assert_equals(pool.waiting_for("c"), set())
    with assert_raises(KeyError):
        pool.waiting_for("j")
    assert_equals(pool.waiting_for("h"), set("defg"))

    # let one of the upstream greenthreads complete
    events["f"].send("fval")
    spin()
    capture.step()
    assert_equals(pool.get("f"), "fval")
    assert_equals(set(pool.keys()), set("abcf"))
    assert_equals(dict(pool.items()), dict(a=1, b=2, c=3, f="fval"))
    assert_equals(pool.running(), 4)
    assert_equals(set(pool.running_keys()), set("degh"))
    assert_equals(pool.waiting(), 1)
    assert_equals(pool.waiting_for("h"), set("deg"))

    # now two others
    events["e"].send("eval")
    events["g"].send("gval")
    spin()
    capture.step()
    assert_equals(pool.get("e"), "eval")
    assert_equals(pool.get("g"), "gval")
    assert_equals(set(pool.keys()), set("abcefg"))
    assert_equals(dict(pool.items()),
                  dict(a=1, b=2, c=3, e="eval", f="fval", g="gval"))
    assert_equals(pool.running(), 2)
    assert_equals(set(pool.running_keys()), set("dh"))
    assert_equals(pool.waiting(), 1)
    assert_equals(pool.waiting_for("h"), set("d"))

    # last one
    events["d"].send("dval")
    # make sure both pool greenthreads get a chance to run
    spin()
    capture.step()
    assert_equals(pool.get("d"), "dval")
    assert_equals(set(pool.keys()), set("abcdefgh"))
    assert_equals(dict(pool.items()),
                  dict(a=1, b=2, c=3,
                       d="dval", e="eval", f="fval", g="gval", h="hval"))
    assert_equals(pool.running(), 0)
    assert_false(pool.running_keys())
    assert_equals(pool.waiting(), 0)
    assert_equals(pool.waiting_for("h"), set())

    capture.validate([
        ["h got b", "h got c"],
        ["f returning fval", "h got f"],
        ["e returning eval", "g returning gval",
         "h got e", "h got g"],
        ["d returning dval", "h got d", "h returning hval"],
        [],
    ])


def spawn_many_func(key, results, capture, pool):
    for k, v in results:
        # with a capture.step() at each post(), too complicated to predict
        # which results will be delivered when
        pass
    capture.add("{0} done".format(key))
    # use post(key) instead of waiting for implicit post() of return value
    pool.post(key, key)
    capture.step()
    spin()


def waitall_done(capture, pool):
    pool.waitall()
    capture.add("waitall() done")


def test_spawn_many():
    # This dependencies dict sets up a graph like this:
    #         a
    #        / \
    #       b   c
    #        \ /|
    #         d |
    #          \|
    #           e

    deps = dict(e="cd",
                d="bc",
                c="a",
                b="a",
                a="")

    capture = Capture()
    pool = DAGPool()
    # spawn a waitall() waiter externally to our DAGPool, but capture its
    # message in same Capture instance
    eventlet.spawn(waitall_done, capture, pool)
    pool.spawn_many(deps, spawn_many_func, capture, pool)
    # This set of greenthreads should in fact run to completion once spawned.
    spin()
    # verify that e completed (also that post(key) within greenthread
    # overrides implicit post of return value, which would be None)
    assert_equals(pool.get("e"), "e")

    # With the dependency graph shown above, it is not guaranteed whether b or
    # c will complete first. Handle either case.
    sequence = capture.sequence[:]
    sequence[1:3] = [set([sequence[1].pop(), sequence[2].pop()])]
    assert_equals(sequence,
                  [set(["a done"]),
                   set(["b done", "c done"]),
                   set(["d done"]),
                   set(["e done"]),
                   set(["waitall() done"]),
                   ])


# deliberately distinguish this from dagpool._MISSING
_notthere = object()


def test_wait_each_all():
    # set up a simple linear dependency chain
    deps = dict(b="a", c="b", d="c", e="d")
    capture = Capture()
    pool = DAGPool([("a", "a")])
    # capture a different Event for each key
    events = dict((key, eventlet.event.Event()) for key in six.iterkeys(deps))
    # can't use spawn_many() because we need a different event for each
    for key, dep in six.iteritems(deps):
        pool.spawn(key, dep, observe, capture, events[key])
    keys = "abcde"                      # this specific order
    each = iter(pool.wait_each())
    for pos in range(len(keys)):
        # next value from wait_each()
        k, v = next(each)
        assert_equals(k, keys[pos])
        # advance every pool greenlet as far as it can go
        spin()
        # everything from keys[:pos+1] should have a value by now
        for k in keys[:pos + 1]:
            assert pool.get(k, _notthere) is not _notthere, \
                "greenlet {0} did not yet produce a value".format(k)
        # everything from keys[pos+1:] should not yet
        for k in keys[pos + 1:]:
            assert pool.get(k, _notthere) is _notthere, \
                "wait_each() delayed value for {0}".format(keys[pos])
        # let next greenthread complete
        if pos < len(keys) - 1:
            k = keys[pos + 1]
            events[k].send(k)


def test_kill():
    pool = DAGPool()
    # nonexistent key raises KeyError
    with assert_raises(KeyError):
        pool.kill("a")
    # spawn a greenthread
    pool.spawn("a", (), lambda key, result: 1)
    # kill it before it can even run
    pool.kill("a")
    # didn't run
    spin()
    assert_equals(pool.get("a"), None)
    # killing it forgets about it
    with assert_raises(KeyError):
        pool.kill("a")
    # so that we can try again
    pool.spawn("a", (), lambda key, result: 2)
    spin()
    # this time it ran to completion, so can no longer be killed
    with assert_raises(KeyError):
        pool.kill("a")
    # verify it ran to completion
    assert_equals(pool.get("a"), 2)


def test_post_collision_preload():
    pool = DAGPool(dict(a=1))
    with assert_raises(Collision):
        pool.post("a", 2)


def test_post_collision_post():
    pool = DAGPool()
    pool.post("a", 1)
    with assert_raises(Collision):
        pool.post("a", 2)


def test_post_collision_spawn():
    pool = DAGPool()
    pool.spawn("a", (), lambda key, result: 1)
    # hasn't yet run
    with assert_raises(Collision):
        # n.b. This exercises the code that tests whether post(key) is or is
        # not coming from that key's greenthread.
        pool.post("a", 2)
    # kill it
    pool.kill("a")
    # now we can post
    pool.post("a", 3)
    assert_equals(pool.get("a"), 3)

    pool = DAGPool()
    pool.spawn("a", (), lambda key, result: 4)
    # run it
    spin()
    with assert_raises(Collision):
        pool.post("a", 5)
    # can't kill it now either
    with assert_raises(KeyError):
        pool.kill("a")
    # still can't post
    with assert_raises(Collision):
        pool.post("a", 6)


def test_post_replace():
    pool = DAGPool()
    pool.post("a", 1)
    pool.post("a", 2, replace=True)
    assert_equals(pool.get("a"), 2)
    assert_equals(dict(pool.wait_each("a")), dict(a=2))
    assert_equals(pool.wait("a"), dict(a=2))
    assert_equals(pool["a"], 2)


def waitfor(capture, pool, key):
    value = pool[key]
    capture.add("got {0}".format(value))


def test_getitem():
    capture = Capture()
    pool = DAGPool()
    eventlet.spawn(waitfor, capture, pool, "a")
    # pool["a"] just waiting
    capture.validate([[]])
    pool.spawn("a", (), lambda key, results: 1)
    # still waiting: hasn't yet run
    capture.validate([[]])
    # run it
    spin()
    capture.validate([["got 1"]])


class BogusError(Exception):
    pass


def raiser(key, results, exc):
    raise exc


def consumer(key, results):
    for k, v in results:
        pass
    return True


def test_waitall_exc():
    pool = DAGPool()
    pool.spawn("a", (), raiser, BogusError("bogus"))
    try:
        pool.waitall()
    except PropagateError as err:
        assert_equals(err.key, "a")
        assert isinstance(err.exc, BogusError), \
            "exc attribute is {0}, not BogusError".format(err.exc)
        assert_equals(str(err.exc), "bogus")
        msg = str(err)
        assert_in("PropagateError(a)", msg)
        assert_in("BogusError", msg)
        assert_in("bogus", msg)


def test_propagate_exc():
    pool = DAGPool()
    pool.spawn("a", (), raiser, BogusError("bogus"))
    pool.spawn("b", "a", consumer)
    pool.spawn("c", "b", consumer)
    try:
        pool["c"]
    except PropagateError as errc:
        assert_equals(errc.key, "c")
        errb = errc.exc
        assert_equals(errb.key, "b")
        erra = errb.exc
        assert_equals(erra.key, "a")
        assert isinstance(erra.exc, BogusError), \
            "exc attribute is {0}, not BogusError".format(erra.exc)
        assert_equals(str(erra.exc), "bogus")
        msg = str(errc)
        assert_in("PropagateError(a)", msg)
        assert_in("PropagateError(b)", msg)
        assert_in("PropagateError(c)", msg)
        assert_in("BogusError", msg)
        assert_in("bogus", msg)


def test_wait_each_exc():
    pool = DAGPool()
    pool.spawn("a", (), raiser, BogusError("bogus"))
    with assert_raises(PropagateError):
        for k, v in pool.wait_each("a"):
            pass

    with assert_raises(PropagateError):
        for k, v in pool.wait_each():
            pass


def test_post_get_exc():
    pool = DAGPool()
    bogua = BogusError("bogua")
    pool.post("a", bogua)
    assert isinstance(pool.get("a"), BogusError), \
        "should have delivered BogusError instead of raising"
    bogub = PropagateError("b", BogusError("bogub"))
    pool.post("b", bogub)
    with assert_raises(PropagateError):
        pool.get("b")

    # Notice that although we have both "a" and "b" keys, items() is
    # guaranteed to raise PropagateError because one of them is
    # PropagateError. Other values don't matter.
    with assert_raises(PropagateError):
        pool.items()

    # Similar remarks about waitall() and wait().
    with assert_raises(PropagateError):
        pool.waitall()
    with assert_raises(PropagateError):
        pool.wait()
    with assert_raises(PropagateError):
        pool.wait("b")
    with assert_raises(PropagateError):
        pool.wait("ab")
    # but if we're only wait()ing for success results, no exception
    assert isinstance(pool.wait("a")["a"], BogusError), \
        "should have delivered BogusError instead of raising"

    # wait_each() is guaranteed to eventually raise PropagateError, though you
    # may obtain valid values before you hit it.
    with assert_raises(PropagateError):
        for k, v in pool.wait_each():
            pass

    # wait_each_success() filters
    assert_equals(dict(pool.wait_each_success()), dict(a=bogua))
    assert_equals(dict(pool.wait_each_success("ab")), dict(a=bogua))
    assert_equals(dict(pool.wait_each_success("a")), dict(a=bogua))
    assert_equals(dict(pool.wait_each_success("b")), {})

    # wait_each_exception() filters the other way
    assert_equals(dict(pool.wait_each_exception()), dict(b=bogub))
    assert_equals(dict(pool.wait_each_exception("ab")), dict(b=bogub))
    assert_equals(dict(pool.wait_each_exception("a")), {})
    assert_equals(dict(pool.wait_each_exception("b")), dict(b=bogub))

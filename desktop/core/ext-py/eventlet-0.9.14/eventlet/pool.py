from eventlet import coros, proc, api
from eventlet.semaphore import Semaphore

import warnings
warnings.warn("The pool module is deprecated.  Please use the "
        "eventlet.GreenPool and eventlet.GreenPile classes instead.",
        DeprecationWarning, stacklevel=2)

class Pool(object):
    def __init__(self, min_size=0, max_size=4, track_events=False):
        if min_size > max_size:
            raise ValueError('min_size cannot be bigger than max_size')
        self.max_size = max_size
        self.sem = Semaphore(max_size)
        self.procs = proc.RunningProcSet()
        if track_events:
            self.results = coros.queue()
        else:
            self.results = None

    def resize(self, new_max_size):
        """ Change the :attr:`max_size` of the pool.

        If the pool gets resized when there are more than *new_max_size*
        coroutines checked out, when they are returned to the pool they will be
        discarded.  The return value of :meth:`free` will be negative in this
        situation.
        """
        max_size_delta = new_max_size - self.max_size 
        self.sem.counter += max_size_delta
        self.max_size = new_max_size

    @property
    def current_size(self):
        """ The number of coroutines that are currently executing jobs. """
        return len(self.procs)

    def free(self):
        """ Returns the number of coroutines that are available for doing
        work."""
        return self.sem.counter

    def execute(self, func, *args, **kwargs):
        """Execute func in one of the coroutines maintained
        by the pool, when one is free.

        Immediately returns a :class:`~eventlet.proc.Proc` object which can be
        queried for the func's result.

        >>> pool = Pool()
        >>> task = pool.execute(lambda a: ('foo', a), 1)
        >>> task.wait()
        ('foo', 1)
        """
        # if reentering an empty pool, don't try to wait on a coroutine freeing
        # itself -- instead, just execute in the current coroutine
        if self.sem.locked() and api.getcurrent() in self.procs:
            p = proc.spawn(func, *args, **kwargs)
            try:
                p.wait()
            except:
                pass
        else:
            self.sem.acquire()
            p = self.procs.spawn(func, *args, **kwargs)
            # assuming the above line cannot raise
            p.link(lambda p: self.sem.release())
        if self.results is not None:
            p.link(self.results)
        return p

    execute_async = execute

    def _execute(self, evt, func, args, kw):
        p = self.execute(func, *args, **kw)
        p.link(evt)
        return p

    def waitall(self):
        """ Calling this function blocks until every coroutine 
        completes its work (i.e. there are 0 running coroutines)."""
        return self.procs.waitall()

    wait_all = waitall

    def wait(self):
        """Wait for the next execute in the pool to complete,
        and return the result."""
        return self.results.wait()
        
    def waiting(self):
        """Return the number of coroutines waiting to execute.
        """
        if self.sem.balance < 0:
            return -self.sem.balance
        else:
            return 0

    def killall(self):
        """ Kill every running coroutine as immediately as possible."""
        return self.procs.killall()

    def launch_all(self, function, iterable):
        """For each tuple (sequence) in *iterable*, launch ``function(*tuple)``
        in its own coroutine -- like ``itertools.starmap()``, but in parallel.
        Discard values returned by ``function()``. You should call
        ``wait_all()`` to wait for all coroutines, newly-launched plus any
        previously-submitted :meth:`execute` or :meth:`execute_async` calls, to
        complete.

        >>> pool = Pool()
        >>> def saw(x):
        ...     print "I saw %s!" % x
        ...
        >>> pool.launch_all(saw, "ABC")
        >>> pool.wait_all()
        I saw A!
        I saw B!
        I saw C!
        """
        for tup in iterable:
            self.execute(function, *tup)

    def process_all(self, function, iterable):
        """For each tuple (sequence) in *iterable*, launch ``function(*tuple)``
        in its own coroutine -- like ``itertools.starmap()``, but in parallel.
        Discard values returned by ``function()``. Don't return until all
        coroutines, newly-launched plus any previously-submitted :meth:`execute()`
        or :meth:`execute_async` calls, have completed.

        >>> from eventlet import coros
        >>> pool = coros.CoroutinePool()
        >>> def saw(x): print "I saw %s!" % x
        ...
        >>> pool.process_all(saw, "DEF")
        I saw D!
        I saw E!
        I saw F!
        """
        self.launch_all(function, iterable)
        self.wait_all()

    def generate_results(self, function, iterable, qsize=None):
        """For each tuple (sequence) in *iterable*, launch ``function(*tuple)``
        in its own coroutine -- like ``itertools.starmap()``, but in parallel.
        Yield each of the values returned by ``function()``, in the order
        they're completed rather than the order the coroutines were launched.

        Iteration stops when we've yielded results for each arguments tuple in
        *iterable*. Unlike :meth:`wait_all` and :meth:`process_all`, this
        function does not wait for any previously-submitted :meth:`execute` or
        :meth:`execute_async` calls.

        Results are temporarily buffered in a queue. If you pass *qsize=*, this
        value is used to limit the max size of the queue: an attempt to buffer
        too many results will suspend the completed :class:`CoroutinePool`
        coroutine until the requesting coroutine (the caller of
        :meth:`generate_results`) has retrieved one or more results by calling
        this generator-iterator's ``next()``.

        If any coroutine raises an uncaught exception, that exception will
        propagate to the requesting coroutine via the corresponding ``next()``
        call.

        What I particularly want these tests to illustrate is that using this
        generator function::

            for result in generate_results(function, iterable):
                # ... do something with result ...
                pass

        executes coroutines at least as aggressively as the classic eventlet
        idiom::

            events = [pool.execute(function, *args) for args in iterable]
            for event in events:
                result = event.wait()
                # ... do something with result ...

        even without a distinct event object for every arg tuple in *iterable*,
        and despite the funny flow control from interleaving launches of new
        coroutines with yields of completed coroutines' results.

        (The use case that makes this function preferable to the classic idiom
        above is when the *iterable*, which may itself be a generator, produces
        millions of items.)

        >>> from eventlet import coros
        >>> import string
        >>> pool = coros.CoroutinePool(max_size=5)
        >>> pausers = [coros.Event() for x in xrange(2)]
        >>> def longtask(evt, desc):
        ...     print "%s woke up with %s" % (desc, evt.wait())
        ...
        >>> pool.launch_all(longtask, zip(pausers, "AB"))
        >>> def quicktask(desc):
        ...     print "returning %s" % desc
        ...     return desc
        ...

        (Instead of using a ``for`` loop, step through :meth:`generate_results`
        items individually to illustrate timing)

        >>> step = iter(pool.generate_results(quicktask, string.ascii_lowercase))
        >>> print step.next()
        returning a
        returning b
        returning c
        a
        >>> print step.next()
        b
        >>> print step.next()
        c
        >>> print step.next()
        returning d
        returning e
        returning f
        d
        >>> pausers[0].send("A")
        >>> print step.next()
        e
        >>> print step.next()
        f
        >>> print step.next()
        A woke up with A
        returning g
        returning h
        returning i
        g
        >>> print "".join([step.next() for x in xrange(3)])
        returning j
        returning k
        returning l
        returning m
        hij
        >>> pausers[1].send("B")
        >>> print "".join([step.next() for x in xrange(4)])
        B woke up with B
        returning n
        returning o
        returning p
        returning q
        klmn
        """
        # Get an iterator because of our funny nested loop below. Wrap the
        # iterable in enumerate() so we count items that come through.
        tuples = iter(enumerate(iterable))
        # If the iterable is empty, this whole function is a no-op, and we can
        # save ourselves some grief by just quitting out. In particular, once
        # we enter the outer loop below, we're going to wait on the queue --
        # but if we launched no coroutines with that queue as the destination,
        # we could end up waiting a very long time.
        try:
            index, args = tuples.next()
        except StopIteration:
            return
        # From this point forward, 'args' is the current arguments tuple and
        # 'index+1' counts how many such tuples we've seen.
        # This implementation relies on the fact that _execute() accepts an
        # event-like object, and -- unless it's None -- the completed
        # coroutine calls send(result). We slyly pass a queue rather than an
        # event -- the same queue instance for all coroutines. This is why our
        # queue interface intentionally resembles the event interface.
        q = coros.queue(max_size=qsize)
        # How many results have we yielded so far?
        finished = 0
        # This first loop is only until we've launched all the coroutines. Its
        # complexity is because if iterable contains more args tuples than the
        # size of our pool, attempting to _execute() the (poolsize+1)th
        # coroutine would suspend until something completes and send()s its
        # result to our queue. But to keep down queue overhead and to maximize
        # responsiveness to our caller, we'd rather suspend on reading the
        # queue. So we stuff the pool as full as we can, then wait for
        # something to finish, then stuff more coroutines into the pool.
        try:
            while True:
                # Before each yield, start as many new coroutines as we can fit.
                # (The self.free() test isn't 100% accurate: if we happen to be
                # executing in one of the pool's coroutines, we could _execute()
                # without waiting even if self.free() reports 0. See _execute().)
                # The point is that we don't want to wait in the _execute() call,
                # we want to wait in the q.wait() call.
                # IMPORTANT: at start, and whenever we've caught up with all
                # coroutines we've launched so far, we MUST iterate this inner
                # loop at least once, regardless of self.free() -- otherwise the
                # q.wait() call below will deadlock!
                # Recall that index is the index of the NEXT args tuple that we
                # haven't yet launched. Therefore it counts how many args tuples
                # we've launched so far.
                while self.free() > 0 or finished == index:
                    # Just like the implementation of execute_async(), save that
                    # we're passing our queue instead of None as the "event" to
                    # which to send() the result.
                    self._execute(q, function, args, {})
                    # We've consumed that args tuple, advance to next.
                    index, args = tuples.next()
                # Okay, we've filled up the pool again, yield a result -- which
                # will probably wait for a coroutine to complete. Although we do
                # have q.ready(), so we could iterate without waiting, we avoid
                # that because every yield could involve considerable real time.
                # We don't know how long it takes to return from yield, so every
                # time we do, take the opportunity to stuff more requests into the
                # pool before yielding again.
                yield q.wait()
                # Be sure to count results so we know when to stop!
                finished += 1
        except StopIteration:
            pass
        # Here we've exhausted the input iterable. index+1 is the total number
        # of coroutines we've launched. We probably haven't yielded that many
        # results yet. Wait for the rest of the results, yielding them as they
        # arrive.
        while finished < index + 1:
            yield q.wait()
            finished += 1


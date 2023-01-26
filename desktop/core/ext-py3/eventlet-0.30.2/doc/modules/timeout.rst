:mod:`timeout` -- Universal Timeouts
========================================

.. class:: eventlet.timeout.Timeout

    Raises *exception* in the current greenthread after *timeout* seconds::

        timeout = Timeout(seconds, exception)
        try:
            ... # execution here is limited by timeout
        finally:
            timeout.cancel()

    When *exception* is omitted or is ``None``, the :class:`Timeout` instance
    itself is raised:

        >>> Timeout(0.1)
        >>> eventlet.sleep(0.2)
        Traceback (most recent call last):
         ...
        Timeout: 0.1 seconds

    You can use the  ``with`` statement for additional convenience::

        with Timeout(seconds, exception) as timeout:
            pass # ... code block ...

    This is equivalent to the try/finally block in the first example.

    There is an additional feature when using the ``with`` statement: if
    *exception* is ``False``, the timeout is still raised, but the with
    statement suppresses it, so the code outside the with-block won't see it::

        data = None
        with Timeout(5, False):
            data = mysock.makefile().readline()
        if data is None:
            ... # 5 seconds passed without reading a line
        else:
            ... # a line was read within 5 seconds

    As a very special case, if *seconds* is None, the timer is not scheduled,
    and is only useful if you're planning to raise it directly.

    There are two Timeout caveats to be aware of:

    * If the code block in the try/finally or with-block never cooperatively yields, the timeout cannot be raised.  In Eventlet, this should rarely be a problem, but be aware that you cannot time out CPU-only operations with this class.
    * If the code block catches and doesn't re-raise :class:`BaseException`  (for example, with ``except:``), then it will catch the Timeout exception, and might not abort as intended.

    When catching timeouts, keep in mind that the one you catch may not be the
    one you set; if you plan on silencing a timeout, always check that it's the
    same instance that you set::

        timeout = Timeout(1)
        try:
            ...
        except Timeout as t:
            if t is not timeout:
                raise # not my timeout

    .. automethod:: cancel
    .. autoattribute:: pending


.. function:: eventlet.timeout.with_timeout(seconds, function, *args, **kwds)

    Wrap a call to some (yielding) function with a timeout; if the called
    function fails to return before the timeout, cancel it and return a flag
    value.

    :param seconds: seconds before timeout occurs
    :type seconds: int or float
    :param func: the callable to execute with a timeout; it must cooperatively yield, or else the timeout will not be able to trigger
    :param \*args: positional arguments to pass to *func*
    :param \*\*kwds: keyword arguments to pass to *func*
    :param timeout_value: value to return if timeout occurs (by default raises
      :class:`Timeout`)

    :rtype: Value returned by *func* if *func* returns before *seconds*, else
      *timeout_value* if provided, else raises :class:`Timeout`.

    :exception Timeout: if *func* times out and no ``timeout_value`` has
      been provided.
    :exception: Any exception raised by *func*

    Example::

        data = with_timeout(30, urllib2.open, 'http://www.google.com/', timeout_value="")

    Here *data* is either the result of the ``get()`` call, or the empty string
    if it took too long to return.  Any exception raised by the ``get()`` call
    is passed through to the caller.

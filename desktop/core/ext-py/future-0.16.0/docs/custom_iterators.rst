.. _custom-iterators:

Custom iterators
----------------

If you define your own iterators, there is an incompatibility in the method name
to retrieve the next item across Py3 and Py2. On Python 3 it is ``__next__``,
whereas on Python 2 it is ``next``.

The most elegant solution to this is to derive your custom iterator class from
``builtins.object`` and define a ``__next__`` method as you normally
would on Python 3. On Python 2, ``object`` then refers to the
``future.types.newobject`` base class, which provides a fallback ``next``
method that calls your ``__next__``. Use it as follows::

    from builtins import object
    
    class Upper(object):
        def __init__(self, iterable):
            self._iter = iter(iterable)
        def __next__(self):                 # Py3-style iterator interface
            return next(self._iter).upper()
        def __iter__(self):
            return self

    itr = Upper('hello')
    assert next(itr) == 'H'
    assert next(itr) == 'E'
    assert list(itr) == list('LLO')


You can use this approach unless you are defining a custom iterator as a
subclass of a base class defined elsewhere that does not derive from
``newobject``.  In that case, you can provide compatibility across
Python 2 and Python 3 using the ``next`` function from ``future.builtins``::

    from builtins import next

    from some_module import some_base_class

    class Upper2(some_base_class):
        def __init__(self, iterable):
            self._iter = iter(iterable)
        def __next__(self):                 # Py3-style iterator interface
            return next(self._iter).upper()
        def __iter__(self):
            return self

    itr2 = Upper2('hello')
    assert next(itr2) == 'H'
    assert next(itr2) == 'E'

``next()`` also works with regular Python 2 iterators with a ``.next`` method::

    itr3 = iter(['one', 'three', 'five'])
    assert 'next' in dir(itr3)
    assert next(itr3) == 'one'

This approach is feasible whenever your code calls the ``next()`` function
explicitly. If you consume the iterator implicitly in a ``for`` loop or
``list()`` call or by some other means, the ``future.builtins.next`` function
will not help; the third assertion below would fail on Python 2::

    itr2 = Upper2('hello')

    assert next(itr2) == 'H'
    assert next(itr2) == 'E'
    assert list(itr2) == list('LLO')      # fails because Py2 implicitly looks
                                          # for a ``next`` method.

Instead, you can use a decorator called ``implements_iterator`` from
``future.utils`` to allow Py3-style iterators to work identically on Py2, even
if they don't inherit from ``future.builtins.object``. Use it as follows::

    from future.utils import implements_iterator

    Upper2 = implements_iterator(Upper2)

    print(list(Upper2('hello')))
    # prints ['H', 'E', 'L', 'L', 'O']

This can of course also be used with the ``@`` decorator syntax when defining
the iterator as follows::

    @implements_iterator
    class Upper2(some_base_class):
        def __init__(self, iterable):
            self._iter = iter(iterable)
        def __next__(self):                 # note the Py3 interface
            return next(self._iter).upper()
        def __iter__(self):
            return self

On Python 3, as usual, this decorator does nothing.


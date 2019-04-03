The ``futurize`` script passes Python 2 code through all the appropriate fixers
to turn it into valid Python 3 code, and then adds ``__future__`` and
``future`` package imports to re-enable compatibility with Python 2.

For example, running ``futurize`` turns this Python 2 code:

.. code-block:: python

    import ConfigParser                 # Py2 module name

    class Upper(object):
        def __init__(self, iterable):
            self._iter = iter(iterable)
        def next(self):                 # Py2-style iterator interface
            return next(self._iter).upper()
        def __iter__(self):
            return self

    itr = Upper('hello')
    print next(itr),
    for letter in itr:
        print letter,                   # Py2-style print statement

into this code which runs on both Py2 and Py3:

.. code-block:: python

    from __future__ import print_function
    from future import standard_library
    standard_library.install_aliases()
    from future.builtins import next
    from future.builtins import object
    import configparser                 # Py3-style import

    class Upper(object):
        def __init__(self, iterable):
            self._iter = iter(iterable)
        def __next__(self):             # Py3-style iterator interface
            return next(self._iter).upper()
        def __iter__(self):
            return self

    itr = Upper('hello')
    print(next(itr), end=' ')           # Py3-style print function
    for letter in itr:
        print(letter, end=' ')


To write out all the changes to your Python files that ``futurize`` suggests,
use the ``-w`` flag.

For complex projects, it is probably best to divide the porting into two stages.
Stage 1 is for "safe" changes that modernize the code but do not break Python
2.7 compatibility or introduce a depdendency on the ``future`` package. Stage 2
is to complete the process.

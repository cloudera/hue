.. _utilities-guide:

Utilities
---------

:mod:`future` also provides some useful functions and decorators to ease
backward compatibility with Py2 in the :mod:`future.utils` and
:mod:`past.utils` modules. These are a selection of the most useful functions
from ``six`` and various home-grown Py2/3 compatibility modules from popular
Python projects, such as Jinja2, Pandas, IPython, and Django. The goal is to
consolidate these in one place, tested and documented, obviating the need for
every project to repeat this work.

Examples::

    # Functions like print() expect __str__ on Py2 to return a byte
    # string. This decorator maps the __str__ to __unicode__ on Py2 and
    # defines __str__ to encode it as utf-8:

    from future.utils import python_2_unicode_compatible

    @python_2_unicode_compatible
    class MyClass(object):
        def __str__(self):
            return u'Unicode string: \u5b54\u5b50'
    a = MyClass()

    # This then prints the Chinese characters for Confucius:
    print(a)


    # Iterators on Py3 require a __next__() method, whereas on Py2 this
    # is called next(). This decorator allows Py3-style iterators to work
    # identically on Py2:

    @implements_iterator
    class Upper(object):
        def __init__(self, iterable):
            self._iter = iter(iterable)
        def __next__(self):                 # note the Py3 interface
            return next(self._iter).upper()
        def __iter__(self):
            return self

    print(list(Upper('hello')))
    # prints ['H', 'E', 'L', 'L', 'O']

On Python 3 these decorators are no-ops.

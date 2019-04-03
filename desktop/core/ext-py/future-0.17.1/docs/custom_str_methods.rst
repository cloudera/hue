.. _custom-str-methods:

Custom __str__ methods
----------------------

If you define a custom ``__str__`` method for any of your classes,
functions like ``print()`` expect ``__str__`` on Py2 to return a byte
string, whereas on Py3 they expect a (unicode) string.

Use the following decorator to map the ``__str__`` to ``__unicode__`` on
Py2 and define ``__str__`` to encode it as utf-8::

    from future.utils import python_2_unicode_compatible

    @python_2_unicode_compatible
    class MyClass(object):
        def __str__(self):
            return u'Unicode string: \u5b54\u5b50'
    a = MyClass()

    # This then prints the name of a Chinese philosopher:
    print(a)

This decorator is identical to the decorator of the same name in
:mod:`django.utils.encoding`.

This decorator is a no-op on Python 3.

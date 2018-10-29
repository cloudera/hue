===================================
Verifying interface implementations
===================================

The ``zope.interface.verify`` module provides functions that test whether a
given interface is implemented by a class or provided by an object, resp.


Verifying classes
=================

This is covered by unit tests defined in ``zope.interface.tests.test_verify``.


Verifying objects
=================

An object provides an interface if

- either its class declares that it implements the interfaces, or the object
  declares that it directly provides the interface;

- the object defines all the methods required by the interface;

- all the methods have the correct signature;

- the object defines all non-method attributes required by the interface.

This doctest currently covers only the latter item.

Testing for attributes
----------------------

Attributes of the object, be they defined by its class or added by its
``__init__`` method, will be recognized:

.. doctest::

   >>> from zope.interface import Interface, Attribute, implements
   >>> from zope.interface.exceptions import BrokenImplementation
   >>> class IFoo(Interface):
   ...     x = Attribute("The X attribute")
   ...     y = Attribute("The Y attribute")

   >>> class Foo(object):
   ...     implements(IFoo)
   ...     x = 1
   ...     def __init__(self):
   ...         self.y = 2

   >>> from zope.interface.verify import verifyObject
   >>> verifyObject(IFoo, Foo())
   True

If either attribute is missing, verification will fail:

.. doctest::

   >>> class Foo(object):
   ...     implements(IFoo)
   ...     x = 1
   >>> try: #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
   ...     verifyObject(IFoo, Foo())
   ... except BrokenImplementation, e:
   ...     print str(e)
   An object has failed to implement interface <InterfaceClass ...IFoo>
   <BLANKLINE>
           The y attribute was not provided.
   <BLANKLINE>
   >>> class Foo(object):
   ...     implements(IFoo)
   ...     def __init__(self):
   ...         self.y = 2
   >>> try: #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
   ...     verifyObject(IFoo, Foo())
   ... except BrokenImplementation, e:
   ...     print str(e)
   An object has failed to implement interface <InterfaceClass ...IFoo>
   <BLANKLINE>
           The x attribute was not provided.
   <BLANKLINE>

If an attribute is implemented as a property that raises an ``AttributeError``
when trying to get its value, the attribute is considered missing:

.. doctest::

   >>> class IFoo(Interface):
   ...     x = Attribute('The X attribute')
   >>> class Foo(object):
   ...     implements(IFoo)
   ...     @property
   ...     def x(self):
   ...         raise AttributeError
   >>> try: #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
   ...     verifyObject(IFoo, Foo())
   ... except BrokenImplementation, e:
   ...     print str(e)
   An object has failed to implement interface <InterfaceClass ...IFoo>
   <BLANKLINE>
           The x attribute was not provided.
   <BLANKLINE>

Any other exception raised by a property will propagate to the caller of
``verifyObject``:

.. doctest::

   >>> class Foo(object):
   ...     implements(IFoo)
   ...     @property
   ...     def x(self):
   ...         raise Exception
   >>> verifyObject(IFoo, Foo())
   Traceback (most recent call last):
   Exception

Of course, broken properties that are not required by the interface don't do
any harm:

.. doctest::

   >>> class Foo(object):
   ...     implements(IFoo)
   ...     x = 1
   ...     @property
   ...     def y(self):
   ...         raise Exception
   >>> verifyObject(IFoo, Foo())
   True

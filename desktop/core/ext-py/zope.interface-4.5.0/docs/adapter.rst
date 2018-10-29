.. _adapter-registry:

==================
 Adapter Registry
==================

Adapter registries provide a way to register objects that depend on
one or more interface specifications and provide (perhaps indirectly)
some interface.  In addition, the registrations have names. (You can
think of the names as qualifiers of the provided interfaces.)

The term "interface specification" refers both to interfaces and to
interface declarations, such as declarations of interfaces implemented
by a class.


Single Adapters
===============

Let's look at a simple example, using a single required specification:

.. doctest::

  >>> from zope.interface.adapter import AdapterRegistry
  >>> import zope.interface

  >>> class IRequire1(zope.interface.Interface):
  ...     pass
  >>> class IProvide1(zope.interface.Interface):
  ...     pass
  >>> class IProvide2(IProvide1):
  ...     pass

  >>> registry = AdapterRegistry()

We'll register an object that depends on ``IRequire1`` and "provides" ``IProvide2``:

.. doctest::

  >>> registry.register([IRequire1], IProvide2, '', 12)

Given the registration, we can look it up again:

.. doctest::

  >>> registry.lookup([IRequire1], IProvide2, '')
  12

Note that we used an integer in the example.  In real applications,
one would use some objects that actually depend on or provide
interfaces. The registry doesn't care about what gets registered, so
we'll use integers and strings to keep the examples simple. There is
one exception.  Registering a value of ``None`` unregisters any
previously-registered value.

If an object depends on a specification, it can be looked up with a
specification that extends the specification that it depends on:

.. doctest::

  >>> class IRequire2(IRequire1):
  ...     pass
  >>> registry.lookup([IRequire2], IProvide2, '')
  12

We can use a class implementation specification to look up the object:

.. doctest::

  >>> class C2:
  ...     zope.interface.implements(IRequire2)

  >>> registry.lookup([zope.interface.implementedBy(C2)], IProvide2, '')
  12


and it can be looked up for interfaces that its provided interface
extends:

.. doctest::

  >>> registry.lookup([IRequire1], IProvide1, '')
  12
  >>> registry.lookup([IRequire2], IProvide1, '')
  12

But if you require a specification that doesn't extend the specification the
object depends on, you won't get anything:

.. doctest::

  >>> registry.lookup([zope.interface.Interface], IProvide1, '')

By the way, you can pass a default value to lookup:

.. doctest::

  >>> registry.lookup([zope.interface.Interface], IProvide1, '', 42)
  42

If you try to get an interface the object doesn't provide, you also
won't get anything:

.. doctest::

  >>> class IProvide3(IProvide2):
  ...     pass
  >>> registry.lookup([IRequire1], IProvide3, '')

You also won't get anything if you use the wrong name:

.. doctest::

  >>> registry.lookup([IRequire1], IProvide1, 'bob')
  >>> registry.register([IRequire1], IProvide2, 'bob', "Bob's 12")
  >>> registry.lookup([IRequire1], IProvide1, 'bob')
  "Bob's 12"

You can leave the name off when doing a lookup:

.. doctest::

  >>> registry.lookup([IRequire1], IProvide1)
  12

If we register an object that provides ``IProvide1``:

.. doctest::

  >>> registry.register([IRequire1], IProvide1, '', 11)

then that object will be prefered over ``O(12)``:

.. doctest::

  >>> registry.lookup([IRequire1], IProvide1, '')
  11

Also, if we register an object for ``IRequire2``, then that will be preferred
when using ``IRequire2``:

.. doctest::

  >>> registry.register([IRequire2], IProvide1, '', 21)
  >>> registry.lookup([IRequire2], IProvide1, '')
  21

Finding out what, if anything, is registered
--------------------------------------------

We can ask if there is an adapter registered for a collection of
interfaces. This is different than lookup, because it looks for an
exact match:

.. doctest::

  >>> print registry.registered([IRequire1], IProvide1)
  11

  >>> print registry.registered([IRequire1], IProvide2)
  12

  >>> print registry.registered([IRequire1], IProvide2, 'bob')
  Bob's 12


  >>> print registry.registered([IRequire2], IProvide1)
  21

  >>> print registry.registered([IRequire2], IProvide2)
  None

In the last example, ``None`` was returned because nothing was registered
exactly for the given interfaces.

lookup1
-------

Lookup of single adapters is common enough that there is a specialized
version of lookup that takes a single required interface:

.. doctest::

  >>> registry.lookup1(IRequire2, IProvide1, '')
  21
  >>> registry.lookup1(IRequire2, IProvide1)
  21

Actual Adaptation
-----------------

The adapter registry is intended to support adaptation, where one
object that implements an interface is adapted to another object that
supports a different interface.  The adapter registry supports the
computation of adapters. In this case, we have to register adapter
factories:

.. doctest::

   >>> class IR(zope.interface.Interface):
   ...     pass

   >>> class X:
   ...     zope.interface.implements(IR)

   >>> class Y:
   ...     zope.interface.implements(IProvide1)
   ...     def __init__(self, context):
   ...         self.context = context

  >>> registry.register([IR], IProvide1, '', Y)

In this case, we registered a class as the factory. Now we can call
``queryAdapter`` to get the adapted object:

.. doctest::

  >>> x = X()
  >>> y = registry.queryAdapter(x, IProvide1)
  >>> y.__class__.__name__
  'Y'
  >>> y.context is x
  True

We can register and lookup by name too:

.. doctest::

  >>> class Y2(Y):
  ...     pass

  >>> registry.register([IR], IProvide1, 'bob', Y2)
  >>> y = registry.queryAdapter(x, IProvide1, 'bob')
  >>> y.__class__.__name__
  'Y2'
  >>> y.context is x
  True

When the adapter factory produces ``None``, then this is treated as if no
adapter has been found. This allows us to prevent adaptation (when desired)
and let the adapter factory determine whether adaptation is possible based on
the state of the object being adapted:

.. doctest::

  >>> def factory(context):
  ...     if context.name == 'object':
  ...         return 'adapter'
  ...     return None

  >>> class Object(object):
  ...     zope.interface.implements(IR)
  ...     name = 'object'

  >>> registry.register([IR], IProvide1, 'conditional', factory)
  >>> obj = Object()
  >>> registry.queryAdapter(obj, IProvide1, 'conditional')
  'adapter'
  >>> obj.name = 'no object'
  >>> registry.queryAdapter(obj, IProvide1, 'conditional') is None
  True
  >>> registry.queryAdapter(obj, IProvide1, 'conditional', 'default')
  'default'

An alternate method that provides the same function as ``queryAdapter()`` is
`adapter_hook()`:

.. doctest::

  >>> y = registry.adapter_hook(IProvide1, x)
  >>> y.__class__.__name__
  'Y'
  >>> y.context is x
  True
  >>> y = registry.adapter_hook(IProvide1, x, 'bob')
  >>> y.__class__.__name__
  'Y2'
  >>> y.context is x
  True

The ``adapter_hook()`` simply switches the order of the object and
interface arguments.  It is used to hook into the interface call
mechanism.


Default Adapters
----------------

Sometimes, you want to provide an adapter that will adapt anything.
For that, provide ``None`` as the required interface:

.. doctest::

  >>> registry.register([None], IProvide1, '', 1)

then we can use that adapter for interfaces we don't have specific
adapters for:

.. doctest::

  >>> class IQ(zope.interface.Interface):
  ...     pass
  >>> registry.lookup([IQ], IProvide1, '')
  1

Of course, specific adapters are still used when applicable:

.. doctest::

  >>> registry.lookup([IRequire2], IProvide1, '')
  21


Class adapters
--------------

You can register adapters for class declarations, which is almost the
same as registering them for a class:

.. doctest::

  >>> registry.register([zope.interface.implementedBy(C2)], IProvide1, '', 'C21')
  >>> registry.lookup([zope.interface.implementedBy(C2)], IProvide1, '')
  'C21'

Dict adapters
-------------

At some point it was impossible to register dictionary-based adapters due a
bug. Let's make sure this works now:

.. doctest::

  >>> adapter = {}
  >>> registry.register((), IQ, '', adapter)
  >>> registry.lookup((), IQ, '') is adapter
  True

Unregistering
-------------

You can unregister by registering ``None``, rather than an object:

.. doctest::

  >>> registry.register([zope.interface.implementedBy(C2)], IProvide1, '', None)
  >>> registry.lookup([zope.interface.implementedBy(C2)], IProvide1, '')
  21

Of course, this means that ``None`` can't be registered. This is an
exception to the statement, made earlier, that the registry doesn't
care what gets registered.

Multi-adapters
==============

You can adapt multiple specifications:

.. doctest::

  >>> registry.register([IRequire1, IQ], IProvide2, '', '1q2')
  >>> registry.lookup([IRequire1, IQ], IProvide2, '')
  '1q2'
  >>> registry.lookup([IRequire2, IQ], IProvide1, '')
  '1q2'

  >>> class IS(zope.interface.Interface):
  ...     pass
  >>> registry.lookup([IRequire2, IS], IProvide1, '')

  >>> class IQ2(IQ):
  ...     pass

  >>> registry.lookup([IRequire2, IQ2], IProvide1, '')
  '1q2'

  >>> registry.register([IRequire1, IQ2], IProvide2, '', '1q22')
  >>> registry.lookup([IRequire2, IQ2], IProvide1, '')
  '1q22'

Multi-adaptation
----------------

You can adapt multiple objects:

.. doctest::

  >>> class Q:
  ...     zope.interface.implements(IQ)

As with single adapters, we register a factory, which is often a class:

.. doctest::

  >>> class IM(zope.interface.Interface):
  ...     pass
  >>> class M:
  ...     zope.interface.implements(IM)
  ...     def __init__(self, x, q):
  ...         self.x, self.q = x, q
  >>> registry.register([IR, IQ], IM, '', M)

And then we can call ``queryMultiAdapter`` to compute an adapter:

.. doctest::

  >>> q = Q()
  >>> m = registry.queryMultiAdapter((x, q), IM)
  >>> m.__class__.__name__
  'M'
  >>> m.x is x and m.q is q
  True

and, of course, we can use names:

.. doctest::

  >>> class M2(M):
  ...     pass
  >>> registry.register([IR, IQ], IM, 'bob', M2)
  >>> m = registry.queryMultiAdapter((x, q), IM, 'bob')
  >>> m.__class__.__name__
  'M2'
  >>> m.x is x and m.q is q
  True

Default Adapters
----------------

As with single adapters, you can define default adapters by specifying
``None`` for the *first* specification:

.. doctest::

  >>> registry.register([None, IQ], IProvide2, '', 'q2')
  >>> registry.lookup([IS, IQ], IProvide2, '')
  'q2'

Null Adapters
=============

You can also adapt **no** specification:

.. doctest::

  >>> registry.register([], IProvide2, '', 2)
  >>> registry.lookup([], IProvide2, '')
  2
  >>> registry.lookup([], IProvide1, '')
  2

Listing named adapters
----------------------

Adapters are named. Sometimes, it's useful to get all of the named
adapters for given interfaces:

.. doctest::

  >>> adapters = list(registry.lookupAll([IRequire1], IProvide1))
  >>> adapters.sort()
  >>> assert adapters == [(u'', 11), (u'bob', "Bob's 12")]

This works for multi-adapters too:

.. doctest::

  >>> registry.register([IRequire1, IQ2], IProvide2, 'bob', '1q2 for bob')
  >>> adapters = list(registry.lookupAll([IRequire2, IQ2], IProvide1))
  >>> adapters.sort()
  >>> assert adapters == [(u'', '1q22'), (u'bob', '1q2 for bob')]

And even null adapters:

.. doctest::

  >>> registry.register([], IProvide2, 'bob', 3)
  >>> adapters = list(registry.lookupAll([], IProvide1))
  >>> adapters.sort()
  >>> assert adapters == [(u'', 2), (u'bob', 3)]

Subscriptions
=============

Normally, we want to look up an object that most closely matches a
specification.  Sometimes, we want to get all of the objects that
match some specification.  We use *subscriptions* for this.  We
subscribe objects against specifications and then later find all of
the subscribed objects:

.. doctest::

  >>> registry.subscribe([IRequire1], IProvide2, 'sub12 1')
  >>> registry.subscriptions([IRequire1], IProvide2)
  ['sub12 1']

Note that, unlike regular adapters, subscriptions are unnamed.

You can have multiple subscribers for the same specification:

.. doctest::

  >>> registry.subscribe([IRequire1], IProvide2, 'sub12 2')
  >>> registry.subscriptions([IRequire1], IProvide2)
  ['sub12 1', 'sub12 2']

If subscribers are registered for the same required interfaces, they
are returned in the order of definition.

You can register subscribers for all specifications using ``None``:

.. doctest::

  >>> registry.subscribe([None], IProvide1, 'sub_1')
  >>> registry.subscriptions([IRequire2], IProvide1)
  ['sub_1', 'sub12 1', 'sub12 2']

Note that the new subscriber is returned first.  Subscribers defined
for less general required interfaces are returned before subscribers
for more general interfaces.

Subscriptions may be combined over multiple compatible specifications:

.. doctest::

  >>> registry.subscriptions([IRequire2], IProvide1)
  ['sub_1', 'sub12 1', 'sub12 2']
  >>> registry.subscribe([IRequire1], IProvide1, 'sub11')
  >>> registry.subscriptions([IRequire2], IProvide1)
  ['sub_1', 'sub12 1', 'sub12 2', 'sub11']
  >>> registry.subscribe([IRequire2], IProvide2, 'sub22')
  >>> registry.subscriptions([IRequire2], IProvide1)
  ['sub_1', 'sub12 1', 'sub12 2', 'sub11', 'sub22']
  >>> registry.subscriptions([IRequire2], IProvide2)
  ['sub12 1', 'sub12 2', 'sub22']

Subscriptions can be on multiple specifications:

.. doctest::

  >>> registry.subscribe([IRequire1, IQ], IProvide2, 'sub1q2')
  >>> registry.subscriptions([IRequire1, IQ], IProvide2)
  ['sub1q2']

As with single subscriptions and non-subscription adapters, you can
specify ``None`` for the first required interface, to specify a default:

.. doctest::

  >>> registry.subscribe([None, IQ], IProvide2, 'sub_q2')
  >>> registry.subscriptions([IS, IQ], IProvide2)
  ['sub_q2']
  >>> registry.subscriptions([IRequire1, IQ], IProvide2)
  ['sub_q2', 'sub1q2']

You can have subscriptions that are independent of any specifications:

.. doctest::

  >>> list(registry.subscriptions([], IProvide1))
  []

  >>> registry.subscribe([], IProvide2, 'sub2')
  >>> registry.subscriptions([], IProvide1)
  ['sub2']
  >>> registry.subscribe([], IProvide1, 'sub1')
  >>> registry.subscriptions([], IProvide1)
  ['sub2', 'sub1']
  >>> registry.subscriptions([], IProvide2)
  ['sub2']

Unregistering subscribers
-------------------------

We can unregister subscribers.  When unregistering a subscriber, we
can unregister a *specific* subscriber:

.. doctest::

  >>> registry.unsubscribe([IRequire1], IProvide1, 'sub11')
  >>> registry.subscriptions([IRequire1], IProvide1)
  ['sub_1', 'sub12 1', 'sub12 2']

If we don't specify a value, then *all* subscribers matching the given
interfaces will be unsubscribed:

.. doctest::

  >>> registry.unsubscribe([IRequire1], IProvide2)
  >>> registry.subscriptions([IRequire1], IProvide1)
  ['sub_1']


Subscription adapters
---------------------

We normally register adapter factories, which then allow us to compute
adapters, but with subscriptions, we get multiple adapters.  Here's an
example of multiple-object subscribers:

.. doctest::

  >>> registry.subscribe([IR, IQ], IM, M)
  >>> registry.subscribe([IR, IQ], IM, M2)

  >>> subscribers = registry.subscribers((x, q), IM)
  >>> len(subscribers)
  2
  >>> class_names = [s.__class__.__name__ for s in subscribers]
  >>> class_names.sort()
  >>> class_names
  ['M', 'M2']
  >>> [(s.x is x and s.q is q) for s in subscribers]
  [True, True]

Adapter factory subscribers can't return ``None`` values:

.. doctest::

  >>> def M3(x, y):
  ...     return None

  >>> registry.subscribe([IR, IQ], IM, M3)
  >>> subscribers = registry.subscribers((x, q), IM)
  >>> len(subscribers)
  2

Handlers
--------

A handler is a subscriber factory that doesn't produce any normal
output.  It returns ``None``.  A handler is unlike adapters in that it does
all of its work when the factory is called.

To register a handler, simply provide ``None`` as the provided interface:

.. doctest::

  >>> def handler(event):
  ...     print 'handler', event

  >>> registry.subscribe([IRequire1], None, handler)
  >>> registry.subscriptions([IRequire1], None) == [handler]
  True


Components
==========

A :class:`zope.interface.registry.Components` object implements the
:class:`zope.interface.interfaces.IComponents` interface. This
interface uses multiple adapter registries to implement multiple
higher-level concerns (utilities, adapters and handlers), while also
providing event notifications and query capabilities.

Frequently Asked Questions
==========================

.. contents:: Summary
   :backlinks: entry
   :local:

How to turn logging on/off?
---------------------------

Logging is turned off by default. In Java, simply call
``GatewayServer.turnLoggingOn()`` or ``GatewayServer.turnLoggingOff()``.
Py4J-java uses the ``java.util.logging`` framework. To get fined-grained
control over the logging behavior, just obtain a Logger instance by calling
``Logger.getLogger("py4j")``. You can also look at the `Java Logging Overview
<http://docs.oracle.com/javase/6/docs/technotes/guides/logging/overview.html>`_
for more information on this framework.

For example, in Java, you can do:

.. code-block:: java

  GatewayServer.turnLoggingOn();
  logger = Logger.getLogger("py4j");
  logger.setLevel(Level.ALL);


In Python, logging can be enabled this way:

::

  logger = logging.getLogger("py4j")
  logger.setLevel(logging.DEBUG)
  logger.addHandler(logging.StreamHandler())

**Hint:** you can enable/disable Java logging from Python too:

::

  gateway.jvm.py4j.GatewayServer.turnLoggingOn()


How to call a constructor?
--------------------------

Use the ``jvm`` member of a gateway followed by the class's fully qualified
name. See :ref:`JVM Views <jvm_views>` to learn how to import packages and
avoid typing the fully qualified name of classes:

::

  >>> gateway = JavaGateway()
  >>> java_list = gateway.jvm.java.util.ArrayList()


How to call a static method?
----------------------------

Use the ``jvm`` member of a gateway followed by the fully qualified name of the
method's class. Do the same for static fields.

::

  >>> gateway = JavaGateway()
  >>> timestamp = gateway.jvm.System.currentTimeMillis() # equivalent to jvm.java.lang.System...


How to access a field?
----------------------

Use the :func:`get_field <py4j.java_gateway.get_field>` function:

::

  >>> field_value = py4j.java_gateway.get_field(object,'public_field')


Or you can also set the :ref:`auto_field <api_gatewayparameters>` parameter to
`True` when you create the gateway:

::

  >>> gateway = JavaGateway(GatewayParameters(auto_field=True))
  >>> object = gateway.entry_point.getObject()
  >>> field_value = object.public_field

How to import a class?
----------------------

As in Java, you can always access any class using its fully qualified name, but
you can also import the fully qualified name to only refer to the simple name
later on:

::

  >>> from py4j.java_gateway import JavaGateway
  >>> from py4j.java_gateway import java_import
  >>> gateway = JavaGateway()
  >>> jList1 = gateway.jvm.java.util.ArrayList()
  >>> java_import(gateway.jvm,'java.util.*')
  >>> jList2 = gateway.jvm.ArrayList()
  >>> jMap = gateway.jvm.HashMap()
  >>> gateway.jvm.java.lang.String("a")
  u'a'
  >>> gateway.jvm.String("a")
  u'a'

Read how to use :ref:`jvm views <jvm_views>` to make sure that an import
statement only affects the current Python module.

How to create an array?
-----------------------

Use the :func:`new_array <py4j.java_gateway.JavaGateway.new_array>` function:

::

   >>> gateway = JavaGateway()
   >>> string_class = gateway.jvm.String
   >>> string_array = gateway.new_array(string_class, 3, 5)
   >>> string_array[2][4] = 'Hello World'
   >>> string_array[2][4]
   u'Hello World'
   >>> string_array[2][3] is None
   True
   >>> string_array[3][1]
   Traceback (most recent call last):
   ...
   IndexError: list index out of range


What ports are used by Py4J?
----------------------------

Py4J by default uses the TCP port 25333 to communicate from Python to Java and
TCP port 25334 to communicate from Java to Python. It also uses TCP port 25332
for a test echo server (only used by unit tests).

These ports can be customized when creating a :class:`JavaGateway
<py4j.java_gateway.JavaGateway>` on the Python side and a GatewayServer on the
Java side.

Is Py4J thread-safe?
--------------------

The Java component of Py4J is thread-safe, but multiple threads could access
the same entry point. Each gateway connection is executed in is own thread
(e.g., each time a Python thread calls a Java method) so if multiple Python
threads/processes/programs are connected to the same gateway, i.e., the same
address and the same port, multiple threads may call the entry point's methods
concurrently.

In the following example, two threads are accessing the same entry point. If
`gateway1` and `gateway2` were created in separate processes, `method1` would
be accessed concurrently.

::

  # ... in Thread One
  gateway1 = JavaGateway() # Thread One is accessing the JVM.
  gateway1.entry_point.method1() # Thread One is calling method1
  # ... in Thread Two
  gateway2 = JavaGateway() # Thread Two is accessing the JVM.
  gateway2.entry_point.method1() # Thread Two is calling method1


The Python component of Py4J is also thread-safe, except the :func:`close
<py4j.java_gateway.GatewayClient.close>` function of a
:class:`CommChannelFactory <py4j.java_gateway.GatewayClient>`, which must
not be accessed concurrently with other methods to ensure that all
communication channels are closed. This is a trade-off to avoid accessing a
lock every time a Java method is called on the Python side. This will only be a
problem if attempting to shut down or close a JavaGateway while calling Java
methods on the Python side.

See :ref:`Py4J Threading Model <adv_threading>` for more details.

How can I use Py4J with Eclipse?
--------------------------------

Because each Eclipse plug-in has its own class loader, a `GatewayServer`
instance started in one plug-in won't have access to the other plug-ins **by
default**. You can work around this limitation by adding this line to the
manifest of the plug-in where the GatewayServer resides:

``Eclipse-BuddyPolicy:global``

You can also use the Py4J Eclipse features that starts a default
`GatewayServer` and that allows Python clients to refer to any classes declared
in any plug-in.

See :ref:`Py4J and Eclipse <eclipse_features>` for more details.

Can I use Py4J with Python 3?
-----------------------------

Yes, thanks to a `generous contributor
<https://github.com/bartdag/py4j/commit/36a145671501ed47bc4002af7cab49b490eb6e0b>`_,
Py4J now works with Python 3.

Are there any security concerns with Py4J?
------------------------------------------

Running a Py4J gateway on a JVM exposes the JVM over the network, which is a
major security concern because a client can use the JVM to run any code (access
files, delete files, write programs and execute them, communicate over the
network, etc.).

By default, Py4J only listens to the IPv4 localhost (127.0.0.1), so if you
trust all users having access to the localhost, the security risks are minimal
because external programs and users do not have access to the localhost by
default on most systems.

If you use Py4J to make a JVM available over the network, you are responsible
for ensuring that (1) only trusted sources can communicate with the JVM and
(2) the privileges of the user running the JVM are properly constrained. This
is usually achieved with a proper firewall configuration, network
segmentation, and security policies configured with selinux or apparmor.

I found a bug, how do I report it?
----------------------------------

Please report bugs on our `issue tracker
<https://github.com/bartdag/py4j/issues>`_.

How can I contribute?
---------------------

There are many ways to contribute to Py4J:

* **Found a bug or have a feature request?** Fill a detailed `issue report
  <https://github.com/bartdag/py4j/issues>`_.

* **Found a typo or have a better way to clarify the documentation?** Write a
  comment at the bottom of documentation the page, send a patch on the `mailing
  list <https://groups.google.com/a/py4j.org/forum/#!forum/py4j/join>`_,
  fill a `bug report <https://github.com/bartdag/py4j/issues>`_ or open a pull
  request. The source of each documentation page is accessible in the sidebar.
  We use `ReStructuredText
  <http://docutils.sourceforge.net/docs/user/rst/quickstart.html>`_

* **Good at writing Python or Java?** Good news, we could use some help. You
  can open a pull request that adds a new feature or that address an `open
  issue <https://github.com/bartdag/py4j/issues>`_. For new features, it is
  always best to discuss it on the `mailing list
  <https://groups.google.com/a/py4j.org/forum/#!forum/py4j/join>`_ first.
  Do not forget to read our :doc:`contribution guidelines </contributing>`.

* **Feeling artistic?** We need a logo. Hop on the `mailing list
  <https://groups.google.com/a/py4j.org/forum/#!forum/py4j/join>`_.

In case of doubt, do not hesitate to contact the founder of the project,
`Barthelemy <mailto:barthelemy@infobart.com>`_.

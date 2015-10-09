:mod:`py4j.java_gateway` --- Py4J Main API
==========================================

.. module:: py4j.java_gateway
  :synopsis: Main Py4J Python module.
.. moduleauthor:: Barthelemy Dagenais <barthelemy@infobart.com>

The :mod:`py4j.java_gateway` module defines most of the classes that are needed
to use Py4J. Py4J users are expected to only use explicitly :class:`JavaGateway
<py4j.java_gateway.JavaGateway>` and optionally, :class:`GatewayParameters
<py4j.java_gateway.GatewayParameters>`, :class:`CallbackServerParameters
<py4j.java_gateway.CallbackServerParameters>`, :func:`java_import
<py4j.java_gateway.java_import>`, :func:`get_field
<py4j.java_gateway.get_field>`, :func:`get_method
<py4j.java_gateway.get_method>`, :func:`launch_gateway
<py4j.java_gateway.launch_gateway>`, and :func:`is_instance_of
<py4j.java_gateway.is_instance_of>`. The other module members are documented to
support the extension of Py4J.

.. _api_javagateway:

JavaGateway
-----------

.. autoclass:: py4j.java_gateway.JavaGateway
   :members:
   :undoc-members:


.. _api_java_gateway_examples:

Examples
^^^^^^^^

Using the ``jvm`` property:
::

  >>> gateway = JavaGateway()
  >>> jvm = gateway.jvm
  >>> l = jvm.java.util.ArrayList()
  >>> l.append(10)
  >>> l.append(1)
  >>> jvm.java.util.Collections.sort(l)
  >>> l
  [1, 10]
  >>> l.append(5)
  >>> l.sort()
  >>> l
  [1, 5, 10]

Using ``auto_field``:

First we declare a class that has a field AND a method called `member`:

.. code-block:: java

  package py4j.examples;
  public class ExampleWithField {
      public int member = 1;
      public String member() {
          return "Hello World";
      }
  }

Then we play with the class using the two possible values of auto_field:

::

  >>> java_gateway = JavaGateway() # auto_field = False
  >>> example = java_gateway.jvm.py4j.examples.ExampleWithField()
  >>> example.member()
  u'Hello World'
  >>> get_field(example,'member')
  1
  >>> java_gateway2 = JavaGateway(GatewayParameters(auto_field=True))
  >>> example2 = java_gateway2.jvm.py4j.examples.ExampleWithField()
  >>> example2.member
  1
  >>> get_method(example2,'member')()
  u'Hello World'


.. _api_gatewayparameters:

GatewayParameters
-----------------

.. autoclass:: py4j.java_gateway.GatewayParameters
   :members:
   :undoc-members:


.. _api_callbackserverparameters:

CallbackServerParameters
------------------------

.. autoclass:: py4j.java_gateway.CallbackServerParameters
   :members:
   :undoc-members:


.. _api_gatewayclient:

GatewayClient
-------------

.. autoclass:: py4j.java_gateway.GatewayClient
   :members:
   :undoc-members:



..
  Examples
  ^^^^^^^^

  ::

    TBD

.. _api_gatewayconnection:

GatewayConnection
-----------------

.. autoclass:: py4j.java_gateway.GatewayConnection
   :members:
   :undoc-members:

..
  Examples
  ^^^^^^^^

  ::

    TBD

.. _api_jvm:

JVMView
-------

.. autoclass:: py4j.java_gateway.JVMView
   :members:
   :undoc-members:

..
  Examples
  ^^^^^^^^

  ::

    TBD

.. _api_javaobject:

JavaObject
----------

Represents a Java object from which you can call methods or access fields.

..
  Examples
  ^^^^^^^^

  ::

    TBD

.. _api_javamember:

JavaMember
-----------

Represents a member (i.e., method) of a :class:`JavaObject`. For now, only
methods are supported. Fields are retrieved directly and are not contained in a
JavaMember.

..
  Examples
  ^^^^^^^^

  ::

    TBD

.. _api_javaclass:

JavaClass
---------

A `JavaClass` represents a Java Class from which static members can be
retrieved. `JavaClass` instances are also needed to initialize an array.

Usually, `JavaClass` are not initialized using their constructor, but they are
created while accessing the `jvm` property of a gateway, e.g.,
`gateway.jvm.java.lang.String`.

..
  Examples
  ^^^^^^^^

  ::

    TBD

.. _api_javapackage:

JavaPackage
-----------

.. autoclass:: py4j.java_gateway.JavaPackage
   :members:
   :undoc-members:

..
  Examples
  ^^^^^^^^

  ::

    TBD

.. _api_pythonproxypool:

PythonProxyPool
---------------

.. autoclass:: py4j.java_gateway.PythonProxyPool
   :members:
   :undoc-members:

..
  Examples
  ^^^^^^^^

  ::

    TBD

.. _api_callbackserver:

CallbackServer
--------------

.. autoclass:: py4j.java_gateway.CallbackServer
   :members:
   :undoc-members:

..
  Examples
  ^^^^^^^^

  ::

    TBD

.. _api_callbackconnection:

CallbackConnection
------------------

.. autoclass:: py4j.java_gateway.CallbackConnection
   :members:
   :undoc-members:

..
  Examples
  ^^^^^^^^

  ::

    TBD

.. _api_functions:

Py4J Functions
--------------

The following functions get be used to import packages or to get a particular field or method when fields and methods in a Java class have the same name:

.. autofunction:: py4j.java_gateway.java_import

.. autofunction:: py4j.java_gateway.launch_gateway

.. autofunction:: py4j.java_gateway.get_field

.. autofunction:: py4j.java_gateway.set_field

.. autofunction:: py4j.java_gateway.get_method

.. autofunction:: py4j.java_gateway.is_instance_of



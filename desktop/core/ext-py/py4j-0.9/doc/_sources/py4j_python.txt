.. _python_api:

Py4J Python API
===============

Using Py4J is usually as simple as creating a :ref:`JavaGateway <api_javagateway>` object:

::
  
  java_gateway = JavaGateway()
  # you are now connected to the JVM 
  # and you can call any method defined on the Java side.

You can still customize and extend Py4J in many ways (e.g., you can choose the port to which you want to connect). The
following modules are documented. Note that users are expected to only use :mod:`py4j.java_gateway`.

.. toctree::

   py4j_java_gateway.rst
   py4j_java_protocol.rst
   py4j_java_collections.rst
   py4j_finalizer.rst



    



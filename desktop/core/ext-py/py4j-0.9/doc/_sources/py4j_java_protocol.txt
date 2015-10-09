:mod:`py4j.protocol` --- Py4J Protocol
==========================================

.. module:: py4j.protocol
  :synopsis: Main Py4J Protocol Python module.
.. moduleauthor:: Barthelemy Dagenais <barthelemy@infobart.com>

The :mod:`py4j.protocol` module defines most of the types, functions, and
characters used in the Py4J protocol. It does not need to be explicitly used by
clients of Py4J because it is automatically loaded by the :mod:`java_gateway
<py4j.java_gateway>` module and the :mod:`java_collections
<py4j.java_collections>` module.

.. _api_py4jerror:

Py4JError
-----------

.. autoclass:: py4j.protocol.Py4JError
   :members:
   :undoc-members:

Py4JJavaError
-------------

.. autoclass:: py4j.protocol.Py4JJavaError
   :members:
   :undoc-members:

Py4JJavaError
-------------

.. autoclass:: py4j.protocol.Py4JNetworkError
   :members:
   :undoc-members:

Py4J Protocol Functions
-----------------------

The following functions can be used to extend Py4J (e.g., to create new commands):

.. autofunction:: py4j.protocol.escape_new_line

.. autofunction:: py4j.protocol.unescape_new_line

.. autofunction:: py4j.protocol.get_command_part

.. autofunction:: py4j.protocol.get_return_value

.. autofunction:: py4j.protocol.register_output_converter

.. autofunction:: py4j.protocol.register_input_converter

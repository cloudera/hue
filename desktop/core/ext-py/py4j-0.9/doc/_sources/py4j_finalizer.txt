:mod:`py4j.finalizer` --- Py4J Finalizer API
=====================================================

.. module:: py4j.finalizer
  :synopsis: Global classes to register finalizers.
.. moduleauthor:: Barthelemy Dagenais <barthelemy@infobart.com>

The :mod:`py4j.finalizer` module contains global classes that enables the registration of finalizers, i.e., weak
reference callbacks. This module is used by Py4J to register a finalizer for each JavaObject instance: once there is no
more reference to a JavaObject instance on the Python side, the finalizer sends a message to the JVM to remove the
reference from the Gateway to prevent memory leak.

The :mod:`py4j.finalizer` module is necessary because JavaObject instances have circular references with JavaMethods and
hence, they cannot keep their own finalizer.

.. _api_tsfinalizer:

ThreadSafeFinalizer
-------------------

.. autoclass:: py4j.finalizer.ThreadSafeFinalizer
   :members:
   :undoc-members:

..
  Examples
  ^^^^^^^^

  ::

    TBD

.. _api_finalizer:

Finalizer
---------

.. autoclass:: py4j.finalizer.Finalizer
   :members:
   :undoc-members:

..
  Examples
  ^^^^^^^^

  ::

    TBD


Py4J Finalizer Functions
------------------------

.. _api_functions_clear_finalizers:


.. autofunction:: py4j.finalizer.clear_finalizers

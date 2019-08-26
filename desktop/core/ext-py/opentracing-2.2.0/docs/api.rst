Python API
==========

Classes
-------
.. autoclass:: opentracing.Span
   :members:

.. autoclass:: opentracing.SpanContext
   :members:

.. autoclass:: opentracing.Scope
   :members:

.. autoclass:: opentracing.ScopeManager
   :members:

.. autoclass:: opentracing.Tracer
   :members:

.. autoclass:: opentracing.ReferenceType
   :members:

.. autoclass:: opentracing.Reference
   :members:

.. autoclass:: opentracing.Format
   :members:

Utility Functions
-----------------
.. autofunction:: opentracing.global_tracer

.. autofunction:: opentracing.set_global_tracer

.. autofunction:: opentracing.start_child_span

.. autofunction:: opentracing.child_of

.. autofunction:: opentracing.follows_from

Exceptions
----------
.. autoclass:: opentracing.InvalidCarrierException
   :members:

.. autoclass:: opentracing.SpanContextCorruptedException
   :members:

.. autoclass:: opentracing.UnsupportedFormatException
   :members:
   
MockTracer
--------------
.. autoclass:: opentracing.mocktracer.MockTracer
   :members:

Scope managers
--------------
.. autoclass:: opentracing.scope_managers.ThreadLocalScopeManager
   :members:

.. autoclass:: opentracing.scope_managers.gevent.GeventScopeManager
   :members:

.. autoclass:: opentracing.scope_managers.tornado.TornadoScopeManager
   :members:

.. autofunction:: opentracing.scope_managers.tornado.tracer_stack_context

.. autoclass:: opentracing.scope_managers.asyncio.AsyncioScopeManager
   :members:

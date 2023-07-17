:mod:`eventlet.green.zmq` -- ØMQ support
========================================

:mod:`pyzmq <zmq>` [1]_ is a python binding to the C++ ØMQ [2]_ library written in Cython [3]_.
:mod:`eventlet.green.zmq` is greenthread aware version of `pyzmq`.

.. automodule:: eventlet.green.zmq
    :show-inheritance:

.. currentmodule:: eventlet.green.zmq

.. autoclass:: Context
    :show-inheritance:

    .. automethod:: socket

.. autoclass:: Socket
    :show-inheritance:
    :inherited-members:

    .. automethod:: recv

    .. automethod:: send

.. module:: zmq


.. [1] http://github.com/zeromq/pyzmq
.. [2] http://www.zeromq.com
.. [3] http://www.cython.org

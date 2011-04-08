"""The :mod:`zmq` module wraps the :class:`Socket` and :class:`Context` found in :mod:`pyzmq <zmq>` to be non blocking
"""
__zmq__ = __import__('zmq')
from eventlet import sleep
from eventlet.hubs import trampoline, get_hub

__patched__ = ['Context', 'Socket']
globals().update(dict([(var, getattr(__zmq__, var))
                       for var in __zmq__.__all__
                       if not (var.startswith('__')
                            or
                              var in __patched__)
                       ]))


def get_hub_name_from_instance(hub):
    """Get the string name the eventlet uses to refer to hub

    :param hub: An eventlet hub
    """
    return hub.__class__.__module__.rsplit('.',1)[-1]

def Context(io_threads=1):
    """Factory function replacement for :class:`zmq.core.context.Context`

    This factory ensures the :class:`zeromq hub <eventlet.hubs.zeromq.Hub>`
    is the active hub, and defers creation (or retreival) of the ``Context``
    to the hub's :meth:`~eventlet.hubs.zeromq.Hub.get_context` method
    
    It's a factory function due to the fact that there can only be one :class:`_Context`
    instance per thread. This is due to the way :class:`zmq.core.poll.Poller`
    works
    """
    hub = get_hub()
    hub_name = get_hub_name_from_instance(hub)
    if hub_name != 'zeromq':
        raise RuntimeError("Hub must be 'zeromq', got '%s'" % hub_name)
    return hub.get_context(io_threads)

class _Context(__zmq__.Context):
    """Internal subclass of :class:`zmq.core.context.Context`

    .. warning:: Do not grab one of these yourself, use the factory function
        :func:`eventlet.green.zmq.Context`
    """

    def socket(self, socket_type):
        """Overridden method to ensure that the green version of socket is used

        Behaves the same as :meth:`zmq.core.context.Context.socket`, but ensures
        that a :class:`Socket` with all of its send and recv methods set to be
        non-blocking is returned
        """
        return Socket(self, socket_type)

class Socket(__zmq__.Socket):
    """Green version of :class:`zmq.core.socket.Socket

    The following four methods are overridden:

        * _send_message
        * _send_copy
        * _recv_message
        * _recv_copy

    To ensure that the ``zmq.NOBLOCK`` flag is set and that sending or recieving
    is deferred to the hub (using :func:`eventlet.hubs.trampoline`) if a
    ``zmq.EAGAIN`` (retry) error is raised
    """


    def _send_message(self, msg, flags=0):
        flags |= __zmq__.NOBLOCK
        while True:
            try:
                super(Socket, self)._send_message(msg, flags)
                return
            except __zmq__.ZMQError, e:
                if e.errno != EAGAIN:
                    raise
            trampoline(self, write=True)

    def _send_copy(self, msg, flags=0):
        flags |= __zmq__.NOBLOCK
        while True:
            try:
                super(Socket, self)._send_copy(msg, flags)
                return
            except __zmq__.ZMQError, e:
                if e.errno != EAGAIN:
                    raise
            trampoline(self, write=True)

    def _recv_message(self, flags=0, track=False):

        flags |= __zmq__.NOBLOCK
        while True:
            try:
                m = super(Socket, self)._recv_message(flags, track)
                if m is not None:
                    return m
            except __zmq__.ZMQError, e:
                if e.errno != EAGAIN:
                    raise
            trampoline(self, read=True)

    def _recv_copy(self, flags=0):
        flags |= __zmq__.NOBLOCK
        while True:
            try:
                m = super(Socket, self)._recv_copy(flags)
                if m is not None:
                    return m
            except __zmq__.ZMQError, e:
                if e.errno != EAGAIN:
                    raise
            trampoline(self, read=True)




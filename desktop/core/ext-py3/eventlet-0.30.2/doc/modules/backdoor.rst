:mod:`backdoor` -- Python interactive interpreter within a running process
===============================================================================

The backdoor module is convenient for inspecting the state of a long-running process.  It supplies the normal Python interactive interpreter in a way that does not block the normal operation of the application.  This can be useful for debugging, performance tuning, or simply learning about how things behave in situ.

In the application, spawn a greenthread running backdoor_server on a listening socket::

    eventlet.spawn(backdoor.backdoor_server, eventlet.listen(('localhost', 3000)), locals())

When this is running, the backdoor is accessible via telnet to the specified port.

.. code-block:: sh

  $ telnet localhost 3000
  (python version, build info)
  Type "help", "copyright", "credits" or "license" for more information.
  >>> import myapp
  >>> dir(myapp)
  ['__all__', '__doc__', '__name__', 'myfunc']
  >>>

The backdoor cooperatively yields to the rest of the application between commands, so on a running server continuously serving requests, you can observe the internal state changing between interpreter commands.

.. automodule:: eventlet.backdoor
	:members:

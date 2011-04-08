Eventlet is a concurrent networking library for Python that allows you to change how you run your code, not how you write it.

It uses epoll or libevent for highly scalable non-blocking I/O.  Coroutines ensure that the developer uses a blocking style of programming that is similar to threading, but provide the benefits of non-blocking I/O.  The event dispatch is implicit, which means you can easily use Eventlet from the Python interpreter, or as a small part of a larger application.

It's easy to get started using Eventlet, and easy to convert existing 
applications to use it.  Start off by looking at the `examples`_, 
`common design patterns`_, and the list of `basic API primitives`_.

.. _examples: http://eventlet.net/doc/examples.html
.. _common design patterns: http://eventlet.net/doc/design_patterns.html
.. _basic API primitives: http://eventlet.net/doc/basic_usage.html

Quick Example
===============

Here's something you can try right on the command line::

    % python
    >>> import eventlet 
    >>> from eventlet.green import urllib2
    >>> gt = eventlet.spawn(urllib2.urlopen, 'http://eventlet.net')
    >>> gt2 = eventlet.spawn(urllib2.urlopen, 'http://secondlife.com')
    >>> gt2.wait()
    >>> gt.wait()


Getting Eventlet
==================

The easiest way to get Eventlet is to use easy_install or pip::

  easy_install eventlet
  pip install eventlet

The development `tip`_ is available via easy_install as well::

  easy_install 'eventlet==dev'
  pip install 'eventlet==dev'

.. _tip: http://bitbucket.org/which_linden/eventlet/get/tip.zip#egg=eventlet-dev

Building the Docs Locally
=========================

To build a complete set of HTML documentation, you must have Sphinx, which can be found at http://sphinx.pocoo.org/ (or installed with `easy_install sphinx`)

  cd doc
  make html
  
The built html files can be found in doc/_build/html afterward.
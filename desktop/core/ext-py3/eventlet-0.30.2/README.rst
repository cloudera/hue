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

    % python3
    >>> import eventlet
    >>> from eventlet.green.urllib.request import urlopen
    >>> gt = eventlet.spawn(urlopen, 'http://eventlet.net')
    >>> gt2 = eventlet.spawn(urlopen, 'http://secondlife.com')
    >>> gt2.wait()
    >>> gt.wait()


Getting Eventlet
==================

The easiest way to get Eventlet is to use pip::

  pip install -U eventlet

To install latest development version once::

  pip install -U https://github.com/eventlet/eventlet/archive/master.zip


Building the Docs Locally
=========================

To build a complete set of HTML documentation, you must have Sphinx, which can be found at http://sphinx.pocoo.org/ (or installed with `pip install Sphinx`)::

  cd doc
  make html

The built html files can be found in doc/_build/html afterward.


Twisted
=======

Eventlet had Twisted hub in the past, but community interest to this integration has dropped over time,
now it is not supported, so with apologies for any inconvenience we discontinue Twisted integration.

If you have a project that uses Eventlet with Twisted, your options are:

* use last working release eventlet==0.14
* start a new project with only Twisted hub code, identify and fix problems. As of eventlet 0.13, `EVENTLET_HUB` environment variable can point to external modules.
* fork Eventlet, revert Twisted removal, identify and fix problems. This work may be merged back into main project.

Apologies for any inconvenience.

Supported Python versions
=========================

Currently CPython 2.7 and 3.4+ are supported, but **2.7 and 3.4 support is deprecated and will be removed in the future**, only CPython 3.5+ support will remain.

Flair
=====

.. image:: https://img.shields.io/pypi/v/eventlet
    :target: https://pypi.org/project/eventlet/

.. image:: https://travis-ci.org/eventlet/eventlet.svg?branch=master
    :target: https://travis-ci.org/eventlet/eventlet

.. image:: https://codecov.io/gh/eventlet/eventlet/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/eventlet/eventlet

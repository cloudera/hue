Eventlet Documentation
====================================

Code talks!  This is a simple web crawler that fetches a bunch of urls concurrently:

.. code-block:: python

    urls = [
        "http://www.google.com/intl/en_ALL/images/logo.gif",
        "http://python.org/images/python-logo.gif",
        "http://us.i1.yimg.com/us.yimg.com/i/ww/beta/y3.gif",
    ]

    import eventlet
    from eventlet.green.urllib.request import urlopen

    def fetch(url):
        return urlopen(url).read()

    pool = eventlet.GreenPool()
    for body in pool.imap(fetch, urls):
        print("got body", len(body))

Supported Python versions
=========================

Currently CPython 2.7 and 3.4+ are supported, but **2.7 and 3.4 support is deprecated and will be removed in the future**, only CPython 3.5+ support will remain.


Contents
=========

.. toctree::
   :maxdepth: 2

   basic_usage
   design_patterns
   patching
   examples
   ssl
   threading
   zeromq
   hubs
   testing
   environment

   modules

   authors
   history

License
---------
Eventlet is made available under the terms of the open source `MIT license <http://www.opensource.org/licenses/mit-license.php>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

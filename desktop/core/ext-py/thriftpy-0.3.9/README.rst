========
ThriftPy
========

.. image:: http://img.shields.io/travis/eleme/thriftpy/develop.svg?style=flat
   :target: https://travis-ci.org/eleme/thriftpy

.. image:: http://img.shields.io/github/release/eleme/thriftpy.svg?style=flat
   :target: https://github.com/eleme/thriftpy/releases

.. image:: http://img.shields.io/pypi/v/thriftpy.svg?style=flat
   :target: https://pypi.python.org/pypi/thriftpy

.. image:: http://img.shields.io/pypi/dm/thriftpy.svg?style=flat
   :target: https://pypi.python.org/pypi/thriftpy

ThriftPy is a pure python implementation of
`Apache Thrift <http://thrift.apache.org/>`_ in a pythonic way.

Documentation: https://thriftpy.readthedocs.org/


Installation
============

Install with pip.

.. code:: bash

    $ pip install thriftpy

You may also install cython first to build cython extension locally.

.. code:: bash

    $ pip install cython thriftpy


Code Demo
=========

ThriftPy make it super easy to write server/client code with thrift. Let's
checkout this simple pingpong service demo.

We need a 'pingpong.thrift' file:

::

    service PingPong {
        string ping(),
    }

Then we can make a server:

.. code:: python

    import thriftpy
    pingpong_thrift = thriftpy.load("pingpong.thrift", module_name="pingpong_thrift")

    from thriftpy.rpc import make_server

    class Dispatcher(object):
        def ping(self):
            return "pong"

    server = make_server(pingpong_thrift.PingPong, Dispatcher(), '127.0.0.1', 6000)
    server.serve()

And a client:

.. code:: python

    import thriftpy
    pingpong_thrift = thriftpy.load("pingpong.thrift", module_name="pingpong_thrift")

    from thriftpy.rpc import make_client

    client = make_client(pingpong_thrift.PingPong, '127.0.0.1', 6000)
    print(client.ping())

See, it's that easy!

You can refer to 'examples' and 'tests' directory in source code for more
usage examples.



Features
========

Currently ThriftPy have these features (also advantages over the upstream
python lib):

- Supports python2.6+, python3.3+, pypy and pypy3.

- Pure python implementation. No longer need to compile & install the 'thrift'
  package. All you need is thriftpy and thrift file.

- Compatible with Apache Thrift. You can use ThriftPy together with the
  official implementation servers and clients, such as a upstream server with
  a thriftpy client or the opposite.

  Currently implemented protocols and transports:

  * binary protocol (python and cython)

  * compact protocol (python and cython)

  * json protocol

  * buffered transport (python & cython)

  * framed transport

  * tornado server and client (with tornado 4.0)


- Can directly load thrift file as module, the sdk code will be generated on
  the fly.

  For example, ``pingpong_thrift = thriftpy.load("pingpong.thrift", module_name="pingpong_thrift")``
  will load 'pingpong.thrift' as 'pingpong_thrift' module.

  Or, when import hook enabled by ``thriftpy.install_import_hook()``, you can
  directly use ``import pingpong_thrift`` to import the 'pingpong.thrift' file
  as module, you may also use ``from pingpong_thrift import PingService`` to
  import specific object from the thrift module.

- Easy RPC server/client setup.



Contribute
==========

1. Fork the repo and make changes.

2. Write a test which shows a bug was fixed or the feature works as expected.

3. Make sure ``travis-ci`` or ``tox`` tests succeed.

4. Send pull request.


Contributors
============

https://github.com/eleme/thriftpy/graphs/contributors


Changelog
=========

https://github.com/eleme/thriftpy/blob/master/CHANGES.rst

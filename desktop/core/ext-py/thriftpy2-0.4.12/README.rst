============
ThriftPy2
============

.. image:: https://travis-ci.com/Thriftpy/thriftpy2.svg?branch=develop
    :target: https://travis-ci.com/Thriftpy/thriftpy2

.. image:: https://img.shields.io/codecov/c/github/Thriftpy/thriftpy2.svg
    :target: https://codecov.io/gh/Thriftpy/thriftpy2

.. image:: https://img.shields.io/pypi/dm/thriftpy2.svg
    :target: https://pypi.org/project/thriftpy2/

.. image:: https://img.shields.io/pypi/v/thriftpy2.svg
    :target: https://pypi.org/project/thriftpy2/

.. image:: https://img.shields.io/pypi/pyversions/thriftpy2.svg
    :target: https://pypi.org/project/thriftpy2/

.. image:: https://img.shields.io/pypi/implementation/thriftpy2.svg
    :target: https://pypi.org/project/thriftpy2/


ThriftPy: https://github.com/eleme/thriftpy has been deprecated, ThriftPy2 aims to provide long term support.


Migrate from Thriftpy?
======================

All you need is:

.. code:: python

    import thriftpy2 as thriftpy


That's it! thriftpy2 is fully compatible with thriftpy.


Installation
============

Install with pip.

.. code:: bash

    $ pip install thriftpy2

You may also install cython first to build cython extension locally.

.. code:: bash

    $ pip install cython thriftpy2


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

    import thriftpy2
    pingpong_thrift = thriftpy2.load("pingpong.thrift", module_name="pingpong_thrift")

    from thriftpy2.rpc import make_server

    class Dispatcher(object):
        def ping(self):
            return "pong"

    server = make_server(pingpong_thrift.PingPong, Dispatcher(), '127.0.0.1', 6000)
    server.serve()

And a client:

.. code:: python

    import thriftpy2
    pingpong_thrift = thriftpy2.load("pingpong.thrift", module_name="pingpong_thrift")

    from thriftpy2.rpc import make_client

    client = make_client(pingpong_thrift.PingPong, '127.0.0.1', 6000)
    print(client.ping())

And it also supports asyncio on Python 3.5 or later:

.. code:: python

    import thriftpy2
    import asyncio
    from thriftpy2.rpc import make_aio_client


    echo_thrift = thriftpy2.load("echo.thrift", module_name="echo_thrift")


    async def request():
        client = await make_aio_client(
            echo_thrift.EchoService, '127.0.0.1', 6000)
        print(await client.echo('hello, world'))
        client.close()

.. code:: python

    import asyncio
    import thriftpy2

    from thriftpy2.rpc import make_aio_server

    echo_thrift = thriftpy2.load("echo.thrift", module_name="echo_thrift")


    class Dispatcher(object):
        async def echo(self, param):
            print(param)
            await asyncio.sleep(0.1)
            return param


    def main():
        server = make_aio_server(
            echo_thrift.EchoService, Dispatcher(), '127.0.0.1', 6000)
        server.serve()


    if __name__ == '__main__':
        main()

See, it's that easy!

You can refer to 'examples' and 'tests' directory in source code for more
usage examples.


Features
========

Currently ThriftPy have these features (also advantages over the upstream
python lib):

- Supports Python 2.7, Python 3.4+, PyPy and PyPy3.

- Pure python implementation. No longer need to compile & install the 'thrift'
  package. All you need is thriftpy2 and thrift file.

- Compatible with Apache Thrift. You can use ThriftPy together with the
  official implementation servers and clients, such as a upstream server with
  a thriftpy2 client or the opposite.

  Currently implemented protocols and transports:

  * binary protocol (python and cython)

  * compact protocol (python and cython)

  * json protocol

  * buffered transport (python & cython)

  * framed transport

  * tornado server and client (with tornado 4.0)

  * http server and client

  * asyncio support (python 3.5 or later)

- Can directly load thrift file as module, the sdk code will be generated on
  the fly.

  For example, ``pingpong_thrift = thriftpy2.load("pingpong.thrift", module_name="pingpong_thrift")``
  will load 'pingpong.thrift' as 'pingpong_thrift' module.

  Or, when import hook enabled by ``thriftpy2.install_import_hook()``, you can
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

https://github.com/Thriftpy/thriftpy2/graphs/contributors


Sponsors:
============

.. image:: ./docs/jetbrains.svg
    :target: https://www.jetbrains.com/?from=ThriftPy


Changelog
=========

https://github.com/Thriftpy/thriftpy2/blob/master/CHANGES.rst

pyjwkest
========

Implementation of JWT, JWS, JWE and JWK as defined in:

- https://tools.ietf.org/html/draft-ietf-jose-json-web-signature
- https://tools.ietf.org/html/draft-ietf-jose-json-web-encryption
- https://tools.ietf.org/html/draft-ietf-jose-json-web-key-36

.. image:: https://api.travis-ci.org/rohe/pyjwkest.png?branch=master
    :target: https://travis-ci.org/rohe/pyjwkest

.. image:: https://img.shields.io/pypi/pyversions/pyjwkest.svg
    :target: https://pypi.python.org/pypi/pyjwkest

.. image:: https://img.shields.io/pypi/v/pyjwkest.svg
    :target: https://pypi.python.org/pypi/pyjwkest

.. image:: https://img.shields.io/pypi/dm/pyjwkest.svg
    :target: https://pypi.python.org/pypi/pyjwkest

.. image:: https://landscape.io/github/rohe/pyjwkest/master/landscape.svg?style=flat
    :target: https://landscape.io/github/rohe/pyjwkest/master

Installation
============

Pyjwkest is written and tested using Python version 2.7 and 3.4.

You should be able to simply run 'python setup.py install' to install it.

But you may get some complains during the installation of pycrypto.
Taken from the pycrypto installation text::

    If the setup.py script crashes with a DistutilsPlatformError complaining
    that the file /usr/lib/python2.2/config/Makefile doesn't exist, this means
    that the files needed for compiling new Python modules aren't installed on
    your system. Red Hat users often run into this because they don't have the
    python2-devel RPM installed. The fix is to simply install the requisite RPM.
    On Debian/Ubuntu, you need the python-dev package.

To verify that everything is in order, run "python setup.py test".


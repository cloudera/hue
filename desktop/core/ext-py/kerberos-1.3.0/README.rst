PyKerberos Package
==================

.. image:: https://travis-ci.org/apple/ccs-pykerberos.svg?branch=master
    :target: https://travis-ci.org/apple/ccs-pykerberos

This Python package is a high-level wrapper for Kerberos (GSSAPI)
operations.  The goal is to avoid having to build a module that wraps
the entire Kerberos.framework, and instead offer a limited set of
functions that do what is needed for client/server Kerberos
authentication based on <http://www.ietf.org/rfc/rfc4559.txt>.

Much of the C-code here is adapted from Apache's mod_auth_kerb-5.0rc7.


Build
=====

In this directory, run:

  python setup.py build


Testing
=======

To run the tests in the tests folder, you must have a valid Kerberos setup on
the test machine. You can use the script .travis.sh as quick and easy way to
setup a Kerberos KDC and Apache web endpoint that can be used for the tests.
Otherwise you can also run the following to run a self contained Docker
container

.. code-block: bash

  docker run \
  -v $(pwd):/app \
  -w /app \
  -e PYENV=2.7.13 \
  -e KERBEROS_USERNAME=administrator \
  -e KERBEROS_PASSWORD=Password01 \
  -e KERBEROS_REALM=example.com \
  -e KERBEROS_PORT=80 \
  ubuntu:16.04 \
  /bin/bash .travis.sh

The docker command needs to be run in the same directory as this library and
you can test it with different Python versions by changing the value of the
PYENV environment value set in the command.

Please have a look at testing_notes.md for more information.


IMPORTANT
=========

The checkPassword method provided by this library is meant only for testing purposes as it does
not offer any protection against possible KDC spoofing. That method should not be used in any
production code.


Channel Bindings
================

You can use this library to authenticate with Channel Binding support. Channel
Bindings are tags that identify the particular data channel being used with the
authentication. You can use Channel bindings to offer more proof of a valid
identity. Some services like Microsoft's Extended Protection can enforce
Channel Binding support on authorisation and you can use this library to meet
those requirements.

More details on Channel Bindings as set through the GSSAPI can be found here
<https://docs.oracle.com/cd/E19455-01/806-3814/overview-52/index.html>. Using
TLS as a example this is how you would add Channel Binding support to your
authentication mechanism. The following code snippet is based on RFC5929
<https://tools.ietf.org/html/rfc5929> using the 'tls-server-endpoint-point'
type.

.. code-block:: python

   import hashlib

    def get_channel_bindings_application_data(socket):
        # This is a highly simplified example, there are other use cases
        # where you might need to use different hash types or get a socket
        # object somehow.
        server_certificate = socket.getpeercert(True)
        certificate_hash = hashlib.sha256(server_certificate).hexdigest().upper()
        certificate_digest = base64.b16decode(certificate_hash)
        application_data = b'tls-server-end-point:%s' % certificate_digest

        return application_data

    def main():
        # Code to setup a socket with the server
        # A lot of code to setup the handshake and start the auth process
        socket = getsocketsomehow()

        # Connect to the host and start the auth process

        # Build the channel bindings object
        application_data = get_channel_bindings_application_data(socket)
        channel_bindings = kerberos.channelBindings(application_data=application_data)

        # More work to get responses from the server

        result, context = kerberos.authGSSClientInit(kerb_spn, gssflags=gssflags, principal=principal)

        # Pass through the channel_bindings object as created in the kerberos.channelBindings method
        result = kerberos.authGSSClientStep(context, neg_resp_value, channel_bindings=channel_bindings)

        # Repeat as necessary


Python APIs
===========

See kerberos.py.


Copyright and License
=====================

Copyright (c) 2006-2018 Apple Inc.  All rights reserved.

This software is licensed under the Apache License, Version 2.0.  The
Apache License is a well-established open source license, enabling
collaborative open source software development.

See the "LICENSE" file for the full text of the license terms.

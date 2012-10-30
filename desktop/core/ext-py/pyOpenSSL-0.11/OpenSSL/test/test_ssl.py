# Copyright (C) Jean-Paul Calderone 2008-2010, All rights reserved

"""
Unit tests for L{OpenSSL.SSL}.
"""

from errno import ECONNREFUSED, EINPROGRESS, EWOULDBLOCK
from sys import platform
from socket import error, socket
from os import makedirs
from os.path import join
from unittest import main

from OpenSSL.crypto import TYPE_RSA, FILETYPE_PEM, FILETYPE_ASN1
from OpenSSL.crypto import PKey, X509, X509Extension
from OpenSSL.crypto import dump_privatekey, load_privatekey
from OpenSSL.crypto import dump_certificate, load_certificate

from OpenSSL.SSL import SENT_SHUTDOWN, RECEIVED_SHUTDOWN
from OpenSSL.SSL import SSLv2_METHOD, SSLv3_METHOD, SSLv23_METHOD, TLSv1_METHOD
from OpenSSL.SSL import OP_NO_SSLv2, OP_NO_SSLv3, OP_SINGLE_DH_USE
from OpenSSL.SSL import VERIFY_PEER, VERIFY_FAIL_IF_NO_PEER_CERT, VERIFY_CLIENT_ONCE
from OpenSSL.SSL import Error, SysCallError, WantReadError, ZeroReturnError
from OpenSSL.SSL import Context, ContextType, Connection, ConnectionType

from OpenSSL.test.util import TestCase, bytes, b
from OpenSSL.test.test_crypto import cleartextCertificatePEM, cleartextPrivateKeyPEM
from OpenSSL.test.test_crypto import client_cert_pem, client_key_pem
from OpenSSL.test.test_crypto import server_cert_pem, server_key_pem, root_cert_pem

try:
    from OpenSSL.SSL import OP_NO_QUERY_MTU
except ImportError:
    OP_NO_QUERY_MTU = None
try:
    from OpenSSL.SSL import OP_COOKIE_EXCHANGE
except ImportError:
    OP_COOKIE_EXCHANGE = None
try:
    from OpenSSL.SSL import OP_NO_TICKET
except ImportError:
    OP_NO_TICKET = None


# openssl dhparam 128 -out dh-128.pem (note that 128 is a small number of bits
# to use)
dhparam = """\
-----BEGIN DH PARAMETERS-----
MBYCEQCobsg29c9WZP/54oAPcwiDAgEC
-----END DH PARAMETERS-----
"""


def verify_cb(conn, cert, errnum, depth, ok):
    return ok

def socket_pair():
    """
    Establish and return a pair of network sockets connected to each other.
    """
    # Connect a pair of sockets
    port = socket()
    port.bind(('', 0))
    port.listen(1)
    client = socket()
    client.setblocking(False)
    client.connect_ex(("127.0.0.1", port.getsockname()[1]))
    client.setblocking(True)
    server = port.accept()[0]

    # Let's pass some unencrypted data to make sure our socket connection is
    # fine.  Just one byte, so we don't have to worry about buffers getting
    # filled up or fragmentation.
    server.send(b("x"))
    assert client.recv(1024) == b("x")
    client.send(b("y"))
    assert server.recv(1024) == b("y")

    # Most of our callers want non-blocking sockets, make it easy for them.
    server.setblocking(False)
    client.setblocking(False)

    return (server, client)



def handshake(client, server):
    conns = [client, server]
    while conns:
        for conn in conns:
            try:
                conn.do_handshake()
            except WantReadError:
                pass
            else:
                conns.remove(conn)


class _LoopbackMixin:
    """
    Helper mixin which defines methods for creating a connected socket pair and
    for forcing two connected SSL sockets to talk to each other via memory BIOs.
    """
    def _loopback(self):
        (server, client) = socket_pair()

        ctx = Context(TLSv1_METHOD)
        ctx.use_privatekey(load_privatekey(FILETYPE_PEM, server_key_pem))
        ctx.use_certificate(load_certificate(FILETYPE_PEM, server_cert_pem))
        server = Connection(ctx, server)
        server.set_accept_state()
        client = Connection(Context(TLSv1_METHOD), client)
        client.set_connect_state()

        handshake(client, server)

        server.setblocking(True)
        client.setblocking(True)
        return server, client


    def _interactInMemory(self, client_conn, server_conn):
        """
        Try to read application bytes from each of the two L{Connection}
        objects.  Copy bytes back and forth between their send/receive buffers
        for as long as there is anything to copy.  When there is nothing more
        to copy, return C{None}.  If one of them actually manages to deliver
        some application bytes, return a two-tuple of the connection from which
        the bytes were read and the bytes themselves.
        """
        wrote = True
        while wrote:
            # Loop until neither side has anything to say
            wrote = False

            # Copy stuff from each side's send buffer to the other side's
            # receive buffer.
            for (read, write) in [(client_conn, server_conn),
                                  (server_conn, client_conn)]:

                # Give the side a chance to generate some more bytes, or
                # succeed.
                try:
                    bytes = read.recv(2 ** 16)
                except WantReadError:
                    # It didn't succeed, so we'll hope it generated some
                    # output.
                    pass
                else:
                    # It did succeed, so we'll stop now and let the caller deal
                    # with it.
                    return (read, bytes)

                while True:
                    # Keep copying as long as there's more stuff there.
                    try:
                        dirty = read.bio_read(4096)
                    except WantReadError:
                        # Okay, nothing more waiting to be sent.  Stop
                        # processing this send buffer.
                        break
                    else:
                        # Keep track of the fact that someone generated some
                        # output.
                        wrote = True
                        write.bio_write(dirty)



class ContextTests(TestCase, _LoopbackMixin):
    """
    Unit tests for L{OpenSSL.SSL.Context}.
    """
    def test_method(self):
        """
        L{Context} can be instantiated with one of L{SSLv2_METHOD},
        L{SSLv3_METHOD}, L{SSLv23_METHOD}, or L{TLSv1_METHOD}.
        """
        for meth in [SSLv2_METHOD, SSLv3_METHOD, SSLv23_METHOD, TLSv1_METHOD]:
            Context(meth)
        self.assertRaises(TypeError, Context, "")
        self.assertRaises(ValueError, Context, 10)


    def test_type(self):
        """
        L{Context} and L{ContextType} refer to the same type object and can be
        used to create instances of that type.
        """
        self.assertIdentical(Context, ContextType)
        self.assertConsistentType(Context, 'Context', TLSv1_METHOD)


    def test_use_privatekey(self):
        """
        L{Context.use_privatekey} takes an L{OpenSSL.crypto.PKey} instance.
        """
        key = PKey()
        key.generate_key(TYPE_RSA, 128)
        ctx = Context(TLSv1_METHOD)
        ctx.use_privatekey(key)
        self.assertRaises(TypeError, ctx.use_privatekey, "")


    def test_set_app_data_wrong_args(self):
        """
        L{Context.set_app_data} raises L{TypeError} if called with other than
        one argument.
        """
        context = Context(TLSv1_METHOD)
        self.assertRaises(TypeError, context.set_app_data)
        self.assertRaises(TypeError, context.set_app_data, None, None)


    def test_get_app_data_wrong_args(self):
        """
        L{Context.get_app_data} raises L{TypeError} if called with any
        arguments.
        """
        context = Context(TLSv1_METHOD)
        self.assertRaises(TypeError, context.get_app_data, None)


    def test_app_data(self):
        """
        L{Context.set_app_data} stores an object for later retrieval using
        L{Context.get_app_data}.
        """
        app_data = object()
        context = Context(TLSv1_METHOD)
        context.set_app_data(app_data)
        self.assertIdentical(context.get_app_data(), app_data)


    def test_set_options_wrong_args(self):
        """
        L{Context.set_options} raises L{TypeError} if called with the wrong
        number of arguments or a non-C{int} argument.
        """
        context = Context(TLSv1_METHOD)
        self.assertRaises(TypeError, context.set_options)
        self.assertRaises(TypeError, context.set_options, None)
        self.assertRaises(TypeError, context.set_options, 1, None)


    def test_set_timeout_wrong_args(self):
        """
        L{Context.set_timeout} raises L{TypeError} if called with the wrong
        number of arguments or a non-C{int} argument.
        """
        context = Context(TLSv1_METHOD)
        self.assertRaises(TypeError, context.set_timeout)
        self.assertRaises(TypeError, context.set_timeout, None)
        self.assertRaises(TypeError, context.set_timeout, 1, None)


    def test_get_timeout_wrong_args(self):
        """
        L{Context.get_timeout} raises L{TypeError} if called with any arguments.
        """
        context = Context(TLSv1_METHOD)
        self.assertRaises(TypeError, context.get_timeout, None)


    def test_timeout(self):
        """
        L{Context.set_timeout} sets the session timeout for all connections
        created using the context object.  L{Context.get_timeout} retrieves this
        value.
        """
        context = Context(TLSv1_METHOD)
        context.set_timeout(1234)
        self.assertEquals(context.get_timeout(), 1234)


    def test_set_verify_depth_wrong_args(self):
        """
        L{Context.set_verify_depth} raises L{TypeError} if called with the wrong
        number of arguments or a non-C{int} argument.
        """
        context = Context(TLSv1_METHOD)
        self.assertRaises(TypeError, context.set_verify_depth)
        self.assertRaises(TypeError, context.set_verify_depth, None)
        self.assertRaises(TypeError, context.set_verify_depth, 1, None)


    def test_get_verify_depth_wrong_args(self):
        """
        L{Context.get_verify_depth} raises L{TypeError} if called with any arguments.
        """
        context = Context(TLSv1_METHOD)
        self.assertRaises(TypeError, context.get_verify_depth, None)


    def test_verify_depth(self):
        """
        L{Context.set_verify_depth} sets the number of certificates in a chain
        to follow before giving up.  The value can be retrieved with
        L{Context.get_verify_depth}.
        """
        context = Context(TLSv1_METHOD)
        context.set_verify_depth(11)
        self.assertEquals(context.get_verify_depth(), 11)


    def _write_encrypted_pem(self, passphrase):
        """
        Write a new private key out to a new file, encrypted using the given
        passphrase.  Return the path to the new file.
        """
        key = PKey()
        key.generate_key(TYPE_RSA, 128)
        pemFile = self.mktemp()
        fObj = open(pemFile, 'w')
        pem = dump_privatekey(FILETYPE_PEM, key, "blowfish", passphrase)
        fObj.write(pem.decode('ascii'))
        fObj.close()
        return pemFile


    def test_set_passwd_cb_wrong_args(self):
        """
        L{Context.set_passwd_cb} raises L{TypeError} if called with the
        wrong arguments or with a non-callable first argument.
        """
        context = Context(TLSv1_METHOD)
        self.assertRaises(TypeError, context.set_passwd_cb)
        self.assertRaises(TypeError, context.set_passwd_cb, None)
        self.assertRaises(TypeError, context.set_passwd_cb, lambda: None, None, None)


    def test_set_passwd_cb(self):
        """
        L{Context.set_passwd_cb} accepts a callable which will be invoked when
        a private key is loaded from an encrypted PEM.
        """
        passphrase = b("foobar")
        pemFile = self._write_encrypted_pem(passphrase)
        calledWith = []
        def passphraseCallback(maxlen, verify, extra):
            calledWith.append((maxlen, verify, extra))
            return passphrase
        context = Context(TLSv1_METHOD)
        context.set_passwd_cb(passphraseCallback)
        context.use_privatekey_file(pemFile)
        self.assertTrue(len(calledWith), 1)
        self.assertTrue(isinstance(calledWith[0][0], int))
        self.assertTrue(isinstance(calledWith[0][1], int))
        self.assertEqual(calledWith[0][2], None)


    def test_passwd_callback_exception(self):
        """
        L{Context.use_privatekey_file} propagates any exception raised by the
        passphrase callback.
        """
        pemFile = self._write_encrypted_pem(b("monkeys are nice"))
        def passphraseCallback(maxlen, verify, extra):
            raise RuntimeError("Sorry, I am a fail.")

        context = Context(TLSv1_METHOD)
        context.set_passwd_cb(passphraseCallback)
        self.assertRaises(RuntimeError, context.use_privatekey_file, pemFile)


    def test_passwd_callback_false(self):
        """
        L{Context.use_privatekey_file} raises L{OpenSSL.SSL.Error} if the
        passphrase callback returns a false value.
        """
        pemFile = self._write_encrypted_pem(b("monkeys are nice"))
        def passphraseCallback(maxlen, verify, extra):
            return None

        context = Context(TLSv1_METHOD)
        context.set_passwd_cb(passphraseCallback)
        self.assertRaises(Error, context.use_privatekey_file, pemFile)


    def test_passwd_callback_non_string(self):
        """
        L{Context.use_privatekey_file} raises L{OpenSSL.SSL.Error} if the
        passphrase callback returns a true non-string value.
        """
        pemFile = self._write_encrypted_pem(b("monkeys are nice"))
        def passphraseCallback(maxlen, verify, extra):
            return 10

        context = Context(TLSv1_METHOD)
        context.set_passwd_cb(passphraseCallback)
        self.assertRaises(Error, context.use_privatekey_file, pemFile)


    def test_passwd_callback_too_long(self):
        """
        If the passphrase returned by the passphrase callback returns a string
        longer than the indicated maximum length, it is truncated.
        """
        # A priori knowledge!
        passphrase = b("x") * 1024
        pemFile = self._write_encrypted_pem(passphrase)
        def passphraseCallback(maxlen, verify, extra):
            assert maxlen == 1024
            return passphrase + b("y")

        context = Context(TLSv1_METHOD)
        context.set_passwd_cb(passphraseCallback)
        # This shall succeed because the truncated result is the correct
        # passphrase.
        context.use_privatekey_file(pemFile)


    def test_set_info_callback(self):
        """
        L{Context.set_info_callback} accepts a callable which will be invoked
        when certain information about an SSL connection is available.
        """
        (server, client) = socket_pair()

        clientSSL = Connection(Context(TLSv1_METHOD), client)
        clientSSL.set_connect_state()

        called = []
        def info(conn, where, ret):
            called.append((conn, where, ret))
        context = Context(TLSv1_METHOD)
        context.set_info_callback(info)
        context.use_certificate(
            load_certificate(FILETYPE_PEM, cleartextCertificatePEM))
        context.use_privatekey(
            load_privatekey(FILETYPE_PEM, cleartextPrivateKeyPEM))

        serverSSL = Connection(context, server)
        serverSSL.set_accept_state()

        while not called:
            for ssl in clientSSL, serverSSL:
                try:
                    ssl.do_handshake()
                except WantReadError:
                    pass

        # Kind of lame.  Just make sure it got called somehow.
        self.assertTrue(called)


    def _load_verify_locations_test(self, *args):
        """
        Create a client context which will verify the peer certificate and call
        its C{load_verify_locations} method with C{*args}.  Then connect it to a
        server and ensure that the handshake succeeds.
        """
        (server, client) = socket_pair()

        clientContext = Context(TLSv1_METHOD)
        clientContext.load_verify_locations(*args)
        # Require that the server certificate verify properly or the
        # connection will fail.
        clientContext.set_verify(
            VERIFY_PEER,
            lambda conn, cert, errno, depth, preverify_ok: preverify_ok)

        clientSSL = Connection(clientContext, client)
        clientSSL.set_connect_state()

        serverContext = Context(TLSv1_METHOD)
        serverContext.use_certificate(
            load_certificate(FILETYPE_PEM, cleartextCertificatePEM))
        serverContext.use_privatekey(
            load_privatekey(FILETYPE_PEM, cleartextPrivateKeyPEM))

        serverSSL = Connection(serverContext, server)
        serverSSL.set_accept_state()

        # Without load_verify_locations above, the handshake
        # will fail:
        # Error: [('SSL routines', 'SSL3_GET_SERVER_CERTIFICATE',
        #          'certificate verify failed')]
        handshake(clientSSL, serverSSL)

        cert = clientSSL.get_peer_certificate()
        self.assertEqual(cert.get_subject().CN, 'Testing Root CA')


    def test_load_verify_file(self):
        """
        L{Context.load_verify_locations} accepts a file name and uses the
        certificates within for verification purposes.
        """
        cafile = self.mktemp()
        fObj = open(cafile, 'w')
        fObj.write(cleartextCertificatePEM.decode('ascii'))
        fObj.close()

        self._load_verify_locations_test(cafile)


    def test_load_verify_invalid_file(self):
        """
        L{Context.load_verify_locations} raises L{Error} when passed a
        non-existent cafile.
        """
        clientContext = Context(TLSv1_METHOD)
        self.assertRaises(
            Error, clientContext.load_verify_locations, self.mktemp())


    def test_load_verify_directory(self):
        """
        L{Context.load_verify_locations} accepts a directory name and uses
        the certificates within for verification purposes.
        """
        capath = self.mktemp()
        makedirs(capath)
        # Hash value computed manually with c_rehash to avoid depending on
        # c_rehash in the test suite.
        cafile = join(capath, 'c7adac82.0')
        fObj = open(cafile, 'w')
        fObj.write(cleartextCertificatePEM.decode('ascii'))
        fObj.close()

        self._load_verify_locations_test(None, capath)


    def test_load_verify_locations_wrong_args(self):
        """
        L{Context.load_verify_locations} raises L{TypeError} if called with
        the wrong number of arguments or with non-C{str} arguments.
        """
        context = Context(TLSv1_METHOD)
        self.assertRaises(TypeError, context.load_verify_locations)
        self.assertRaises(TypeError, context.load_verify_locations, object())
        self.assertRaises(TypeError, context.load_verify_locations, object(), object())
        self.assertRaises(TypeError, context.load_verify_locations, None, None, None)


    if platform == "win32":
        "set_default_verify_paths appears not to work on Windows.  "
        "See LP#404343 and LP#404344."
    else:
        def test_set_default_verify_paths(self):
            """
            L{Context.set_default_verify_paths} causes the platform-specific CA
            certificate locations to be used for verification purposes.
            """
            # Testing this requires a server with a certificate signed by one of
            # the CAs in the platform CA location.  Getting one of those costs
            # money.  Fortunately (or unfortunately, depending on your
            # perspective), it's easy to think of a public server on the
            # internet which has such a certificate.  Connecting to the network
            # in a unit test is bad, but it's the only way I can think of to
            # really test this. -exarkun

            # Arg, verisign.com doesn't speak TLSv1
            context = Context(SSLv3_METHOD)
            context.set_default_verify_paths()
            context.set_verify(
                VERIFY_PEER,
                lambda conn, cert, errno, depth, preverify_ok: preverify_ok)

            client = socket()
            client.connect(('verisign.com', 443))
            clientSSL = Connection(context, client)
            clientSSL.set_connect_state()
            clientSSL.do_handshake()
            clientSSL.send('GET / HTTP/1.0\r\n\r\n')
            self.assertTrue(clientSSL.recv(1024))


    def test_set_default_verify_paths_signature(self):
        """
        L{Context.set_default_verify_paths} takes no arguments and raises
        L{TypeError} if given any.
        """
        context = Context(TLSv1_METHOD)
        self.assertRaises(TypeError, context.set_default_verify_paths, None)
        self.assertRaises(TypeError, context.set_default_verify_paths, 1)
        self.assertRaises(TypeError, context.set_default_verify_paths, "")


    def test_add_extra_chain_cert_invalid_cert(self):
        """
        L{Context.add_extra_chain_cert} raises L{TypeError} if called with
        other than one argument or if called with an object which is not an
        instance of L{X509}.
        """
        context = Context(TLSv1_METHOD)
        self.assertRaises(TypeError, context.add_extra_chain_cert)
        self.assertRaises(TypeError, context.add_extra_chain_cert, object())
        self.assertRaises(TypeError, context.add_extra_chain_cert, object(), object())


    def _create_certificate_chain(self):
        """
        Construct and return a chain of certificates.

            1. A new self-signed certificate authority certificate (cacert)
            2. A new intermediate certificate signed by cacert (icert)
            3. A new server certificate signed by icert (scert)
        """
        caext = X509Extension(b('basicConstraints'), False, b('CA:true'))

        # Step 1
        cakey = PKey()
        cakey.generate_key(TYPE_RSA, 512)
        cacert = X509()
        cacert.get_subject().commonName = "Authority Certificate"
        cacert.set_issuer(cacert.get_subject())
        cacert.set_pubkey(cakey)
        cacert.set_notBefore(b("20000101000000Z"))
        cacert.set_notAfter(b("20200101000000Z"))
        cacert.add_extensions([caext])
        cacert.set_serial_number(0)
        cacert.sign(cakey, "sha1")

        # Step 2
        ikey = PKey()
        ikey.generate_key(TYPE_RSA, 512)
        icert = X509()
        icert.get_subject().commonName = "Intermediate Certificate"
        icert.set_issuer(cacert.get_subject())
        icert.set_pubkey(ikey)
        icert.set_notBefore(b("20000101000000Z"))
        icert.set_notAfter(b("20200101000000Z"))
        icert.add_extensions([caext])
        icert.set_serial_number(0)
        icert.sign(cakey, "sha1")

        # Step 3
        skey = PKey()
        skey.generate_key(TYPE_RSA, 512)
        scert = X509()
        scert.get_subject().commonName = "Server Certificate"
        scert.set_issuer(icert.get_subject())
        scert.set_pubkey(skey)
        scert.set_notBefore(b("20000101000000Z"))
        scert.set_notAfter(b("20200101000000Z"))
        scert.add_extensions([
                X509Extension(b('basicConstraints'), True, b('CA:false'))])
        scert.set_serial_number(0)
        scert.sign(ikey, "sha1")

        return [(cakey, cacert), (ikey, icert), (skey, scert)]


    def _handshake_test(self, serverContext, clientContext):
        """
        Verify that a client and server created with the given contexts can
        successfully handshake and communicate.
        """
        serverSocket, clientSocket = socket_pair()

        server = Connection(serverContext, serverSocket)
        server.set_accept_state()

        client = Connection(clientContext, clientSocket)
        client.set_connect_state()

        # Make them talk to each other.
        # self._interactInMemory(client, server)
        for i in range(3):
            for s in [client, server]:
                try:
                    s.do_handshake()
                except WantReadError:
                    pass


    def test_add_extra_chain_cert(self):
        """
        L{Context.add_extra_chain_cert} accepts an L{X509} instance to add to
        the certificate chain.

        See L{_create_certificate_chain} for the details of the certificate
        chain tested.

        The chain is tested by starting a server with scert and connecting
        to it with a client which trusts cacert and requires verification to
        succeed.
        """
        chain = self._create_certificate_chain()
        [(cakey, cacert), (ikey, icert), (skey, scert)] = chain

        # Dump the CA certificate to a file because that's the only way to load
        # it as a trusted CA in the client context.
        for cert, name in [(cacert, 'ca.pem'), (icert, 'i.pem'), (scert, 's.pem')]:
            fObj = open(name, 'w')
            fObj.write(dump_certificate(FILETYPE_PEM, cert).decode('ascii'))
            fObj.close()

        for key, name in [(cakey, 'ca.key'), (ikey, 'i.key'), (skey, 's.key')]:
            fObj = open(name, 'w')
            fObj.write(dump_privatekey(FILETYPE_PEM, key).decode('ascii'))
            fObj.close()

        # Create the server context
        serverContext = Context(TLSv1_METHOD)
        serverContext.use_privatekey(skey)
        serverContext.use_certificate(scert)
        # The client already has cacert, we only need to give them icert.
        serverContext.add_extra_chain_cert(icert)

        # Create the client
        clientContext = Context(TLSv1_METHOD)
        clientContext.set_verify(
            VERIFY_PEER | VERIFY_FAIL_IF_NO_PEER_CERT, verify_cb)
        clientContext.load_verify_locations('ca.pem')

        # Try it out.
        self._handshake_test(serverContext, clientContext)


    def test_use_certificate_chain_file(self):
        """
        L{Context.use_certificate_chain_file} reads a certificate chain from
        the specified file.

        The chain is tested by starting a server with scert and connecting
        to it with a client which trusts cacert and requires verification to
        succeed.
        """
        chain = self._create_certificate_chain()
        [(cakey, cacert), (ikey, icert), (skey, scert)] = chain

        # Write out the chain file.
        chainFile = self.mktemp()
        fObj = open(chainFile, 'w')
        # Most specific to least general.
        fObj.write(dump_certificate(FILETYPE_PEM, scert).decode('ascii'))
        fObj.write(dump_certificate(FILETYPE_PEM, icert).decode('ascii'))
        fObj.write(dump_certificate(FILETYPE_PEM, cacert).decode('ascii'))
        fObj.close()

        serverContext = Context(TLSv1_METHOD)
        serverContext.use_certificate_chain_file(chainFile)
        serverContext.use_privatekey(skey)

        fObj = open('ca.pem', 'w')
        fObj.write(dump_certificate(FILETYPE_PEM, cacert).decode('ascii'))
        fObj.close()

        clientContext = Context(TLSv1_METHOD)
        clientContext.set_verify(
            VERIFY_PEER | VERIFY_FAIL_IF_NO_PEER_CERT, verify_cb)
        clientContext.load_verify_locations('ca.pem')

        self._handshake_test(serverContext, clientContext)

    # XXX load_client_ca
    # XXX set_session_id

    def test_get_verify_mode_wrong_args(self):
        """
        L{Context.get_verify_mode} raises L{TypeError} if called with any
        arguments.
        """
        context = Context(TLSv1_METHOD)
        self.assertRaises(TypeError, context.get_verify_mode, None)


    def test_get_verify_mode(self):
        """
        L{Context.get_verify_mode} returns the verify mode flags previously
        passed to L{Context.set_verify}.
        """
        context = Context(TLSv1_METHOD)
        self.assertEquals(context.get_verify_mode(), 0)
        context.set_verify(
            VERIFY_PEER | VERIFY_CLIENT_ONCE, lambda *args: None)
        self.assertEquals(
            context.get_verify_mode(), VERIFY_PEER | VERIFY_CLIENT_ONCE)


    def test_load_tmp_dh_wrong_args(self):
        """
        L{Context.load_tmp_dh} raises L{TypeError} if called with the wrong
        number of arguments or with a non-C{str} argument.
        """
        context = Context(TLSv1_METHOD)
        self.assertRaises(TypeError, context.load_tmp_dh)
        self.assertRaises(TypeError, context.load_tmp_dh, "foo", None)
        self.assertRaises(TypeError, context.load_tmp_dh, object())


    def test_load_tmp_dh_missing_file(self):
        """
        L{Context.load_tmp_dh} raises L{OpenSSL.SSL.Error} if the specified file
        does not exist.
        """
        context = Context(TLSv1_METHOD)
        self.assertRaises(Error, context.load_tmp_dh, "hello")


    def test_load_tmp_dh(self):
        """
        L{Context.load_tmp_dh} loads Diffie-Hellman parameters from the
        specified file.
        """
        context = Context(TLSv1_METHOD)
        dhfilename = self.mktemp()
        dhfile = open(dhfilename, "w")
        dhfile.write(dhparam)
        dhfile.close()
        context.load_tmp_dh(dhfilename)
        # XXX What should I assert here? -exarkun


    def test_set_cipher_list(self):
        """
        L{Context.set_cipher_list} accepts a C{str} naming the ciphers which
        connections created with the context object will be able to choose from.
        """
        context = Context(TLSv1_METHOD)
        context.set_cipher_list("hello world:EXP-RC4-MD5")
        conn = Connection(context, None)
        self.assertEquals(conn.get_cipher_list(), ["EXP-RC4-MD5"])



class ConnectionTests(TestCase, _LoopbackMixin):
    """
    Unit tests for L{OpenSSL.SSL.Connection}.
    """
    # XXX want_write
    # XXX want_read
    # XXX get_peer_certificate -> None
    # XXX sock_shutdown
    # XXX master_key -> TypeError
    # XXX server_random -> TypeError
    # XXX state_string
    # XXX connect -> TypeError
    # XXX connect_ex -> TypeError
    # XXX set_connect_state -> TypeError
    # XXX set_accept_state -> TypeError
    # XXX renegotiate_pending
    # XXX do_handshake -> TypeError
    # XXX bio_read -> TypeError
    # XXX recv -> TypeError
    # XXX send -> TypeError
    # XXX bio_write -> TypeError

    def test_type(self):
        """
        L{Connection} and L{ConnectionType} refer to the same type object and
        can be used to create instances of that type.
        """
        self.assertIdentical(Connection, ConnectionType)
        ctx = Context(TLSv1_METHOD)
        self.assertConsistentType(Connection, 'Connection', ctx, None)


    def test_get_context(self):
        """
        L{Connection.get_context} returns the L{Context} instance used to
        construct the L{Connection} instance.
        """
        context = Context(TLSv1_METHOD)
        connection = Connection(context, None)
        self.assertIdentical(connection.get_context(), context)


    def test_get_context_wrong_args(self):
        """
        L{Connection.get_context} raises L{TypeError} if called with any
        arguments.
        """
        connection = Connection(Context(TLSv1_METHOD), None)
        self.assertRaises(TypeError, connection.get_context, None)


    def test_pending(self):
        """
        L{Connection.pending} returns the number of bytes available for
        immediate read.
        """
        connection = Connection(Context(TLSv1_METHOD), None)
        self.assertEquals(connection.pending(), 0)


    def test_pending_wrong_args(self):
        """
        L{Connection.pending} raises L{TypeError} if called with any arguments.
        """
        connection = Connection(Context(TLSv1_METHOD), None)
        self.assertRaises(TypeError, connection.pending, None)


    def test_connect_wrong_args(self):
        """
        L{Connection.connect} raises L{TypeError} if called with a non-address
        argument or with the wrong number of arguments.
        """
        connection = Connection(Context(TLSv1_METHOD), socket())
        self.assertRaises(TypeError, connection.connect, None)
        self.assertRaises(TypeError, connection.connect)
        self.assertRaises(TypeError, connection.connect, ("127.0.0.1", 1), None)


    def test_connect_refused(self):
        """
        L{Connection.connect} raises L{socket.error} if the underlying socket
        connect method raises it.
        """
        client = socket()
        context = Context(TLSv1_METHOD)
        clientSSL = Connection(context, client)
        exc = self.assertRaises(error, clientSSL.connect, ("127.0.0.1", 1))
        self.assertEquals(exc.args[0], ECONNREFUSED)


    def test_connect(self):
        """
        L{Connection.connect} establishes a connection to the specified address.
        """
        port = socket()
        port.bind(('', 0))
        port.listen(3)

        clientSSL = Connection(Context(TLSv1_METHOD), socket())
        clientSSL.connect(('127.0.0.1', port.getsockname()[1]))
        # XXX An assertion?  Or something?


    if platform == "darwin":
        "connect_ex sometimes causes a kernel panic on OS X 10.6.4"
    else:
        def test_connect_ex(self):
            """
            If there is a connection error, L{Connection.connect_ex} returns the
            errno instead of raising an exception.
            """
            port = socket()
            port.bind(('', 0))
            port.listen(3)

            clientSSL = Connection(Context(TLSv1_METHOD), socket())
            clientSSL.setblocking(False)
            result = clientSSL.connect_ex(port.getsockname())
            expected = (EINPROGRESS, EWOULDBLOCK)
            self.assertTrue(
                    result in expected, "%r not in %r" % (result, expected))


    def test_accept_wrong_args(self):
        """
        L{Connection.accept} raises L{TypeError} if called with any arguments.
        """
        connection = Connection(Context(TLSv1_METHOD), socket())
        self.assertRaises(TypeError, connection.accept, None)


    def test_accept(self):
        """
        L{Connection.accept} accepts a pending connection attempt and returns a
        tuple of a new L{Connection} (the accepted client) and the address the
        connection originated from.
        """
        ctx = Context(TLSv1_METHOD)
        ctx.use_privatekey(load_privatekey(FILETYPE_PEM, server_key_pem))
        ctx.use_certificate(load_certificate(FILETYPE_PEM, server_cert_pem))
        port = socket()
        portSSL = Connection(ctx, port)
        portSSL.bind(('', 0))
        portSSL.listen(3)

        clientSSL = Connection(Context(TLSv1_METHOD), socket())

        # Calling portSSL.getsockname() here to get the server IP address sounds
        # great, but frequently fails on Windows.
        clientSSL.connect(('127.0.0.1', portSSL.getsockname()[1]))

        serverSSL, address = portSSL.accept()

        self.assertTrue(isinstance(serverSSL, Connection))
        self.assertIdentical(serverSSL.get_context(), ctx)
        self.assertEquals(address, clientSSL.getsockname())


    def test_shutdown_wrong_args(self):
        """
        L{Connection.shutdown} raises L{TypeError} if called with the wrong
        number of arguments or with arguments other than integers.
        """
        connection = Connection(Context(TLSv1_METHOD), None)
        self.assertRaises(TypeError, connection.shutdown, None)
        self.assertRaises(TypeError, connection.get_shutdown, None)
        self.assertRaises(TypeError, connection.set_shutdown)
        self.assertRaises(TypeError, connection.set_shutdown, None)
        self.assertRaises(TypeError, connection.set_shutdown, 0, 1)


    def test_shutdown(self):
        """
        L{Connection.shutdown} performs an SSL-level connection shutdown.
        """
        server, client = self._loopback()
        self.assertFalse(server.shutdown())
        self.assertEquals(server.get_shutdown(), SENT_SHUTDOWN)
        self.assertRaises(ZeroReturnError, client.recv, 1024)
        self.assertEquals(client.get_shutdown(), RECEIVED_SHUTDOWN)
        client.shutdown()
        self.assertEquals(client.get_shutdown(), SENT_SHUTDOWN|RECEIVED_SHUTDOWN)
        self.assertRaises(ZeroReturnError, server.recv, 1024)
        self.assertEquals(server.get_shutdown(), SENT_SHUTDOWN|RECEIVED_SHUTDOWN)


    def test_set_shutdown(self):
        """
        L{Connection.set_shutdown} sets the state of the SSL connection shutdown
        process.
        """
        connection = Connection(Context(TLSv1_METHOD), socket())
        connection.set_shutdown(RECEIVED_SHUTDOWN)
        self.assertEquals(connection.get_shutdown(), RECEIVED_SHUTDOWN)


    def test_app_data_wrong_args(self):
        """
        L{Connection.set_app_data} raises L{TypeError} if called with other than
        one argument.  L{Connection.get_app_data} raises L{TypeError} if called
        with any arguments.
        """
        conn = Connection(Context(TLSv1_METHOD), None)
        self.assertRaises(TypeError, conn.get_app_data, None)
        self.assertRaises(TypeError, conn.set_app_data)
        self.assertRaises(TypeError, conn.set_app_data, None, None)


    def test_app_data(self):
        """
        Any object can be set as app data by passing it to
        L{Connection.set_app_data} and later retrieved with
        L{Connection.get_app_data}.
        """
        conn = Connection(Context(TLSv1_METHOD), None)
        app_data = object()
        conn.set_app_data(app_data)
        self.assertIdentical(conn.get_app_data(), app_data)


    def test_makefile(self):
        """
        L{Connection.makefile} is not implemented and calling that method raises
        L{NotImplementedError}.
        """
        conn = Connection(Context(TLSv1_METHOD), None)
        self.assertRaises(NotImplementedError, conn.makefile)



class ConnectionGetCipherListTests(TestCase):
    """
    Tests for L{Connection.get_cipher_list}.
    """
    def test_wrong_args(self):
        """
        L{Connection.get_cipher_list} raises L{TypeError} if called with any
        arguments.
        """
        connection = Connection(Context(TLSv1_METHOD), None)
        self.assertRaises(TypeError, connection.get_cipher_list, None)


    def test_result(self):
        """
        L{Connection.get_cipher_list} returns a C{list} of C{str} giving the
        names of the ciphers which might be used.
        """
        connection = Connection(Context(TLSv1_METHOD), None)
        ciphers = connection.get_cipher_list()
        self.assertTrue(isinstance(ciphers, list))
        for cipher in ciphers:
            self.assertTrue(isinstance(cipher, str))



class ConnectionSendallTests(TestCase, _LoopbackMixin):
    """
    Tests for L{Connection.sendall}.
    """
    def test_wrong_args(self):
        """
        When called with arguments other than a single string,
        L{Connection.sendall} raises L{TypeError}.
        """
        connection = Connection(Context(TLSv1_METHOD), None)
        self.assertRaises(TypeError, connection.sendall)
        self.assertRaises(TypeError, connection.sendall, object())
        self.assertRaises(TypeError, connection.sendall, "foo", "bar")


    def test_short(self):
        """
        L{Connection.sendall} transmits all of the bytes in the string passed to
        it.
        """
        server, client = self._loopback()
        server.sendall(b('x'))
        self.assertEquals(client.recv(1), b('x'))


    def test_long(self):
        """
        L{Connection.sendall} transmits all of the bytes in the string passed to
        it even if this requires multiple calls of an underlying write function.
        """
        server, client = self._loopback()
        # Should be enough, underlying SSL_write should only do 16k at a time.
        # On Windows, after 32k of bytes the write will block (forever - because
        # no one is yet reading).
        message = b('x') * (1024 * 32 - 1) + b('y')
        server.sendall(message)
        accum = []
        received = 0
        while received < len(message):
            data = client.recv(1024)
            accum.append(data)
            received += len(data)
        self.assertEquals(message, b('').join(accum))


    def test_closed(self):
        """
        If the underlying socket is closed, L{Connection.sendall} propagates the
        write error from the low level write call.
        """
        server, client = self._loopback()
        server.sock_shutdown(2)
        self.assertRaises(SysCallError, server.sendall, "hello, world")



class ConnectionRenegotiateTests(TestCase, _LoopbackMixin):
    """
    Tests for SSL renegotiation APIs.
    """
    def test_renegotiate_wrong_args(self):
        """
        L{Connection.renegotiate} raises L{TypeError} if called with any
        arguments.
        """
        connection = Connection(Context(TLSv1_METHOD), None)
        self.assertRaises(TypeError, connection.renegotiate, None)


    def test_total_renegotiations_wrong_args(self):
        """
        L{Connection.total_renegotiations} raises L{TypeError} if called with
        any arguments.
        """
        connection = Connection(Context(TLSv1_METHOD), None)
        self.assertRaises(TypeError, connection.total_renegotiations, None)


    def test_total_renegotiations(self):
        """
        L{Connection.total_renegotiations} returns C{0} before any
        renegotiations have happened.
        """
        connection = Connection(Context(TLSv1_METHOD), None)
        self.assertEquals(connection.total_renegotiations(), 0)


#     def test_renegotiate(self):
#         """
#         """
#         server, client = self._loopback()

#         server.send("hello world")
#         self.assertEquals(client.recv(len("hello world")), "hello world")

#         self.assertEquals(server.total_renegotiations(), 0)
#         self.assertTrue(server.renegotiate())

#         server.setblocking(False)
#         client.setblocking(False)
#         while server.renegotiate_pending():
#             client.do_handshake()
#             server.do_handshake()

#         self.assertEquals(server.total_renegotiations(), 1)




class ErrorTests(TestCase):
    """
    Unit tests for L{OpenSSL.SSL.Error}.
    """
    def test_type(self):
        """
        L{Error} is an exception type.
        """
        self.assertTrue(issubclass(Error, Exception))
        self.assertEqual(Error.__name__, 'Error')



class ConstantsTests(TestCase):
    """
    Tests for the values of constants exposed in L{OpenSSL.SSL}.

    These are values defined by OpenSSL intended only to be used as flags to
    OpenSSL APIs.  The only assertions it seems can be made about them is
    their values.
    """
    # unittest.TestCase has no skip mechanism
    if OP_NO_QUERY_MTU is not None:
        def test_op_no_query_mtu(self):
            """
            The value of L{OpenSSL.SSL.OP_NO_QUERY_MTU} is 0x1000, the value of
            I{SSL_OP_NO_QUERY_MTU} defined by I{openssl/ssl.h}.
            """
            self.assertEqual(OP_NO_QUERY_MTU, 0x1000)
    else:
        "OP_NO_QUERY_MTU unavailable - OpenSSL version may be too old"


    if OP_COOKIE_EXCHANGE is not None:
        def test_op_cookie_exchange(self):
            """
            The value of L{OpenSSL.SSL.OP_COOKIE_EXCHANGE} is 0x2000, the value
            of I{SSL_OP_COOKIE_EXCHANGE} defined by I{openssl/ssl.h}.
            """
            self.assertEqual(OP_COOKIE_EXCHANGE, 0x2000)
    else:
        "OP_COOKIE_EXCHANGE unavailable - OpenSSL version may be too old"


    if OP_NO_TICKET is not None:
        def test_op_no_ticket(self):
            """
            The value of L{OpenSSL.SSL.OP_NO_TICKET} is 0x4000, the value of
            I{SSL_OP_NO_TICKET} defined by I{openssl/ssl.h}.
            """
            self.assertEqual(OP_NO_TICKET, 0x4000)
    else:
        "OP_NO_TICKET unavailable - OpenSSL version may be too old"



class MemoryBIOTests(TestCase, _LoopbackMixin):
    """
    Tests for L{OpenSSL.SSL.Connection} using a memory BIO.
    """
    def _server(self, sock):
        """
        Create a new server-side SSL L{Connection} object wrapped around
        C{sock}.
        """
        # Create the server side Connection.  This is mostly setup boilerplate
        # - use TLSv1, use a particular certificate, etc.
        server_ctx = Context(TLSv1_METHOD)
        server_ctx.set_options(OP_NO_SSLv2 | OP_NO_SSLv3 | OP_SINGLE_DH_USE )
        server_ctx.set_verify(VERIFY_PEER|VERIFY_FAIL_IF_NO_PEER_CERT|VERIFY_CLIENT_ONCE, verify_cb)
        server_store = server_ctx.get_cert_store()
        server_ctx.use_privatekey(load_privatekey(FILETYPE_PEM, server_key_pem))
        server_ctx.use_certificate(load_certificate(FILETYPE_PEM, server_cert_pem))
        server_ctx.check_privatekey()
        server_store.add_cert(load_certificate(FILETYPE_PEM, root_cert_pem))
        # Here the Connection is actually created.  If None is passed as the 2nd
        # parameter, it indicates a memory BIO should be created.
        server_conn = Connection(server_ctx, sock)
        server_conn.set_accept_state()
        return server_conn


    def _client(self, sock):
        """
        Create a new client-side SSL L{Connection} object wrapped around
        C{sock}.
        """
        # Now create the client side Connection.  Similar boilerplate to the
        # above.
        client_ctx = Context(TLSv1_METHOD)
        client_ctx.set_options(OP_NO_SSLv2 | OP_NO_SSLv3 | OP_SINGLE_DH_USE )
        client_ctx.set_verify(VERIFY_PEER|VERIFY_FAIL_IF_NO_PEER_CERT|VERIFY_CLIENT_ONCE, verify_cb)
        client_store = client_ctx.get_cert_store()
        client_ctx.use_privatekey(load_privatekey(FILETYPE_PEM, client_key_pem))
        client_ctx.use_certificate(load_certificate(FILETYPE_PEM, client_cert_pem))
        client_ctx.check_privatekey()
        client_store.add_cert(load_certificate(FILETYPE_PEM, root_cert_pem))
        client_conn = Connection(client_ctx, sock)
        client_conn.set_connect_state()
        return client_conn


    def test_memoryConnect(self):
        """
        Two L{Connection}s which use memory BIOs can be manually connected by
        reading from the output of each and writing those bytes to the input of
        the other and in this way establish a connection and exchange
        application-level bytes with each other.
        """
        server_conn = self._server(None)
        client_conn = self._client(None)

        # There should be no key or nonces yet.
        self.assertIdentical(server_conn.master_key(), None)
        self.assertIdentical(server_conn.client_random(), None)
        self.assertIdentical(server_conn.server_random(), None)

        # First, the handshake needs to happen.  We'll deliver bytes back and
        # forth between the client and server until neither of them feels like
        # speaking any more.
        self.assertIdentical(
            self._interactInMemory(client_conn, server_conn), None)

        # Now that the handshake is done, there should be a key and nonces.
        self.assertNotIdentical(server_conn.master_key(), None)
        self.assertNotIdentical(server_conn.client_random(), None)
        self.assertNotIdentical(server_conn.server_random(), None)
        self.assertEquals(server_conn.client_random(), client_conn.client_random())
        self.assertEquals(server_conn.server_random(), client_conn.server_random())
        self.assertNotEquals(server_conn.client_random(), server_conn.server_random())
        self.assertNotEquals(client_conn.client_random(), client_conn.server_random())

        # Here are the bytes we'll try to send.
        important_message = b('One if by land, two if by sea.')

        server_conn.write(important_message)
        self.assertEquals(
            self._interactInMemory(client_conn, server_conn),
            (client_conn, important_message))

        client_conn.write(important_message[::-1])
        self.assertEquals(
            self._interactInMemory(client_conn, server_conn),
            (server_conn, important_message[::-1]))


    def test_socketConnect(self):
        """
        Just like L{test_memoryConnect} but with an actual socket.

        This is primarily to rule out the memory BIO code as the source of
        any problems encountered while passing data over a L{Connection} (if
        this test fails, there must be a problem outside the memory BIO
        code, as no memory BIO is involved here).  Even though this isn't a
        memory BIO test, it's convenient to have it here.
        """
        server_conn, client_conn = self._loopback()

        important_message = b("Help me Obi Wan Kenobi, you're my only hope.")
        client_conn.send(important_message)
        msg = server_conn.recv(1024)
        self.assertEqual(msg, important_message)

        # Again in the other direction, just for fun.
        important_message = important_message[::-1]
        server_conn.send(important_message)
        msg = client_conn.recv(1024)
        self.assertEqual(msg, important_message)


    def test_socketOverridesMemory(self):
        """
        Test that L{OpenSSL.SSL.bio_read} and L{OpenSSL.SSL.bio_write} don't
        work on L{OpenSSL.SSL.Connection}() that use sockets.
        """
        context = Context(SSLv3_METHOD)
        client = socket()
        clientSSL = Connection(context, client)
        self.assertRaises( TypeError, clientSSL.bio_read, 100)
        self.assertRaises( TypeError, clientSSL.bio_write, "foo")
        self.assertRaises( TypeError, clientSSL.bio_shutdown )


    def test_outgoingOverflow(self):
        """
        If more bytes than can be written to the memory BIO are passed to
        L{Connection.send} at once, the number of bytes which were written is
        returned and that many bytes from the beginning of the input can be
        read from the other end of the connection.
        """
        server = self._server(None)
        client = self._client(None)

        self._interactInMemory(client, server)

        size = 2 ** 15
        sent = client.send("x" * size)
        # Sanity check.  We're trying to test what happens when the entire
        # input can't be sent.  If the entire input was sent, this test is
        # meaningless.
        self.assertTrue(sent < size)

        receiver, received = self._interactInMemory(client, server)
        self.assertIdentical(receiver, server)

        # We can rely on all of these bytes being received at once because
        # _loopback passes 2 ** 16 to recv - more than 2 ** 15.
        self.assertEquals(len(received), sent)


    def test_shutdown(self):
        """
        L{Connection.bio_shutdown} signals the end of the data stream from
        which the L{Connection} reads.
        """
        server = self._server(None)
        server.bio_shutdown()
        e = self.assertRaises(Error, server.recv, 1024)
        # We don't want WantReadError or ZeroReturnError or anything - it's a
        # handshake failure.
        self.assertEquals(e.__class__, Error)


    def _check_client_ca_list(self, func):
        """
        Verify the return value of the C{get_client_ca_list} method for server and client connections.

        @param func: A function which will be called with the server context
            before the client and server are connected to each other.  This
            function should specify a list of CAs for the server to send to the
            client and return that same list.  The list will be used to verify
            that C{get_client_ca_list} returns the proper value at various
            times.
        """
        server = self._server(None)
        client = self._client(None)
        self.assertEqual(client.get_client_ca_list(), [])
        self.assertEqual(server.get_client_ca_list(), [])
        ctx = server.get_context()
        expected = func(ctx)
        self.assertEqual(client.get_client_ca_list(), [])
        self.assertEqual(server.get_client_ca_list(), expected)
        self._interactInMemory(client, server)
        self.assertEqual(client.get_client_ca_list(), expected)
        self.assertEqual(server.get_client_ca_list(), expected)


    def test_set_client_ca_list_errors(self):
        """
        L{Context.set_client_ca_list} raises a L{TypeError} if called with a
        non-list or a list that contains objects other than X509Names.
        """
        ctx = Context(TLSv1_METHOD)
        self.assertRaises(TypeError, ctx.set_client_ca_list, "spam")
        self.assertRaises(TypeError, ctx.set_client_ca_list, ["spam"])
        self.assertIdentical(ctx.set_client_ca_list([]), None)


    def test_set_empty_ca_list(self):
        """
        If passed an empty list, L{Context.set_client_ca_list} configures the
        context to send no CA names to the client and, on both the server and
        client sides, L{Connection.get_client_ca_list} returns an empty list
        after the connection is set up.
        """
        def no_ca(ctx):
            ctx.set_client_ca_list([])
            return []
        self._check_client_ca_list(no_ca)


    def test_set_one_ca_list(self):
        """
        If passed a list containing a single X509Name,
        L{Context.set_client_ca_list} configures the context to send that CA
        name to the client and, on both the server and client sides,
        L{Connection.get_client_ca_list} returns a list containing that
        X509Name after the connection is set up.
        """
        cacert = load_certificate(FILETYPE_PEM, root_cert_pem)
        cadesc = cacert.get_subject()
        def single_ca(ctx):
            ctx.set_client_ca_list([cadesc])
            return [cadesc]
        self._check_client_ca_list(single_ca)


    def test_set_multiple_ca_list(self):
        """
        If passed a list containing multiple X509Name objects,
        L{Context.set_client_ca_list} configures the context to send those CA
        names to the client and, on both the server and client sides,
        L{Connection.get_client_ca_list} returns a list containing those
        X509Names after the connection is set up.
        """
        secert = load_certificate(FILETYPE_PEM, server_cert_pem)
        clcert = load_certificate(FILETYPE_PEM, server_cert_pem)

        sedesc = secert.get_subject()
        cldesc = clcert.get_subject()

        def multiple_ca(ctx):
            L = [sedesc, cldesc]
            ctx.set_client_ca_list(L)
            return L
        self._check_client_ca_list(multiple_ca)


    def test_reset_ca_list(self):
        """
        If called multiple times, only the X509Names passed to the final call
        of L{Context.set_client_ca_list} are used to configure the CA names
        sent to the client.
        """
        cacert = load_certificate(FILETYPE_PEM, root_cert_pem)
        secert = load_certificate(FILETYPE_PEM, server_cert_pem)
        clcert = load_certificate(FILETYPE_PEM, server_cert_pem)

        cadesc = cacert.get_subject()
        sedesc = secert.get_subject()
        cldesc = clcert.get_subject()

        def changed_ca(ctx):
            ctx.set_client_ca_list([sedesc, cldesc])
            ctx.set_client_ca_list([cadesc])
            return [cadesc]
        self._check_client_ca_list(changed_ca)


    def test_mutated_ca_list(self):
        """
        If the list passed to L{Context.set_client_ca_list} is mutated
        afterwards, this does not affect the list of CA names sent to the
        client.
        """
        cacert = load_certificate(FILETYPE_PEM, root_cert_pem)
        secert = load_certificate(FILETYPE_PEM, server_cert_pem)

        cadesc = cacert.get_subject()
        sedesc = secert.get_subject()

        def mutated_ca(ctx):
            L = [cadesc]
            ctx.set_client_ca_list([cadesc])
            L.append(sedesc)
            return [cadesc]
        self._check_client_ca_list(mutated_ca)


    def test_add_client_ca_errors(self):
        """
        L{Context.add_client_ca} raises L{TypeError} if called with a non-X509
        object or with a number of arguments other than one.
        """
        ctx = Context(TLSv1_METHOD)
        cacert = load_certificate(FILETYPE_PEM, root_cert_pem)
        self.assertRaises(TypeError, ctx.add_client_ca)
        self.assertRaises(TypeError, ctx.add_client_ca, "spam")
        self.assertRaises(TypeError, ctx.add_client_ca, cacert, cacert)


    def test_one_add_client_ca(self):
        """
        A certificate's subject can be added as a CA to be sent to the client
        with L{Context.add_client_ca}.
        """
        cacert = load_certificate(FILETYPE_PEM, root_cert_pem)
        cadesc = cacert.get_subject()
        def single_ca(ctx):
            ctx.add_client_ca(cacert)
            return [cadesc]
        self._check_client_ca_list(single_ca)


    def test_multiple_add_client_ca(self):
        """
        Multiple CA names can be sent to the client by calling
        L{Context.add_client_ca} with multiple X509 objects.
        """
        cacert = load_certificate(FILETYPE_PEM, root_cert_pem)
        secert = load_certificate(FILETYPE_PEM, server_cert_pem)

        cadesc = cacert.get_subject()
        sedesc = secert.get_subject()

        def multiple_ca(ctx):
            ctx.add_client_ca(cacert)
            ctx.add_client_ca(secert)
            return [cadesc, sedesc]
        self._check_client_ca_list(multiple_ca)


    def test_set_and_add_client_ca(self):
        """
        A call to L{Context.set_client_ca_list} followed by a call to
        L{Context.add_client_ca} results in using the CA names from the first
        call and the CA name from the second call.
        """
        cacert = load_certificate(FILETYPE_PEM, root_cert_pem)
        secert = load_certificate(FILETYPE_PEM, server_cert_pem)
        clcert = load_certificate(FILETYPE_PEM, server_cert_pem)

        cadesc = cacert.get_subject()
        sedesc = secert.get_subject()
        cldesc = clcert.get_subject()

        def mixed_set_add_ca(ctx):
            ctx.set_client_ca_list([cadesc, sedesc])
            ctx.add_client_ca(clcert)
            return [cadesc, sedesc, cldesc]
        self._check_client_ca_list(mixed_set_add_ca)


    def test_set_after_add_client_ca(self):
        """
        A call to L{Context.set_client_ca_list} after a call to
        L{Context.add_client_ca} replaces the CA name specified by the former
        call with the names specified by the latter cal.
        """
        cacert = load_certificate(FILETYPE_PEM, root_cert_pem)
        secert = load_certificate(FILETYPE_PEM, server_cert_pem)
        clcert = load_certificate(FILETYPE_PEM, server_cert_pem)

        cadesc = cacert.get_subject()
        sedesc = secert.get_subject()

        def set_replaces_add_ca(ctx):
            ctx.add_client_ca(clcert)
            ctx.set_client_ca_list([cadesc])
            ctx.add_client_ca(secert)
            return [cadesc, sedesc]
        self._check_client_ca_list(set_replaces_add_ca)



if __name__ == '__main__':
    main()

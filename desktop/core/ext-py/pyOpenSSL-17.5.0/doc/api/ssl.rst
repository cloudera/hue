.. _openssl-ssl:

:py:mod:`SSL` --- An interface to the SSL-specific parts of OpenSSL
===================================================================

.. py:module:: OpenSSL.SSL
    :synopsis: An interface to the SSL-specific parts of OpenSSL


This module handles things specific to SSL. There are two objects defined:
Context, Connection.

.. py:data:: SSLv2_METHOD
             SSLv3_METHOD
             SSLv23_METHOD
             TLSv1_METHOD
             TLSv1_1_METHOD
             TLSv1_2_METHOD

    These constants represent the different SSL methods to use when creating a
    context object.  If the underlying OpenSSL build is missing support for any
    of these protocols, constructing a :py:class:`Context` using the
    corresponding :py:const:`*_METHOD` will raise an exception.


.. py:data:: VERIFY_NONE
             VERIFY_PEER
             VERIFY_FAIL_IF_NO_PEER_CERT

    These constants represent the verification mode used by the Context
    object's :py:meth:`set_verify` method.


.. py:data:: FILETYPE_PEM
             FILETYPE_ASN1

    File type constants used with the :py:meth:`use_certificate_file` and
    :py:meth:`use_privatekey_file` methods of Context objects.


.. py:data:: OP_SINGLE_DH_USE
             OP_SINGLE_ECDH_USE

    Constants used with :py:meth:`set_options` of Context objects.

    When these options are used, a new key will always be created when using
    ephemeral (Elliptic curve) Diffie-Hellman.


.. py:data:: OP_EPHEMERAL_RSA

    Constant used with :py:meth:`set_options` of Context objects.

    When this option is used, ephemeral RSA keys will always be used when doing
    RSA operations.


.. py:data:: OP_NO_TICKET

    Constant used with :py:meth:`set_options` of Context objects.

    When this option is used, the session ticket extension will not be used.


.. py:data:: OP_NO_COMPRESSION

    Constant used with :py:meth:`set_options` of Context objects.

    When this option is used, compression will not be used.


.. py:data:: OP_NO_SSLv2
             OP_NO_SSLv3
             OP_NO_TLSv1
             OP_NO_TLSv1_1
             OP_NO_TLSv1_2

    Constants used with :py:meth:`set_options` of Context objects.

    Each of these options disables one version of the SSL/TLS protocol.  This
    is interesting if you're using e.g. :py:const:`SSLv23_METHOD` to get an
    SSLv2-compatible handshake, but don't want to use SSLv2.  If the underlying
    OpenSSL build is missing support for any of these protocols, the
    :py:const:`OP_NO_*` constant may be undefined.


.. py:data:: SSLEAY_VERSION
             SSLEAY_CFLAGS
             SSLEAY_BUILT_ON
             SSLEAY_PLATFORM
             SSLEAY_DIR

    Constants used with :py:meth:`SSLeay_version` to specify what OpenSSL version
    information to retrieve.  See the man page for the :py:func:`SSLeay_version` C
    API for details.


.. py:data:: SESS_CACHE_OFF
             SESS_CACHE_CLIENT
             SESS_CACHE_SERVER
             SESS_CACHE_BOTH
             SESS_CACHE_NO_AUTO_CLEAR
             SESS_CACHE_NO_INTERNAL_LOOKUP
             SESS_CACHE_NO_INTERNAL_STORE
             SESS_CACHE_NO_INTERNAL

     Constants used with :py:meth:`Context.set_session_cache_mode` to specify
     the behavior of the session cache and potential session reuse.  See the man
     page for the :py:func:`SSL_CTX_set_session_cache_mode` C API for details.

     .. versionadded:: 0.14


.. py:data:: OPENSSL_VERSION_NUMBER

    An integer giving the version number of the OpenSSL library used to build this
    version of pyOpenSSL.  See the man page for the :py:func:`SSLeay_version` C API
    for details.


.. py:function:: SSLeay_version(type)

    Retrieve a string describing some aspect of the underlying OpenSSL version.  The
    type passed in should be one of the :py:const:`SSLEAY_*` constants defined in
    this module.


.. py:data:: ContextType

    See :py:class:`Context`.


.. py:class:: Context(method)

    A class representing SSL contexts.  Contexts define the parameters of one or
    more SSL connections.

    *method* should be :py:const:`SSLv2_METHOD`, :py:const:`SSLv3_METHOD`,
    :py:const:`SSLv23_METHOD`, :py:const:`TLSv1_METHOD`, :py:const:`TLSv1_1_METHOD`,
    or :py:const:`TLSv1_2_METHOD`.


.. py:class:: Session()

    A class representing an SSL session.  A session defines certain connection
    parameters which may be re-used to speed up the setup of subsequent
    connections.

    .. versionadded:: 0.14


.. py:data:: ConnectionType

    See :py:class:`Connection`.


.. py:class:: Connection(context, socket)

    A class representing SSL connections.

    *context* should be an instance of :py:class:`Context` and *socket*
    should be a socket [#connection-context-socket]_  object.  *socket* may be
    *None*; in this case, the Connection is created with a memory BIO: see
    the :py:meth:`bio_read`, :py:meth:`bio_write`, and :py:meth:`bio_shutdown`
    methods.

.. py:exception:: Error

    This exception is used as a base class for the other SSL-related
    exceptions, but may also be raised directly.

    Whenever this exception is raised directly, it has a list of error messages
    from the OpenSSL error queue, where each item is a tuple *(lib, function,
    reason)*. Here *lib*, *function* and *reason* are all strings, describing
    where and what the problem is. See :manpage:`err(3)` for more information.


.. py:exception:: ZeroReturnError

    This exception matches the error return code
    :py:data:`SSL_ERROR_ZERO_RETURN`, and is raised when the SSL Connection has
    been closed. In SSL 3.0 and TLS 1.0, this only occurs if a closure alert has
    occurred in the protocol, i.e.  the connection has been closed cleanly. Note
    that this does not necessarily mean that the transport layer (e.g. a socket)
    has been closed.

    It may seem a little strange that this is an exception, but it does match an
    :py:data:`SSL_ERROR` code, and is very convenient.


.. py:exception:: WantReadError

    The operation did not complete; the same I/O method should be called again
    later, with the same arguments. Any I/O method can lead to this since new
    handshakes can occur at any time.

    The wanted read is for **dirty** data sent over the network, not the
    **clean** data inside the tunnel.  For a socket based SSL connection,
    **read** means data coming at us over the network.  Until that read
    succeeds, the attempted :py:meth:`OpenSSL.SSL.Connection.recv`,
    :py:meth:`OpenSSL.SSL.Connection.send`, or
    :py:meth:`OpenSSL.SSL.Connection.do_handshake` is prevented or incomplete. You
    probably want to :py:meth:`select()` on the socket before trying again.


.. py:exception:: WantWriteError

    See :py:exc:`WantReadError`.  The socket send buffer may be too full to
    write more data.


.. py:exception:: WantX509LookupError

    The operation did not complete because an application callback has asked to be
    called again. The I/O method should be called again later, with the same
    arguments.

    .. note:: This won't occur in this version, as there are no such
        callbacks in this version.


.. py:exception:: SysCallError

    The :py:exc:`SysCallError` occurs when there's an I/O error and OpenSSL's
    error queue does not contain any information. This can mean two things: An
    error in the transport protocol, or an end of file that violates the protocol.
    The parameter to the exception is always a pair *(errnum,
    errstr)*.



.. _openssl-context:

Context objects
---------------

Context objects have the following methods:

.. :py:class:: OpenSSL.SSL.Context

.. py:method:: Context.check_privatekey()

    Check if the private key (loaded with :py:meth:`use_privatekey`) matches the
    certificate (loaded with :py:meth:`use_certificate`).  Returns
    :py:data:`None` if they match, raises :py:exc:`Error` otherwise.


.. py:method:: Context.get_app_data()

    Retrieve application data as set by :py:meth:`set_app_data`.


.. py:method:: Context.get_cert_store()

    Retrieve the certificate store (a X509Store object) that the context uses.
    This can be used to add "trusted" certificates without using the
    :py:meth:`load_verify_locations` method.


.. py:method:: Context.get_timeout()

    Retrieve session timeout, as set by :py:meth:`set_timeout`. The default is 300
    seconds.


.. py:method:: Context.get_verify_depth()

    Retrieve the Context object's verify depth, as set by
    :py:meth:`set_verify_depth`.


.. py:method:: Context.get_verify_mode()

    Retrieve the Context object's verify mode, as set by :py:meth:`set_verify`.


.. automethod:: Context.load_client_ca


.. py:method:: Context.set_client_ca_list(certificate_authorities)

    Replace the current list of preferred certificate signers that would be
    sent to the client when requesting a client certificate with the
    *certificate_authorities* sequence of :py:class:`OpenSSL.crypto.X509Name`'s.

    .. versionadded:: 0.10


.. py:method:: Context.add_client_ca(certificate_authority)

    Extract a :py:class:`OpenSSL.crypto.X509Name` from the *certificate_authority*
    :py:class:`OpenSSL.crypto.X509` certificate and add it to the list of preferred
    certificate signers sent to the client when requesting a client certificate.

    .. versionadded:: 0.10


.. py:method:: Context.load_verify_locations(pemfile, capath)

    Specify where CA certificates for verification purposes are located. These
    are trusted certificates. Note that the certificates have to be in PEM
    format.  If capath is passed, it must be a directory prepared using the
    ``c_rehash`` tool included with OpenSSL.  Either, but not both, of
    *pemfile* or *capath* may be :py:data:`None`.


.. py:method:: Context.set_default_verify_paths()

    Specify that the platform provided CA certificates are to be used for verification purposes.
    This method has some caveats related to the binary wheels that cryptography (pyOpenSSL's primary dependency) ships:

    * macOS will only load certificates using this method if the user has the ``openssl@1.1`` `Homebrew <https://brew.sh>`_ formula installed in the default location.
    * Windows will not work.
    * manylinux1 cryptography wheels will work on most common Linux distributions in pyOpenSSL 17.1.0 and above.
      pyOpenSSL detects the manylinux1 wheel and attempts to load roots via a fallback path.


.. py:method:: Context.load_tmp_dh(dhfile)

    Load parameters for Ephemeral Diffie-Hellman from *dhfile*.


.. py:method:: Context.set_tmp_ecdh(curve)

   Select a curve to use for ECDHE key exchange.

   The valid values of *curve* are the objects returned by
   :py:func:`OpenSSL.crypto.get_elliptic_curves` or
   :py:func:`OpenSSL.crypto.get_elliptic_curve`.


.. py:method:: Context.set_app_data(data)

    Associate *data* with this Context object. *data* can be retrieved
    later using the :py:meth:`get_app_data` method.


.. automethod:: Context.set_cipher_list

.. py:method:: Context.set_info_callback(callback)

    Set the information callback to *callback*. This function will be called
    from time to time during SSL handshakes.

    *callback* should take three arguments: a Connection object and two integers.
    The first integer specifies where in the SSL handshake the function was
    called, and the other the return code from a (possibly failed) internal
    function call.


.. py:method:: Context.set_options(options)

    Add SSL options. Options you have set before are not cleared!
    This method should be used with the :py:const:`OP_*` constants.


.. py:method:: Context.set_mode(mode)

   Add SSL mode. Modes you have set before are not cleared!  This method should
   be used with the :py:const:`MODE_*` constants.


.. py:method:: Context.set_passwd_cb(callback[, userdata])

    Set the passphrase callback to *callback*. This function will be called
    when a private key with a passphrase is loaded. *callback* must accept
    three positional arguments.  First, an integer giving the maximum length of
    the passphrase it may return.  If the returned passphrase is longer than
    this, it will be truncated.  Second, a boolean value which will be true if
    the user should be prompted for the passphrase twice and the callback should
    verify that the two values supplied are equal. Third, the value given as the
    *userdata* parameter to :py:meth:`set_passwd_cb`.  The *callback* must return
    a byte string. If an error occurs, *callback* should return a false value
    (e.g. an empty string).


.. py:method:: Context.set_session_cache_mode(mode)

    Set the behavior of the session cache used by all connections using this
    Context.  The previously set mode is returned.  See :py:const:`SESS_CACHE_*`
    for details about particular modes.

    .. versionadded:: 0.14


.. py:method:: Context.get_session_cache_mode()

    Get the current session cache mode.

    .. versionadded:: 0.14


.. automethod:: Context.set_session_id


.. py:method:: Context.set_timeout(timeout)

    Set the timeout for newly created sessions for this Context object to
    *timeout*. *timeout* must be given in (whole) seconds. The default
    value is 300 seconds. See the OpenSSL manual for more information (e.g.
    :manpage:`SSL_CTX_set_timeout(3)`).


.. py:method:: Context.set_verify(mode, callback)

    Set the verification flags for this Context object to *mode* and specify
    that *callback* should be used for verification callbacks. *mode* should be
    one of :py:const:`VERIFY_NONE` and :py:const:`VERIFY_PEER`. If
    :py:const:`VERIFY_PEER` is used, *mode* can be OR:ed with
    :py:const:`VERIFY_FAIL_IF_NO_PEER_CERT` and :py:const:`VERIFY_CLIENT_ONCE`
    to further control the behaviour.

    *callback* should take five arguments: A Connection object, an X509 object,
    and three integer variables, which are in turn potential error number, error
    depth and return code. *callback* should return true if verification passes
    and false otherwise.


.. py:method:: Context.set_verify_depth(depth)

    Set the maximum depth for the certificate chain verification that shall be
    allowed for this Context object.


.. py:method:: Context.use_certificate(cert)

    Use the certificate *cert* which has to be a X509 object.


.. py:method:: Context.add_extra_chain_cert(cert)

    Adds the certificate *cert*, which has to be a X509 object, to the
    certificate chain presented together with the certificate.


.. py:method:: Context.use_certificate_chain_file(file)

    Load a certificate chain from *file* which must be PEM encoded.


.. py:method:: Context.use_privatekey(pkey)

    Use the private key *pkey* which has to be a PKey object.


.. py:method:: Context.use_certificate_file(file[, format])

    Load the first certificate found in *file*. The certificate must be in the
    format specified by *format*, which is either :py:const:`FILETYPE_PEM` or
    :py:const:`FILETYPE_ASN1`. The default is :py:const:`FILETYPE_PEM`.


.. py:method:: Context.use_privatekey_file(file[, format])

    Load the first private key found in *file*. The private key must be in the
    format specified by *format*, which is either :py:const:`FILETYPE_PEM` or
    :py:const:`FILETYPE_ASN1`. The default is :py:const:`FILETYPE_PEM`.


.. py:method:: Context.set_tlsext_servername_callback(callback)

    Specify a one-argument callable to use as the TLS extension server name
    callback.  When a connection using the server name extension is made using
    this context, the callback will be invoked with the :py:class:`Connection`
    instance.

    .. versionadded:: 0.13


.. py:method:: Context.set_npn_advertise_callback(callback)

    Specify a callback function that will be called when offering `Next
    Protocol Negotiation
    <https://tools.ietf.org/html/draft-agl-tls-nextprotoneg-03>`_ as a server.

    *callback* should be the callback function.  It will be invoked with one
    argument, the :py:class:`Connection` instance.  It should return a list of
    bytestrings representing the advertised protocols, like
    ``[b'http/1.1', b'spdy/2']``.

    .. versionadded:: 0.15


.. py:method:: Context.set_npn_select_callback(callback):

    Specify a callback function that will be called when a server offers Next
    Protocol Negotiation options.

    *callback* should be the callback function.  It will be invoked with two
    arguments: the :py:class:`Connection`, and a list of offered protocols as
    bytestrings, e.g. ``[b'http/1.1', b'spdy/2']``.  It should return one of
    those bytestrings, the chosen protocol.

    .. versionadded:: 0.15

.. py:method:: Context.set_alpn_protos(protos)

    Specify the protocols that the client is prepared to speak after the TLS
    connection has been negotiated using Application Layer Protocol
    Negotiation.

    *protos* should be a list of protocols that the client is offering, each
    as a bytestring. For example, ``[b'http/1.1', b'spdy/2']``.


.. py:method:: Context.set_alpn_select_callback(callback)

    Specify a callback function that will be called on the server when a client
    offers protocols using Application Layer Protocol Negotiation.

    *callback* should be the callback function. It will be invoked with two
    arguments: the :py:class:`Connection` and a list of offered protocols as
    bytestrings, e.g. ``[b'http/1.1', b'spdy/2']``. It should return one of
    these bytestrings, the chosen protocol.


.. _openssl-session:

Session objects
---------------

Session objects have no methods.


.. _openssl-connection:

Connection objects
------------------

Connection objects have the following methods:

.. py:method:: Connection.accept()

    Call the :py:meth:`accept` method of the underlying socket and set up SSL on the
    returned socket, using the Context object supplied to this Connection object at
    creation. Returns a pair *(conn, address)*. where *conn* is the new
    Connection object created, and *address* is as returned by the socket's
    :py:meth:`accept`.


.. py:method:: Connection.bind(address)

    Call the :py:meth:`bind` method of the underlying socket.


.. py:method:: Connection.close()

    Call the :py:meth:`close` method of the underlying socket. Note: If you want
    correct SSL closure, you need to call the :py:meth:`shutdown` method first.


.. py:method:: Connection.connect(address)

    Call the :py:meth:`connect` method of the underlying socket and set up SSL on the
    socket, using the Context object supplied to this Connection object at
    creation.


.. py:method:: Connection.connect_ex(address)

    Call the :py:meth:`connect_ex` method of the underlying socket and set up SSL on
    the socket, using the Context object supplied to this Connection object at
    creation. Note that if the :py:meth:`connect_ex` method of the socket doesn't
    return 0, SSL won't be initialized.


.. py:method:: Connection.do_handshake()

    Perform an SSL handshake (usually called after :py:meth:`renegotiate` or one of
    :py:meth:`set_accept_state` or :py:meth:`set_accept_state`). This can raise the
    same exceptions as :py:meth:`send` and :py:meth:`recv`.


.. py:method:: Connection.fileno()

    Retrieve the file descriptor number for the underlying socket.


.. py:method:: Connection.listen(backlog)

    Call the :py:meth:`listen` method of the underlying socket.


.. py:method:: Connection.get_app_data()

    Retrieve application data as set by :py:meth:`set_app_data`.


.. automethod:: Connection.get_cipher_list


.. py:method:: Connection.get_protocol_version()

    Retrieve the version of the SSL or TLS protocol used by the Connection.
    For example, it will return ``0x769`` for connections made over TLS
    version 1.


.. py:method:: Connection.get_protocol_version_name()

    Retrieve the version of the SSL or TLS protocol used by the Connection as
    a unicode string. For example, it will return ``TLSv1`` for connections
    made over TLS version 1, or ``Unknown`` for connections that were not
    successfully established.


.. py:method:: Connection.get_client_ca_list()

    Retrieve the list of preferred client certificate issuers sent by the server
    as :py:class:`OpenSSL.crypto.X509Name` objects.

    If this is a client :py:class:`Connection`, the list will be empty until the
    connection with the server is established.

    If this is a server :py:class:`Connection`, return the list of certificate
    authorities that will be sent or has been sent to the client, as controlled
    by this :py:class:`Connection`'s :py:class:`Context`.

    .. versionadded:: 0.10


.. py:method:: Connection.get_context()

    Retrieve the Context object associated with this Connection.


.. py:method:: Connection.set_context(context)

    Specify a replacement Context object for this Connection.


.. py:method:: Connection.get_peer_certificate()

    Retrieve the other side's certificate (if any)


.. py:method:: Connection.get_peer_cert_chain()

    Retrieve the tuple of the other side's certificate chain (if any)


.. py:method:: Connection.getpeername()

    Call the :py:meth:`getpeername` method of the underlying socket.


.. py:method:: Connection.getsockname()

    Call the :py:meth:`getsockname` method of the underlying socket.


.. py:method:: Connection.getsockopt(level, optname[, buflen])

    Call the :py:meth:`getsockopt` method of the underlying socket.


.. py:method:: Connection.pending()

    Retrieve the number of bytes that can be safely read from the SSL buffer
    (**not** the underlying transport buffer).


.. py:method:: Connection.recv(bufsize[, flags])

    Receive data from the Connection. The return value is a string representing the
    data received. The maximum amount of data to be received at once, is specified
    by *bufsize*. The only supported flag is ``MSG_PEEK``, all other flags are
    ignored.


.. py:method:: Connection.recv_into(buffer[, nbytes[, flags]])

    Receive data from the Connection and copy it directly into the provided
    buffer. The return value is the number of bytes read from the connection.
    The maximum amount of data to be received at once is specified by *nbytes*.
    The only supported flag is ``MSG_PEEK``, all other flags are ignored.

.. py:method:: Connection.bio_write(bytes)

    If the Connection was created with a memory BIO, this method can be used to add
    bytes to the read end of that memory BIO.  The Connection can then read the
    bytes (for example, in response to a call to :py:meth:`recv`).


.. automethod:: Connection.renegotiate

.. automethod:: Connection.renegotiate_pending

.. automethod:: Connection.total_renegotiations

.. py:method:: Connection.send(string)

    Send the *string* data to the Connection.


.. py:method:: Connection.bio_read(bufsize)

    If the Connection was created with a memory BIO, this method can be used to
    read bytes from the write end of that memory BIO.  Many Connection methods will
    add bytes which must be read in this manner or the buffer will eventually fill
    up and the Connection will be able to take no further actions.


.. py:method:: Connection.sendall(string)

    Send all of the *string* data to the Connection. This calls :py:meth:`send`
    repeatedly until all data is sent. If an error occurs, it's impossible to tell
    how much data has been sent.


.. py:method:: Connection.set_accept_state()

    Set the connection to work in server mode. The handshake will be handled
    automatically by read/write.


.. py:method:: Connection.set_app_data(data)

    Associate *data* with this Connection object. *data* can be retrieved
    later using the :py:meth:`get_app_data` method.


.. py:method:: Connection.set_connect_state()

    Set the connection to work in client mode. The handshake will be handled
    automatically by read/write.


.. py:method:: Connection.setblocking(flag)

    Call the :py:meth:`setblocking` method of the underlying socket.


.. py:method:: Connection.setsockopt(level, optname, value)

    Call the :py:meth:`setsockopt` method of the underlying socket.


.. py:method:: Connection.shutdown()

    Send the shutdown message to the Connection. Returns true if the shutdown
    message exchange is completed and false otherwise (in which case you call
    :py:meth:`recv` or :py:meth:`send` when the connection becomes
    readable/writeable.


.. py:method:: Connection.get_shutdown()

    Get the shutdown state of the Connection.  Returns a bitvector of either or
    both of *SENT_SHUTDOWN* and *RECEIVED_SHUTDOWN*.


.. py:method:: Connection.set_shutdown(state)

    Set the shutdown state of the Connection.  *state* is a bitvector of
    either or both of *SENT_SHUTDOWN* and *RECEIVED_SHUTDOWN*.


.. py:method:: Connection.sock_shutdown(how)

    Call the :py:meth:`shutdown` method of the underlying socket.


.. py:method:: Connection.bio_shutdown()

    If the Connection was created with a memory BIO, this method can be used to
    indicate that *end of file* has been reached on the read end of that memory
    BIO.


.. automethod:: Connection.get_state_string

.. py:method:: Connection.client_random()

    Retrieve the random value used with the client hello message.


.. py:method:: Connection.server_random()

    Retrieve the random value used with the server hello message.


.. py:method:: Connection.master_key()

    Retrieve the value of the master key for this session.


.. py:method:: Connection.want_read()

    Checks if more data has to be read from the transport layer to complete an
    operation.


.. py:method:: Connection.want_write()

    Checks if there is data to write to the transport layer to complete an
    operation.


.. py:method:: Connection.set_tlsext_host_name(name)

    Specify the byte string to send as the server name in the client hello message.

    .. versionadded:: 0.13


.. py:method:: Connection.get_servername()

    Get the value of the server name received in the client hello message.

    .. versionadded:: 0.13


.. py:method:: Connection.get_session()

    Get a :py:class:`Session` instance representing the SSL session in use by
    the connection, or :py:obj:`None` if there is no session.

    .. versionadded:: 0.14


.. py:method:: Connection.set_session(session)

    Set a new SSL session (using a :py:class:`Session` instance) to be used by
    the connection.

    .. versionadded:: 0.14


.. py:method:: Connection.get_finished()

    Obtain latest TLS Finished message that we sent, or :py:obj:`None` if
    handshake is not completed.

    .. versionadded:: 0.15


.. py:method:: Connection.get_peer_finished()

    Obtain latest TLS Finished message that we expected from peer, or
    :py:obj:`None` if handshake is not completed.

    .. versionadded:: 0.15


.. py:method:: Connection.get_cipher_name()

    Obtain the name of the currently used cipher.

    .. versionadded:: 0.15


.. py:method:: Connection.get_cipher_bits()

    Obtain the number of secret bits of the currently used cipher.

    .. versionadded:: 0.15


.. py:method:: Connection.get_cipher_version()

    Obtain the protocol name of the currently used cipher.

    .. versionadded:: 0.15


.. py:method:: Connection.get_next_proto_negotiated():

    Get the protocol that was negotiated by Next Protocol Negotiation. Returns
    a bytestring of the protocol name. If no protocol has been negotiated yet,
    returns an empty string.

    .. versionadded:: 0.15

.. py:method:: Connection.set_alpn_protos(protos)

    Specify the protocols that the client is prepared to speak after the TLS
    connection has been negotiated using Application Layer Protocol
    Negotiation.

    *protos* should be a list of protocols that the client is offering, each
    as a bytestring. For example, ``[b'http/1.1', b'spdy/2']``.


.. py:method:: Connection.get_alpn_proto_negotiated()

    Get the protocol that was negotiated by Application Layer Protocol
    Negotiation. Returns a bytestring of the protocol name. If no protocol has
    been negotiated yet, returns an empty string.


.. Rubric:: Footnotes

.. [#connection-context-socket] Actually, all that is required is an object that
    **behaves** like a socket, you could even use files, even though it'd be
    tricky to get the handshakes right!

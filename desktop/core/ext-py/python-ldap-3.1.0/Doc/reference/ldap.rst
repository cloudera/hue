********************************************
:py:mod:`ldap` LDAP library interface module
********************************************

.. py:module:: ldap
    :platform: Posix, Windows
    :synopsis: Access to an underlying LDAP C library.
.. moduleauthor:: python-ldap project (see https://www.python-ldap.org/)


This module provides access to the LDAP (Lightweight Directory Access Protocol)
C API implemented in OpenLDAP.  It is similar to the C API, with
the notable differences that lists are manipulated via Python list operations
and errors appear as exceptions.

   .. seealso::

      For more detailed information on the C interface, please see the (expired)
      `draft-ietf-ldapext-ldap-c-api <https://tools.ietf.org/html/draft-ietf-ldapext-ldap-c-api>`_


This documentation is current for the Python LDAP module, version
|release|.  Source and binaries are available from
https://www.python-ldap.org/.


Functions
=========

This module defines the following functions:

.. py:function:: initialize(uri [, trace_level=0 [, trace_file=sys.stdout [, trace_stack_limit=None, [bytes_mode=None, [bytes_strictness=None]]]]]) -> LDAPObject object

   Initializes a new connection object for accessing the given LDAP server,
   and return an LDAP object (see :ref:`ldap-objects`) used to perform operations
   on that server.

   The *uri* parameter may be a comma- or whitespace-separated list of URIs
   containing only the schema, the host, and the port fields. Note that
   when using multiple URIs you cannot determine to which URI your client
   gets connected.

   Note that internally the OpenLDAP function
   `ldap_initialize(3) <https://www.openldap.org/software/man.cgi?query=ldap_init&sektion=3>`_
   is called which just initializes the LDAP connection struct in the C API
   - nothing else. Therefore the first call to an operation method (bind,
   search etc.) then really opens the connection (lazy connect). Before
   that nothing is sent on the wire. The error handling in the calling
   application has to correctly handle this behaviour.

   Three optional arguments are for generating debug log information:
   *trace_level* specifies the amount of information being logged,
   *trace_file* specifies a file-like object as target of the debug log and
   *trace_stack_limit* specifies the stack limit of tracebacks in debug log.

   The *bytes_mode* and *bytes_strictness* arguments specify text/bytes
   behavior under Python 2.
   See :ref:`text-bytes` for a complete documentation.

   Possible values for *trace_level* are
   :py:const:`0` for no logging,
   :py:const:`1` for only logging the method calls with arguments,
   :py:const:`2` for logging the method calls with arguments and the complete results and
   :py:const:`9` for also logging the traceback of method calls.

   .. seealso::

      :rfc:`4516` - Lightweight Directory Access Protocol (LDAP): Uniform Resource Locator


.. py:function:: get_option(option) -> int|string

   This function returns the value of the global option specified by *option*.


.. py:function:: set_option(option, invalue) -> None

   This function sets the value of the global option specified by *option* to
   *invalue*.

.. versionchanged:: 3.1

   The deprecated functions ``ldap.init()`` and ``ldap.open()`` were removed.


.. _ldap-constants:

Constants
=========

The module defines various constants. Note that some constants depend
on the build options and which underlying libs were used or even on
the version of the libs. So before using those constants the application has
to explicitly check whether they are available.

General
-------

.. py:data:: PORT

   The assigned TCP port number (389) that LDAP servers listen on.

.. py:data:: SASL_AVAIL

   Integer where a non-zero value indicates that python-ldap was built with
   support for SASL (Cyrus-SASL).

.. py:data:: TLS_AVAIL

   Integer where a non-zero value indicates that python-ldap was built with
   support for SSL/TLS (OpenSSL or similar libs).


.. _ldap-options:

Options
-------

.. seealso::

   :manpage:`ldap.conf(5)` and :manpage:`ldap_get_option(3)`


For use with functions :py:func:set_option() and :py:func:get_option()
and methods :py:method:LDAPObject.set_option() and :py:method:LDAPObject.get_option() the
following option identifiers are defined as constants:

.. py:data:: OPT_API_FEATURE_INFO

.. py:data:: OPT_API_INFO

.. py:data:: OPT_CLIENT_CONTROLS

.. py:data:: OPT_DEBUG_LEVEL

   Sets the debug level within the underlying OpenLDAP C lib (libldap).
   libldap sends the log messages to stderr.

.. py:data:: OPT_DEFBASE

.. py:data:: OPT_DEREF

   Specifies how alias dereferencing is done within the underlying LDAP C lib.

.. py:data:: OPT_ERROR_STRING

.. py:data:: OPT_DIAGNOSTIC_MESSAGE

.. py:data:: OPT_HOST_NAME

.. py:data:: OPT_MATCHED_DN

.. py:data:: OPT_NETWORK_TIMEOUT

   .. versionchanged:: 3.0
      A timeout of ``-1`` or ``None`` resets timeout to infinity.

.. py:data:: OPT_PROTOCOL_VERSION

   Sets the LDAP protocol version used for a connection. This is mapped to
   object attribute `ldap.LDAPObject.protocol_version`

.. py:data:: OPT_REFERRALS

   int specifying whether referrals should be automatically chased within
   the underlying LDAP C lib.

.. py:data:: OPT_REFHOPLIMIT

.. py:data:: OPT_RESTART

.. py:data:: OPT_SERVER_CONTROLS

.. py:data:: OPT_SIZELIMIT

.. py:data:: OPT_SUCCESS

.. py:data:: OPT_TIMELIMIT

.. py:data:: OPT_TIMEOUT

   .. versionchanged:: 3.0
      A timeout of ``-1`` or ``None`` resets timeout to infinity.

.. py:data:: OPT_URI

.. _ldap-sasl-options:

SASL options
::::::::::::

.. py:data:: OPT_X_SASL_AUTHCID

.. py:data:: OPT_X_SASL_AUTHZID

.. py:data:: OPT_X_SASL_MECH

.. py:data:: OPT_X_SASL_NOCANON

   If set to zero SASL host name canonicalization is disabled.

.. py:data:: OPT_X_SASL_REALM

.. py:data:: OPT_X_SASL_SECPROPS

.. py:data:: OPT_X_SASL_SSF

.. py:data:: OPT_X_SASL_SSF_EXTERNAL

.. py:data:: OPT_X_SASL_SSF_MAX

.. py:data:: OPT_X_SASL_SSF_MIN

.. _ldap-tls-options:

TLS options
:::::::::::

.. py:data:: OPT_X_TLS

.. py:data:: OPT_X_TLS_ALLOW

.. py:data:: OPT_X_TLS_CACERTDIR

.. py:data:: OPT_X_TLS_CACERTFILE

.. py:data:: OPT_X_TLS_CERTFILE

.. py:data:: OPT_X_TLS_CIPHER_SUITE

.. py:data:: OPT_X_TLS_CTX

.. py:data:: OPT_X_TLS_DEMAND

.. py:data:: OPT_X_TLS_HARD

.. py:data:: OPT_X_TLS_KEYFILE

.. py:data:: OPT_X_TLS_NEVER

.. py:data:: OPT_X_TLS_RANDOM_FILE

.. py:data:: OPT_X_TLS_REQUIRE_CERT

.. py:data:: OPT_X_TLS_TRY

.. _ldap-keepalive-options:

Keepalive options
:::::::::::::::::

.. py:data:: OPT_X_KEEPALIVE_IDLE

.. py:data:: OPT_X_KEEPALIVE_PROBES

.. py:data:: OPT_X_KEEPALIVE_INTERVAL

.. _ldap-dn-flags:

DN format flags
----------------

This constants are used for DN-parsing functions found in
sub-module :py:mod:`ldap.dn`.

.. seealso::
   `ldap_str2dn(3) <https://www.openldap.org/software/man.cgi?query=ldap_str2dn&sektion=3>`_

.. py:data:: DN_FORMAT_LDAP

.. py:data:: DN_FORMAT_LDAPV3

.. py:data:: DN_FORMAT_LDAPV2

.. py:data:: DN_FORMAT_DCE

.. py:data:: DN_FORMAT_UFN

.. py:data:: DN_FORMAT_AD_CANONICAL

.. py:data:: DN_FORMAT_MASK

.. py:data:: DN_PRETTY

.. py:data:: DN_SKIP

.. py:data:: DN_P_NOLEADTRAILSPACES

.. py:data:: DN_P_NOSPACEAFTERRDN

.. py:data:: DN_PEDANTIC



.. _ldap-exceptions:

Exceptions
==========

The module defines the following exceptions:

.. py:exception:: LDAPError

   This is the base class of all exceptions raised by the module :py:mod:`ldap`.
   Unlike the C interface, errors are not returned as result codes, but
   are instead turned into exceptions, raised as soon an the error condition
   is detected.

   The exceptions are accompanied by a dictionary possibly
   containing an string value for the key :py:const:`desc`
   (giving an English description of the error class)
   and/or a string value for the key :py:const:`info`
   (giving a string containing more information that the server may have sent).

   A third possible field of this dictionary is :py:const:`matched` and
   is set to a truncated form of the name provided or alias dereferenced
   for the lowest entry (object or alias) that was matched.


.. py:exception:: ADMINLIMIT_EXCEEDED

.. py:exception:: AFFECTS_MULTIPLE_DSAS

.. py:exception:: ALIAS_DEREF_PROBLEM

   A problem was encountered when dereferencing an alias.
   (Sets the :py:const:`matched` field.)

.. py:exception:: ALIAS_PROBLEM

   An alias in the directory points to a nonexistent entry.
   (Sets the :py:const:`matched` field.)

.. py:exception:: ALREADY_EXISTS

   The entry already exists. E.g. the *dn* specified with :py:meth:`add()`
   already exists in the DIT.

.. py:exception:: AUTH_UNKNOWN

   The authentication method specified to :py:meth:`bind()` is not known.

.. py:exception:: BUSY

   The DSA is busy.

.. py:exception:: CLIENT_LOOP

.. py:exception:: COMPARE_FALSE

   A compare operation returned false.
   (This exception should never be seen because :py:meth:`compare()` returns
   a boolean result.)

.. py:exception:: COMPARE_TRUE

   A compare operation returned true.
   (This exception should never be seen because :py:meth:`compare()` returns
   a boolean result.)

.. py:exception:: CONFIDENTIALITY_REQUIRED

   Indicates that the session is not protected by a protocol such
   as Transport Layer Security (TLS), which provides session
   confidentiality.

.. py:exception:: CONNECT_ERROR

.. py:exception:: CONSTRAINT_VIOLATION

   An attribute value specified or an operation started violates some
   server-side constraint
   (e.g., a postalAddress has too many lines or a line that is too long
   or a password is expired).

.. py:exception:: CONTROL_NOT_FOUND

.. py:exception:: DECODING_ERROR

   An error was encountered decoding a result from the LDAP server.

.. py:exception:: ENCODING_ERROR

   An error was encountered encoding parameters to send to the LDAP server.

.. py:exception:: FILTER_ERROR

   An invalid filter was supplied to :py:meth:`search()`
   (e.g. unbalanced parentheses).

.. py:exception:: INAPPROPRIATE_AUTH

   Inappropriate authentication was specified (e.g. :py:const:`AUTH_SIMPLE`
   was specified and the entry does not have a userPassword attribute).

.. py:exception:: INAPPROPRIATE_MATCHING

   Filter type not supported for the specified attribute.

.. py:exception:: INSUFFICIENT_ACCESS

   The user has insufficient access to perform the operation.

.. py:exception:: INVALID_CREDENTIALS

   Invalid credentials were presented during :py:meth:`bind()` or
   :py:meth:`simple_bind()`.
   (e.g., the wrong password).

.. py:exception:: INVALID_DN_SYNTAX

   A syntactically invalid DN was specified. (Sets the :py:const:`matched` field.)

.. py:exception:: INVALID_SYNTAX

   An attribute value specified by the client did not comply to the
   syntax defined in the server-side schema.

.. py:exception:: IS_LEAF

   The object specified is a leaf of the directory tree.
   Sets the :py:const:`matched` field of the exception dictionary value.

.. py:exception:: LOCAL_ERROR

   Some local error occurred. This is usually due to failed memory allocation.

.. py:exception:: LOOP_DETECT

   A loop was detected.

.. py:exception:: MORE_RESULTS_TO_RETURN

.. py:exception:: NAMING_VIOLATION

   A naming violation occurred. This is raised e.g. if the LDAP server
   has constraints about the tree naming.

.. py:exception:: NO_OBJECT_CLASS_MODS

   Modifying the objectClass attribute as requested is not allowed
   (e.g. modifying structural object class of existing entry).

.. py:exception:: NOT_ALLOWED_ON_NONLEAF

   The operation is not allowed on a non-leaf object.

.. py:exception:: NOT_ALLOWED_ON_RDN

   The operation is not allowed on an RDN.

.. py:exception:: NOT_SUPPORTED

.. py:exception:: NO_MEMORY

.. py:exception:: NO_OBJECT_CLASS_MODS

   Object class modifications are not allowed.

.. py:exception:: NO_RESULTS_RETURNED

.. py:exception:: NO_SUCH_ATTRIBUTE

   The attribute type specified does not exist in the entry.

.. py:exception:: NO_SUCH_OBJECT

   The specified object does not exist in the directory.
   Sets the :py:const:`matched` field of the exception dictionary value.

.. py:exception:: OBJECT_CLASS_VIOLATION

   An object class violation occurred when the LDAP server checked
   the data sent by the client against the server-side schema
   (e.g. a "must" attribute was missing in the entry data).

.. py:exception:: OPERATIONS_ERROR

   An operations error occurred.

.. py:exception:: OTHER

   An unclassified error occurred.

.. py:exception:: PARAM_ERROR

   An ldap routine was called with a bad parameter.

.. py:exception:: PARTIAL_RESULTS

   Partial results only returned. This exception is raised if
   a referral is received when using LDAPv2.
   (This exception should never be seen with LDAPv3.)

.. py:exception:: PROTOCOL_ERROR

   A violation of the LDAP protocol was detected.

.. py:exception:: RESULTS_TOO_LARGE

   The result does not fit into a UDP packet. This happens only when using
   UDP-based CLDAP (connection-less LDAP) which is not supported anyway.

.. py:exception:: SASL_BIND_IN_PROGRESS

.. py:exception:: SERVER_DOWN

   The  LDAP  library  can't  contact the LDAP server.

.. py:exception:: SIZELIMIT_EXCEEDED

   An LDAP size limit was exceeded.
   This could be due to a ``sizelimit`` configuration on the LDAP server.

.. py:exception:: STRONG_AUTH_NOT_SUPPORTED

   The LDAP server does not support strong authentication.

.. py:exception:: STRONG_AUTH_REQUIRED

   Strong authentication is required  for the operation.

.. py:exception:: TIMELIMIT_EXCEEDED

   An LDAP time limit was exceeded.

.. py:exception:: TIMEOUT

   A timelimit was exceeded while waiting for a result from the server.

.. py:exception:: TYPE_OR_VALUE_EXISTS

   An  attribute  type or attribute value specified already
   exists in the entry.

.. py:exception:: UNAVAILABLE

   The DSA is unavailable.

.. py:exception:: UNAVAILABLE_CRITICAL_EXTENSION

   Indicates that the LDAP server was unable to satisfy a request
   because one or more critical extensions were not available. Either
   the server does not support the control or the control is not appropriate
   for the operation type.

.. py:exception:: UNDEFINED_TYPE

   An attribute type used is not defined in the server-side schema.

.. py:exception:: UNWILLING_TO_PERFORM

   The  DSA is  unwilling to perform the operation.

.. py:exception:: USER_CANCELLED

   The operation was cancelled via the :py:meth:`abandon()` method.

The above exceptions are raised when a result code from an underlying API
call does not indicate success.


Warnings
========

.. py:class:: LDAPBytesWarning

    Raised when bytes/text mismatch in non-strict bytes mode.

    See :ref:`bytes_mode` for details.

    .. versionadded:: 3.0.0


.. _ldap-objects:

LDAPObject classes
==================

.. py:class:: LDAPObject

   Instances of :py:class:`LDAPObject` are returned by :py:func:`initialize()`
   and :py:func:`open()` (deprecated). The connection is automatically unbound
   and closed when the LDAP object is deleted.

   Internally :py:class:`LDAPObject` is set to :py:class:`SimpleLDAPObject`
   by default.

.. py:class:: SimpleLDAPObject(uri [, trace_level=0 [, trace_file=sys.stdout [, trace_stack_limit=5]]])

   This basic class wraps all methods of the underlying C API object.

   The arguments are same like for function :py:func:`initialize()`.

.. py:class:: ReconnectLDAPObject(uri [, trace_level=0 [, trace_file=sys.stdout [, trace_stack_limit=5] [, retry_max=1 [, retry_delay=60.0]]]])

   This class is derived from :py:class:`SimpleLDAPObject` and used for automatic
   reconnects when using the synchronous request methods (see below). This class
   also implements the pickle protocol.

   The first arguments are same like for function :py:func:`initialize()`.

   For automatic reconnects it has additional arguments:

   *retry_max* specifies the number of reconnect attempts before
   re-raising the :py:exc:`ldap.SERVER_DOWN` exception.

   *retry_delay* specifies the time in seconds between reconnect attempts.


.. _ldap-controls:

Arguments for LDAPv3 controls
-----------------------------

The :py:mod:`ldap.controls` module can be used for constructing and
decoding LDAPv3 controls. These arguments are available in the methods
with names ending in :py:const:`_ext` or :py:const:`_ext_s`:

*serverctrls*
  is a list of :py:class:`ldap.controls.LDAPControl` instances sent to the server along
  with the LDAP request (see module :py:mod:`ldap.controls`). These are
  controls which alter the behaviour of the server when processing the
  request if the control is supported by the server. The effect of controls
  might differ depending on the type of LDAP request or controls might not
  be applicable with certain LDAP requests at all.

*clientctrls*
  is a list of :py:class:`ldap.controls.LDAPControl` instances passed to the
  client API and alter the behaviour of the client when processing the
  request.


.. _sending-ldap-requests:

Sending LDAP requests
---------------------

Most methods on LDAP objects initiate an asynchronous request to the
LDAP server and return a message id that can be used later to retrieve
the result with :py:meth:`result()`.

Methods with names ending in :py:const:`_s` are the synchronous form
and wait for and return with the server's result, or with
:py:const:`None` if no data is expected.


:class:`LDAPObject` instances have the following methods:

.. py:method:: LDAPObject.abandon(msgid) -> None

.. py:method:: LDAPObject.abandon_ext(msgid [, serverctrls=None [, clientctrls=None]]) -> None

   Abandons an LDAP operation in progress without waiting for a LDAP response.
   The *msgid* argument should be the message ID of an outstanding LDAP
   operation as returned by the asynchronous methods :py:meth:`search()`, :py:meth:`modify()`, etc.
   The caller can expect that the result of an abandoned operation will not be
   returned from a future call to :py:meth:`result()`.

   *serverctrls* and *clientctrls* like described in section :ref:`ldap-controls`.


.. py:method:: LDAPObject.add(dn, modlist) -> int

.. py:method:: LDAPObject.add_s(dn, modlist) -> None

.. py:method:: LDAPObject.add_ext(dn, modlist [, serverctrls=None [, clientctrls=None]]) -> int

.. py:method:: LDAPObject.add_ext_s(dn, modlist [, serverctrls=None [, clientctrls=None]]) -> tuple

   Performs an LDAP add operation. The *dn* argument is the distinguished
   name (DN) of the entry to add, and *modlist* is a list of attributes to be
   added. The modlist is similar the one passed to :py:meth:`modify()`, except that the
   operation integer is omitted from the tuples in modlist. You might want to
   look into sub-module \refmodule{ldap.modlist} for generating the modlist.

   The asynchronous methods :py:meth:`add()` and :py:meth:`add_ext()`
   return the message ID of the initiated request.

   *serverctrls* and *clientctrls* like described in section :ref:`ldap-controls`.

   The *dn* argument, and mod_type (second item) of *modlist* are text strings;
   see :ref:`bytes_mode`.


.. py:method:: LDAPObject.bind(who, cred, method) -> int

.. py:method:: LDAPObject.bind_s(who, cred, method) -> None

.. py:method:: LDAPObject.cancel( cancelid, [, serverctrls=None [, clientctrls=None]]) -> None

   Send cancels extended operation for an LDAP operation specified by *cancelid*.
   The *cancelid* should be the message id of an outstanding LDAP operation as returned
   by the asynchronous methods search(), modify() etc.  The caller
   can expect that the result of an abandoned operation will not be
   returned from a future call to :py:meth:`result()`.
   In opposite to :py:meth:`abandon()` this extended operation gets an result from
   the server and thus should be preferred if the server supports it.

   *serverctrls* and *clientctrls* like described in section :ref:`ldap-controls`.

   :rfc:`3909` - Lightweight Directory Access Protocol (LDAP): Cancel Operation


.. py:method:: LDAPObject.compare(dn, attr, value) -> int

.. py:method:: LDAPObject.compare_s(dn, attr, value) -> bool

.. py:method:: LDAPObject.compare_ext(dn, attr, value [, serverctrls=None [, clientctrls=None]]) -> int

.. py:method:: LDAPObject.compare_ext_s(dn, attr, value [, serverctrls=None [, clientctrls=None]]) -> bool

   Perform an LDAP comparison between the attribute named *attr* of entry *dn*,
   and the value *value*. The synchronous forms returns ``True`` or ``False``.
   The asynchronous forms returns the message ID of the initiated request, and
   the result of the asynchronous compare can be obtained using
   :py:meth:`result()`.

   Note that the asynchronous technique yields the answer
   by raising the exception objects :py:exc:`ldap.COMPARE_TRUE` or
   :py:exc:`ldap.COMPARE_FALSE`.

   *serverctrls* and *clientctrls* like described in section :ref:`ldap-controls`.

   The *dn* and *attr* arguments are text strings; see :ref:`bytes_mode`.

   .. note::

      A design fault in the LDAP API prevents *value*
      from containing *NULL* characters.


.. py:method:: LDAPObject.delete(dn) -> int

.. py:method::  LDAPObject.delete_s(dn) -> None

.. py:method:: LDAPObject.delete_ext(dn [, serverctrls=None [, clientctrls=None]]) -> int

.. py:method:: LDAPObject.delete_ext_s(dn [, serverctrls=None [, clientctrls=None]]) -> tuple

   Performs an LDAP delete operation on *dn*. The asynchronous form
   returns the message id of the initiated request, and the result can be obtained
   from a subsequent call to :py:meth:`result()`.

   *serverctrls* and *clientctrls* like described in section :ref:`ldap-controls`.

   The *dn* argument is text string; see :ref:`bytes_mode`.


.. py:method:: LDAPObject.extop(extreq[,serverctrls=None[,clientctrls=None]]]) -> int

.. py:method:: LDAPObject.extop_s(extreq[,serverctrls=None[,clientctrls=None[,extop_resp_class=None]]]]) -> (respoid,respvalue)

   Performs an LDAP extended operation. The asynchronous
   form returns the message id of the initiated request, and the
   result can be obtained from a subsequent call to :py:meth:`extop_result()`.

   The *extreq* is an instance of class :py:class:`ldap.extop.ExtendedRequest`
   containing the parameters for the extended operation request.

   *serverctrls* and *clientctrls* like described in section :ref:`ldap-controls`.

   If argument *extop_resp_class* is set to a sub-class of
   :py:class:`ldap.extop.ExtendedResponse` this class is used to return an
   object of this class instead of a raw BER value in respvalue.

.. py:method:: LDAPObject.extop_result(self,msgid=ldap.RES_ANY,all=1,timeout=None) -> (respoid,respvalue)

   Wrapper method around :py:meth:`result4()` just for retrieving
   the result of an extended operation sent before.


.. py:method:: LDAPObject.modify(dn, modlist) -> int

.. py:method:: LDAPObject.modify_s(dn, modlist) -> None

.. py:method:: LDAPObject.modify_ext(dn, modlist [, serverctrls=None [, clientctrls=None]]) -> int

.. py:method:: LDAPObject.modify_ext_s(dn, modlist [, serverctrls=None [, clientctrls=None]]) -> tuple

   Performs an LDAP modify operation on an entry's attributes.
   The *dn* argument is the distinguished name (DN) of the entry to modify,
   and *modlist* is a list of modifications to make to that entry.

   Each element in the list *modlist* should be a tuple of the form
   *(mod_op,mod_type,mod_vals)*,
   where *mod_op* indicates the operation (one of :py:const:`ldap.MOD_ADD`,
   :py:const:`ldap.MOD_DELETE`, or :py:const:`ldap.MOD_REPLACE`),
   *mod_type* is a string indicating the attribute type name, and
   *mod_vals* is either a string value or a list of string values to add,
   delete or replace respectively.  For the delete operation, *mod_vals*
   may be :py:const:`None` indicating that all attributes are to be deleted.

   *serverctrls* and *clientctrls* like described in section :ref:`ldap-controls`.

   The asynchronous methods :py:meth:`modify()` and :py:meth:`modify_ext()`
   return the message ID of the initiated request.

   You might want to look into sub-module :py:mod:`ldap.modlist` for
   generating *modlist*.

   The *dn* argument, and mod_type (second item) of *modlist* are text strings;
   see :ref:`bytes_mode`.


.. py:method:: LDAPObject.modrdn(dn, newrdn [, delold=1]) -> int


.. py:method::  LDAPObject.modrdn_s(dn, newrdn [, delold=1]) -> None

   Perform a ``modify RDN`` operation, (i.e. a renaming operation).
   These routines take *dn* (the DN of the entry whose RDN is to be changed,
   and *newrdn*, the new RDN to give to the entry. The optional parameter
   *delold* is used to specify whether the old RDN should be kept as an
   attribute of the entry or not.
   The asynchronous version returns the initiated message id.

   This operation is emulated by :py:meth:`rename()` and :py:meth:`rename_s()` methods
   since the modrdn2* routines in the C library are deprecated.

   The *dn* and *newrdn* arguments are text strings; see :ref:`bytes_mode`.


.. py:method:: LDAPObject.passwd(user, oldpw, newpw [, serverctrls=None [, clientctrls=None]]) -> int

.. py:method:: LDAPObject.passwd_s(user, oldpw, newpw [, serverctrls=None [, clientctrls=None]]) -> None

   Perform a ``LDAP Password Modify Extended Operation`` operation
   on the entry specified by *user*.
   The old password in *oldpw* is replaced with the new
   password in *newpw* by a LDAP server supporting this operation.

   If *oldpw* is not :py:const:`None` it has to match the old password
   of the specified *user* which is sometimes used when a user changes
   his own password.

   *serverctrls* and *clientctrls* like described in section :ref:`ldap-controls`.

   The asynchronous version returns the initiated message id.

   The *user*, *oldpw* and *newpw* arguments are text strings; see :ref:`bytes_mode`.

   .. seealso::

      :rfc:`3062` - LDAP Password Modify Extended Operation



.. py:method:: LDAPObject.rename(dn, newrdn [, newsuperior=None [, delold=1 [, serverctrls=None [, clientctrls=None]]]]) -> int

.. py:method:: LDAPObject.rename_s(dn, newrdn [, newsuperior=None [, delold=1 [, serverctrls=None [, clientctrls=None]]]]) -> None

   Perform a ``Rename`` operation, (i.e. a renaming operation).
   These routines take *dn* (the DN of the entry whose RDN is to be changed,
   and *newrdn*, the new RDN to give to the entry.
   The optional parameter *newsuperior* is used to specify
   a new parent DN for moving an entry in the tree
   (not all LDAP servers support this).
   The optional parameter *delold* is used to specify
   whether the old RDN should be kept as an attribute of the entry or not.

   *serverctrls* and *clientctrls* like described in section :ref:`ldap-controls`.

   The *dn* and *newdn* arguments are text strings; see :ref:`bytes_mode`.


.. py:method:: LDAPObject.result([msgid=RES_ANY [, all=1 [, timeout=None]]]) -> 2-tuple

   This method is used to wait for and return the result of an operation
   previously initiated by one of the LDAP *asynchronous* operations
   (e.g. :py:meth:`search()`, :py:meth:`modify()`, etc.)

   The *msgid* parameter is the integer identifier returned by that method.
   The identifier is guaranteed to be unique across an LDAP session,
   and tells the :py:meth:`result()` method to request the result of that
   specific operation.

   If a result is desired from any one of the in-progress operations,
   *msgid* should be specified as the constant :py:const:`RES_ANY`
   and the method :py:meth:`result2()` should be used instead.

   The *all* parameter only has meaning for :py:meth:`search()` responses
   and is used to select whether a single entry of the search
   response should be returned, or to wait for all the results
   of the search before returning.

   A search response is made up of zero or more search entries
   followed by a search result. If *all* is 0, search entries will
   be returned one at a time as they come in, via separate calls
   to :py:meth:`result()`. If all is 1, the search response will be returned
   in its entirety, i.e. after all entries and the final search
   result have been received.

   For *all* set to 0, result tuples
   trickle in (with the same message id), and with the result types
   :py:const:`RES_SEARCH_ENTRY` and :py:const:`RES_SEARCH_REFERENCE`,
   until the final result which has a result type of :py:const:`RES_SEARCH_RESULT`
   and a (usually) empty data field.  When all is set to 1, only one result is returned,
   with a result type of RES_SEARCH_RESULT, and all the result tuples
   listed in the data field.

   The *timeout* parameter is a limit on the number of seconds that the
   method will wait for a response from the server.
   If *timeout* is negative (which is the default),
   the method will wait indefinitely for a response.
   The timeout can be expressed as a floating-point value, and
   a value of :py:const:`0` effects a poll.
   If a timeout does occur, a :py:exc:`ldap.TIMEOUT` exception is raised,
   unless polling, in which case ``(None, None)`` is returned.

   The :py:meth:`result()` method returns a tuple of the form
   ``(result-type, result-data)``.
   The first element, ``result-type`` is a string, being one of
   these module constants:
   :py:const:`RES_BIND`, :py:const:`RES_SEARCH_ENTRY`,
   :py:const:`RES_SEARCH_REFERENCE`, :py:const:`RES_SEARCH_RESULT`,
   :py:const:`RES_MODIFY`, :py:const:`RES_ADD`, :py:const:`RES_DELETE`,
   :py:const:`RES_MODRDN`, or :py:const:`RES_COMPARE`.

   If *all* is :py:const:`0`, one response at a time is returned on
   each call to :py:meth:`result()`, with termination indicated by
   ``result-data`` being an empty list.

   See :py:meth:`search()` for a description of the search result's
   ``result-data``, otherwise the ``result-data`` is normally meaningless.



.. py:method:: LDAPObject.result2([msgid=RES_ANY [, all=1 [, timeout=None]]]) -> 3-tuple

   This method behaves almost exactly like :py:meth:`result()`. But
   it returns a 3-tuple also containing the message id of the
   outstanding LDAP operation a particular result message belongs
   to. This is especially handy if one needs to dispatch results
   obtained with ``msgid=``:py:const:`RES_ANY` to several consumer
   threads which invoked a particular LDAP operation.


.. py:method:: LDAPObject.result3([msgid=RES_ANY [, all=1 [, timeout=None]]]) -> 4-tuple

   This method behaves almost exactly like :py:meth:`result2()`. But it
   returns an extra item in the tuple, the decoded server controls.

.. py:method:: LDAPObject.result4([msgid=RES_ANY [, all=1 [, timeout=None [, add_ctrls=0 [, add_intermediates=0 [, add_extop=0 [, resp_ctrl_classes=None]]]]]]]) -> 6-tuple

   This method behaves almost exactly like :py:meth:`result3()`. But it
   returns an extra items in the tuple, the decoded results of an extended response.

   The additional arguments are:

   *add_ctrls* (integer flag) specifies whether response controls are returned.

   add_intermediates (integer flag) specifies whether response controls of
   intermediate search results are returned.

   *add_extop* (integer flag) specifies whether the response of an
   extended operation is returned. If using extended operations you should
   consider using the method :py:meth:`extop_result()` or
   :py:meth:`extop_s()` instead.

   *resp_ctrl_classes* is a dictionary mapping the OID of a response controls to a
   :py:class:`ldap.controls.ResponseControl` class of response controls known by the
   application. So the response control value will be automatically decoded.
   If :py:const:`None` the global dictionary :py:data:`ldap.controls.KNOWN_RESPONSE_CONTROLS`
   is used instead.

.. py:method:: LDAPObject.sasl_interactive_bind_s(who, auth[, serverctrls=None [, clientctrls=None [, sasl_flags=ldap.SASL_QUIET]]]) -> None

   This call is used to bind to the directory with a SASL bind request.

   *auth* is an :py:class:`ldap.sasl.sasl()` instance.

   *serverctrls* and *clientctrls* like described in section :ref:`ldap-controls`.


.. py:method:: LDAPObject.sasl_non_interactive_bind_s(sasl_mech[, serverctrls=None [, clientctrls=None [, sasl_flags=ldap.SASL_QUIET [, authz_id='']]]]) -> None

   This call is used to bind to the directory with a SASL bind request with
   non-interactive SASL mechanism defined with argument *sasl_mech* and
   internally calls :py:meth:`sasl_interactive_bind_s()`.

   *serverctrls* and *clientctrls* like described in section :ref:`ldap-controls`.


.. py:method:: LDAPObject.sasl_external_bind_s([serverctrls=None [, clientctrls=None [, sasl_flags=ldap.SASL_QUIET [, authz_id='']]]]) -> None

   This call is used to bind to the directory with a SASL bind request with
   mechanism EXTERNAL and internally calls :py:meth:`sasl_non_interactive_bind_s()`.

   *serverctrls* and *clientctrls* like described in section :ref:`ldap-controls`.


.. py:method:: LDAPObject.sasl_gssapi_bind_s([serverctrls=None [, clientctrls=None [, sasl_flags=ldap.SASL_QUIET [, authz_id='']]]]) -> None

   This call is used to bind to the directory with a SASL bind request with
   mechanism GSSAPI and internally calls :py:meth:`sasl_non_interactive_bind_s()`.

   *serverctrls* and *clientctrls* like described in section :ref:`ldap-controls`.


.. py:method:: LDAPObject.simple_bind([who=None [, cred=None [, serverctrls=None [, clientctrls=None]]]]) -> int

.. py:method:: LDAPObject.simple_bind_s([who=None [, cred=None [, serverctrls=None [, clientctrls=None]]]]) -> None

   After an LDAP object is created, and before any other operations can be
   attempted over the connection, a bind operation must be performed.

   This method attempts to bind with the LDAP server using
   either simple authentication, or Kerberos (if available).
   The first and most general method, :py:meth:`bind()`,
   takes a third parameter, *method* which can currently solely
   be :py:const:`AUTH_SIMPLE`.

   *serverctrls* and *clientctrls* like described in section :ref:`ldap-controls`.

   The *who* and *cred* arguments are text strings; see :ref:`bytes_mode`.

   .. versionchanged:: 3.0

      :meth:`~LDAPObject.simple_bind` and :meth:`~LDAPObject.simple_bind_s`
      now accept ``None`` for *who* and *cred*, too.

.. py:method:: LDAPObject.search(base, scope [,filterstr='(objectClass=*)' [, attrlist=None [, attrsonly=0]]]) ->int

.. py:method:: LDAPObject.search_s(base, scope [,filterstr='(objectClass=*)' [, attrlist=None [, attrsonly=0]]]) ->list|None

.. py:method:: LDAPObject.search_st(base, scope [,filterstr='(objectClass=*)' [, attrlist=None [, attrsonly=0 [, timeout=-1]]]]) -> list|None

.. py:method:: LDAPObject.search_ext(base, scope [,filterstr='(objectClass=*)' [, attrlist=None [, attrsonly=0 [, serverctrls=None [, clientctrls=None [, timeout=-1 [, sizelimit=0]]]]]]]) -> int

.. py:method:: LDAPObject.search_ext_s(base, scope [,filterstr='(objectClass=*)' [, attrlist=None [, attrsonly=0 [, serverctrls=None [, clientctrls=None [, timeout=-1 [, sizelimit=0]]]]]]]) -> list|None

   Perform an LDAP search operation, with *base* as the DN of the entry
   at which to start the search, *scope* being one of
   :py:const:`SCOPE_BASE` (to search the object itself),
   :py:const:`SCOPE_ONELEVEL` (to search the object's immediate children), or
   :py:const:`SCOPE_SUBTREE` (to search the object and all its descendants).

   The *filterstr* argument is a string representation of the filter to apply in
   the search.

   .. seealso::

      :rfc:`4515` - Lightweight Directory Access Protocol (LDAP): String Representation of Search Filters.


   Each result tuple is of the form ``(dn, attrs)``,
   where *dn* is a string containing the DN (distinguished name) of the
   entry, and *attrs* is a dictionary containing the attributes associated
   with the entry. The keys of *attrs* are strings, and the associated
   values are lists of strings.

   The DN in *dn* is automatically extracted using the underlying libldap
   function :c:func:`ldap_get_dn()`, which may raise an exception if the
   DN is malformed.

   If *attrsonly* is non-zero, the values of *attrs* will be meaningless
   (they are not transmitted in the result).

   The retrieved attributes can be limited with the *attrlist* parameter.
   If *attrlist* is :py:const:`None`, all the attributes of each entry are returned.

   *serverctrls* and *clientctrls* like described in section :ref:`ldap-controls`.

   The synchronous form with timeout, :py:meth:`search_st()` or :py:meth:`search_ext_s()`,
   will block for at most *timeout* seconds (or indefinitely if *timeout*
   is negative). A :py:exc:`ldap.TIMEOUT` exception is raised if no result is received
   within the specified time.

   The amount of search results retrieved can be limited with the
   *sizelimit* parameter when using :py:meth:`search_ext()`
   or :py:meth:`search_ext_s()` (client-side search limit). If non-zero
   not more than *sizelimit* results are returned by the server.

   The *base* and *filterstr* arguments, and *attrlist* contents,
   are text strings; see :ref:`bytes_mode`.

   .. versionchanged:: 3.0

      ``filterstr=None`` is equivalent to ``filterstr='(objectClass=*)'``.


.. py:method:: LDAPObject.start_tls_s() -> None

   Negotiate TLS with server. The ``version`` attribute must have been
   set to :py:const:`VERSION3` (which it is by default) before calling this method.
   If TLS could not be started an exception will be raised.

  .. seealso::

    :rfc:`2830` - Lightweight Directory Access Protocol (v3): Extension for Transport Layer Security


.. py:method:: LDAPObject.unbind() -> int

.. py:method:: LDAPObject.unbind_s() -> None

.. py:method:: LDAPObject.unbind_ext([, serverctrls=None [, clientctrls=None]]) -> int

.. py:method:: LDAPObject.unbind_ext_s([, serverctrls=None [, clientctrls=None]]) -> None

   This call is used to unbind from the directory, terminate the
   current association, and free resources. Once called, the connection to the
   LDAP server is closed and the LDAP object is marked invalid.
   Further invocation of methods on the object will yield exceptions.

   *serverctrls* and *clientctrls* like described in section :ref:`ldap-controls`.

   These methods are all synchronous in nature.


.. py:method:: LDAPObject.whoami_s() -> string

   This synchronous method implements the LDAP "Who Am I?"
   extended operation.

   It is useful for finding out to find out which identity
   is assumed by the LDAP server after a SASL bind.

   .. seealso::

      :rfc:`4532` - Lightweight Directory Access Protocol (LDAP) "Who am I?" Operation


Connection-specific LDAP options
--------------------------------

.. py:method:: LDAPObject.get_option(option) -> int|string

   This method returns the value of the LDAPObject option
   specified by *option*.


.. py:method:: LDAPObject.set_option(option, invalue) -> None

   This method sets the value of the LDAPObject option
   specified by *option* to *invalue*.


Object attributes
-----------------

If the underlying library provides enough information,
each LDAP object will also have the following attributes.
These attributes are mutable unless described as read-only.

.. py:attribute:: LDAPObject.deref -> int

   Controls whether aliases are automatically dereferenced.
   This must be one of :py:const:`DEREF_NEVER`, :py:const:`DEREF_SEARCHING`,
   :py:const:`DEREF_FINDING` or :py:const:`DEREF_ALWAYS`.
   This option is mapped to option constant :py:const:`OPT_DEREF`
   and used in the underlying OpenLDAP client lib.


.. py:attribute:: LDAPObject.network_timeout -> int

   Limit on waiting for a network response, in seconds.
   Defaults to :py:const:`NO_LIMIT`.
   This option is mapped to option constant :py:const:`OPT_NETWORK_TIMEOUT`
   and used in the underlying OpenLDAP client lib.

   .. versionchanged:: 3.0.0
      A timeout of ``-1`` or ``None`` resets timeout to infinity.

.. py:attribute:: LDAPObject.protocol_version -> int

   Version of LDAP in use (either :py:const:`VERSION2` for LDAPv2
   or :py:const:`VERSION3` for LDAPv3).
   This option is mapped to option constant :py:const:`OPT_PROTOCOL_VERSION`
   and used in the underlying OpenLDAP client lib.

   .. note::

      It is highly recommended to set the protocol version after establishing
      a LDAP connection with :py:func:`ldap.initialize()` and before submitting
      the first request.


.. py:attribute:: LDAPObject.sizelimit -> int

   Limit on size of message to receive from server.
   Defaults to :py:const:`NO_LIMIT`.
   This option is mapped to option constant :py:const:`OPT_SIZELIMIT`
   and used in the underlying OpenLDAP client lib. Its use is deprecated
   in favour of *sizelimit* parameter when using :py:meth:`search_ext()`.


.. py:attribute:: LDAPObject.timelimit -> int

   Limit on waiting for any response, in seconds.
   Defaults to :py:const:`NO_LIMIT`.
   This option is mapped to option constant :py:const:`OPT_TIMELIMIT`
   and used in the underlying OpenLDAP client lib. Its use is deprecated
   in favour of using :py:attr:`timeout`.


.. py:attribute:: LDAPObject.timeout -> int

   Limit on waiting for any response, in seconds.
   Defaults to :py:const:`NO_LIMIT`.
   This option is used in the wrapper module.


.. _ldap-example:

Example
=======

The following example demonstrates how to open a connection to an
LDAP server using the :py:mod:`ldap` module and invoke a synchronous
subtree search.

>>> import ldap
>>> l = ldap.initialize('ldap://localhost:1390')
>>> l.search_s('ou=Testing,dc=stroeder,dc=de',ldap.SCOPE_SUBTREE,'(cn=fred*)',['cn','mail'])
[('cn=Fred Feuerstein,ou=Testing,dc=stroeder,dc=de', {'cn': ['Fred Feuerstein']})]
>>> r = l.search_s('ou=Testing,dc=stroeder,dc=de',ldap.SCOPE_SUBTREE,'(objectClass=*)',['cn','mail'])
>>> for dn,entry in r:
>>>   print('Processing',repr(dn))
>>>   handle_ldap_entry(entry)

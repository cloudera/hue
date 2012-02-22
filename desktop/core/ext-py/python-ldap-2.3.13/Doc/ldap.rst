.. % $Id: ldap.rst,v 1.18 2011/02/19 13:05:16 stroeder Exp $

*****************************************
:mod:`ldap` LDAP library interface module
*****************************************

.. module:: ldap
   :platform: UNIX,Windows
   :synopsis: Access to an underlying LDAP C library.
.. moduleauthor:: python-ldap project (see http://www.python-ldap.org/)


This module provides access to the LDAP  (Lightweight Directory Access Protocol)
C API implemented  in OpenLDAP 2.3 or newer.  It is similar to the C API, with
the notable differences  that lists are manipulated via Python  list operations
and errors appear as exceptions.    For far more detailed information on the C
interface,   please see the (expired) draft-ietf-ldapext-ldap-c-api-04.    This
documentation is current for the Python LDAP module, version  |release|.  Source
and binaries are available from http://www.python-ldap.org/.

.. % not standard, in C
.. % Author of the module code;
.. % Leave at least one blank line after this, to simplify ad-hoc tools
.. % that are sometimes used to massage these files.
.. % ==== 2. ====
.. % Give a short overview of what the module does.
.. % If it is platform specific, mention this.
.. % Mention other important restrictions or general operating principles.
.. % ==== 3. ====
.. % List the public functions defined by the module.  Begin with a
.. % standard phrase.  You may also list the exceptions and other data
.. % items defined in the module, insofar as they are important for the
.. % user.


Functions
=========

The :mod:`ldap` module defines the following functions:

.. function:: initialize(uri [, trace_level=0 [, trace_file=sys.stdout [, trace_stack_limit=None]]])

   Opens a new connection with an LDAP server, and return an LDAP object
   (see :ref:`ldap-objects`) used to perform operations on that server.  Parameter
   *uri* has to be a valid LDAP URL.
   The optional arguments are for generating debug log information:
   *trace_level* specifies the amount of information being logged,
   *trace_file* specifies a file-like object as target of the debug log and
   *trace_stack_limit* specifies the stack limit of tracebacks in debug log.
   Possible values for *trace_level* are
   :const:`0` for no logging,
   :const:`1` for only logging the method calls with arguments,
   :const:`2` for logging the method calls with arguments and the complete results and 
   :const:`3` for also logging the traceback of method calls.

   .. seealso::

      :rfc:`4516` - Lightweight Directory Access Protocol (LDAP): Uniform Resource Locator

   .. % -> LDAPObject

.. function:: open(host [, port=PORT])

   Opens a new connection with an LDAP server, and return an LDAP object  (see
   :ref:`ldap-objects`) used to perform operations on that server.  *host* is a
   string containing solely the host name. *port*  is an integer specifying the
   port where the LDAP server is  listening (default is 389).  Note: Using this
   function is deprecated.

   .. % -> LDAPObject

.. % %------------------------------------------------------------
.. % % get_option


.. function:: get_option(option)

   This function returns the value of the global option  specified by *option*.

   .. % -> None

.. % %------------------------------------------------------------
.. % % set_option


.. function:: set_option(option, invalue)

   This function sets the value of the global option  specified by *option* to
   *invalue*.

   .. % -> None

.. _ldap-constants:

Constants
=========

The module defines various constants. Note that some constants depend
on the build options and which underlying libs were used or even on
the version of the libs. So before using those constants the application has
to explicitly check whether they are available.

General
-------

.. data:: PORT

   The assigned TCP port number (389) that LDAP servers listen on.

.. data:: SASL_AVAIL

   Integer where a non-zero value indicates that python-ldap was built with
   support for SASL (Cyrus-SASL).

.. data:: TLS_AVAIL

   Integer where a non-zero value indicates that python-ldap was built with
   support for SSL/TLS (OpenSSL or similar libs).


.. _ldap-options:

Options
-------

.. seealso::

   :manpage:`ldap.conf{5}` and :manpage:`ldap_get_options{3}`


For use with functions and method set_option() and get_option() the
following option identifiers are defined as constants:

.. data:: OPT_API_FEATURE_INFO

.. data:: OPT_API_INFO

.. data:: OPT_CLIENT_CONTROLS

.. data:: OPT_DEBUG_LEVEL

   Sets the debug level within the underlying LDAP C lib.

.. data:: OPT_DEFBASE

.. data:: OPT_DEREF

   Specifies how alias derefencing is done within the underlying LDAP C lib.

.. data:: OPT_ERROR_STRING

.. data:: OPT_DIAGNOSTIC_MESSAGE

.. data:: OPT_HOST_NAME

.. data:: OPT_MATCHED_DN

.. data:: OPT_NETWORK_TIMEOUT

.. data:: OPT_PROTOCOL_VERSION

   Sets the LDAP protocol version used for a connection. This is mapped to
   object attribute `ldap.LDAPObject.protocol_version`

.. data:: OPT_REFERRALS

   int specifying whether referrals should be automatically chased within
   the underlying LDAP C lib.

.. data:: OPT_REFHOPLIMIT

.. data:: OPT_RESTART

.. data:: OPT_SERVER_CONTROLS

.. data:: OPT_SIZELIMIT

.. data:: OPT_SUCCESS

.. data:: OPT_TIMELIMIT

.. data:: OPT_TIMEOUT

.. data:: OPT_URI

.. _ldap-sasl-options:

SASL options
::::::::::::

.. data:: OPT_X_SASL_AUTHCID

.. data:: OPT_X_SASL_AUTHZID

.. data:: OPT_X_SASL_MECH

.. data:: OPT_X_SASL_NOCANON

   If set to zero SASL host name canonicalization is disabled.

.. data:: OPT_X_SASL_REALM

.. data:: OPT_X_SASL_SECPROPS

.. data:: OPT_X_SASL_SSF

.. data:: OPT_X_SASL_SSF_EXTERNAL

.. data:: OPT_X_SASL_SSF_MAX

.. data:: OPT_X_SASL_SSF_MIN

.. _ldap-tls-options:

TLS options
:::::::::::

.. data:: OPT_X_TLS

.. data:: OPT_X_TLS_ALLOW

.. data:: OPT_X_TLS_CACERTDIR

.. data:: OPT_X_TLS_CACERTFILE

.. data:: OPT_X_TLS_CERTFILE

.. data:: OPT_X_TLS_CIPHER_SUITE

.. data:: OPT_X_TLS_CTX

.. data:: OPT_X_TLS_DEMAND

.. data:: OPT_X_TLS_HARD

.. data:: OPT_X_TLS_KEYFILE

.. data:: OPT_X_TLS_NEVER

.. data:: OPT_X_TLS_RANDOM_FILE

.. data:: OPT_X_TLS_REQUIRE_CERT

.. data:: OPT_X_TLS_TRY

.. _ldap-keepalive-options:

Keepalive options
:::::::::::::::::

.. data:: OPT_X_KEEPALIVE_IDLE

.. data:: OPT_X_KEEPALIVE_PROBES

.. data:: OPT_X_KEEPALIVE_INTERVAL

.. _ldap-dn-flags:

DN format flags
----------------

This constants are used for DN-parsing functions found in
sub-module :mod:`ldap.dn`.

.. seealso::

   :manpage:`ldap_str2dn{3}`


.. data:: DN_FORMAT_LDAP

.. data:: DN_FORMAT_LDAPV3

.. data:: DN_FORMAT_LDAPV2

.. data:: DN_FORMAT_DCE

.. data:: DN_FORMAT_UFN

.. data:: DN_FORMAT_AD_CANONICAL

.. data:: DN_FORMAT_MASK

.. data:: DN_PRETTY

.. data:: DN_SKIP

.. data:: DN_P_NOLEADTRAILSPACES

.. data:: DN_P_NOSPACEAFTERRDN

.. data:: DN_PEDANTIC



.. _ldap-exceptions:

Exceptions
==========

The module defines the following exceptions:

.. exception:: LDAPError

   This is the base class of all execeptions raised by the module :mod:`ldap`.
   Unlike the C interface, errors are not returned as result codes, but
   are instead turned into exceptions, raised as soon an the error condition 
   is detected.

   The exceptions are accompanied by a dictionary possibly
   containing an string value for the key :const:`desc`
   (giving an English description of the error class)
   and/or a string value for the key :const:`info`
   (giving a string containing more information that the server may have sent).

   A third possible field of this dictionary is :const:`matched` and
   is set to a truncated form of the name provided or alias dereferenced
   for the lowest entry (object or alias) that was matched.


.. exception:: ADMINLIMIT_EXCEEDED

.. exception:: AFFECTS_MULTIPLE_DSAS

.. exception:: ALIAS_DEREF_PROBLEM

   A problem was encountered when dereferencing an alias.
   (Sets the :const:`matched` field.)

.. exception:: ALIAS_PROBLEM

   An alias in the directory points to a nonexistent entry.
   (Sets the :const:`matched` field.)

.. exception:: ALREADY_EXISTS

   The entry already exists. E.g. the *dn* specified with :meth:`add()`
   already exists in the DIT.

.. exception:: AUTH_UNKNOWN

   The authentication method specified to :meth:`bind()` is not known.

.. exception:: BUSY

   The DSA is busy.

.. exception:: CLIENT_LOOP

.. exception:: COMPARE_FALSE

   A compare operation returned false.
   (This exception should never be seen because :meth:`compare()` returns
   a boolean result.)

.. exception:: COMPARE_TRUE

   A compare operation returned true.
   (This exception should never be seen because :meth:`compare()` returns
   a boolean result.)

.. exception:: CONFIDENTIALITY_REQUIRED

   Indicates that the session is not protected by a protocol such
   as Transport Layer Security (TLS), which provides session
   confidentiality.

.. exception:: CONNECT_ERROR

.. exception:: CONSTRAINT_VIOLATION

   An attribute value specified or an operation started violates some
   server-side constraint
   (e.g., a postalAddress has too many lines or a line that is too long
   or a password is expired).

.. exception:: CONTROL_NOT_FOUND

.. exception:: DECODING_ERROR

   An error was encountered decoding a result from the LDAP server.

.. exception:: ENCODING_ERROR

   An error was encountered encoding parameters to send to the LDAP server.

.. exception:: FILTER_ERROR

   An invalid filter was supplied to :meth:`search()`
   (e.g. unbalanced parentheses).

.. exception:: INAPPROPRIATE_AUTH

   Inappropriate authentication was specified (e.g. :const:`AUTH_SIMPLE`
   was specified and the entry does not have a userPassword attribute).

.. exception:: INAPPROPRIATE_MATCHING

   Filter type not supported for the specified attribute.

.. exception:: INSUFFICIENT_ACCESS

   The user has insufficient access to perform the operation.

.. exception:: INVALID_CREDENTIALS

   Invalid credentials were presented during :meth:`bind()` or
   :meth:`simple_bind()`.
   (e.g., the wrong password).

.. exception:: INVALID_DN_SYNTAX

   A syntactically invalid DN was specified. (Sets the :const:`matched` field.)

.. exception:: INVALID_SYNTAX

   An attribute value specified by the client did not comply to the
   syntax defined in the server-side schema.

.. exception:: IS_LEAF

   The object specified is a leaf of the diretcory tree.
   Sets the :const:`matched` field of the exception dictionary value.

.. exception:: LOCAL_ERROR

   Some local error occurred. This is usually due to failed memory allocation.

.. exception:: LOOP_DETECT

   A loop was detected.

.. exception:: MORE_RESULTS_TO_RETURN

.. exception:: NAMING_VIOLATION

   A naming violation occurred. This is raised e.g. if the LDAP server
   has constraints about the tree naming.

.. exception:: NO_OBJECT_CLASS_MODS

   Modifying the objectClass attribute as requested is not allowed
   (e.g. modifying structural object class of existing entry).

.. exception:: NOT_ALLOWED_ON_NONLEAF

   The operation is not allowed on a non-leaf object.

.. exception:: NOT_ALLOWED_ON_RDN

   The operation is not allowed on an RDN.

.. exception:: NOT_SUPPORTED

.. exception:: NO_MEMORY

.. exception:: NO_OBJECT_CLASS_MODS

   Object class modifications are not allowed.

.. exception:: NO_RESULTS_RETURNED

.. exception:: NO_SUCH_ATTRIBUTE

   The attribute type specified does not exist in the entry.

.. exception:: NO_SUCH_OBJECT

   The specified object does not exist in the directory.
   Sets the :const:`matched` field of the exception dictionary value.

.. exception:: OBJECT_CLASS_VIOLATION

   An object class violation occurred when the LDAP server checked
   the data sent by the client against the server-side schema
   (e.g. a "must" attribute was missing in the entry data).

.. exception:: OPERATIONS_ERROR

   An operations error occurred.

.. exception:: OTHER

   An unclassified error occurred.

.. exception:: PARAM_ERROR

   An ldap routine was called with a bad parameter.

.. exception:: PARTIAL_RESULTS

   Partial results only returned. This exception is raised if
   a referral is received when using LDAPv2.
   (This exception should never be seen with LDAPv3.)

.. exception:: PROTOCOL_ERROR

   A violation of the LDAP protocol was detected.

.. exception:: RESULTS_TOO_LARGE

   The result does not fit into a UDP packet. This happens only when using
   UDP-based CLDAP (connection-less LDAP) which is not supported anyway.

.. exception:: SASL_BIND_IN_PROGRESS

.. exception:: SERVER_DOWN

   The  LDAP  library  can't  contact the LDAP server.

.. exception:: SIZELIMIT_EXCEEDED

   An LDAP size limit was exceeded.
   This could be due to a ``sizelimit`` configuration on the LDAP server.

.. exception:: STRONG_AUTH_NOT_SUPPORTED

   The LDAP server does not support strong authentication.

.. exception:: STRONG_AUTH_REQUIRED

   Strong authentication is required  for the operation.

.. exception:: TIMELIMIT_EXCEEDED

   An LDAP time limit was exceeded.

.. exception:: TIMEOUT

   A timelimit was exceeded while waiting for a result from the server.

.. exception:: TYPE_OR_VALUE_EXISTS

   An  attribute  type or attribute value specified already 
   exists in the entry.

.. exception:: UNAVAILABLE

   The DSA is unavailable.

.. exception:: UNAVAILABLE_CRITICAL_EXTENSION

   Indicates that the LDAP server was unable to satisfy a request
   because one or more critical extensions were not available. Either
   the server does not support the control or the control is not appropriate
   for the operation type.

.. exception:: UNDEFINED_TYPE

   An attribute type used is not defined in the server-side schema.

.. exception:: UNWILLING_TO_PERFORM

   The  DSA is  unwilling to perform the operation.

.. exception:: USER_CANCELLED

   The operation was cancelled via the :meth:`abandon()` method.

The above exceptions are raised when a result code from an underlying API
call does not indicate success.


.. _ldap-objects:

LDAPObject class
================

.. % This label is generally useful for referencing this section, but is
.. % also used to give a filename when generating HTML.

.. %\noindent

Instances of :class:`ldap.LDAPObject` are returned by :func:`initialize()`
and :func:`open()` (deprecated). The connection is automatically unbound
and closed  when the LDAP object is deleted.

Arguments for LDAPv3 controls
-----------------------------

The :mod:`ldap.controls` module can be used for constructing and
decoding LDAPv3 controls. These arguments are available in the methods
with names ending in :const:`_ext` or :const:`_ext_s`:

*serverctrls*
  is a list of :class:`LDAPControl` instances sent to the server along
  with the LDAP request (see module :mod:`ldap.controls`). These are
  controls which alter the behaviour of the server when processing the
  request if the control is supported by the server. The effect of controls
  might differ depending on the type of LDAP request or controls might not
  be applicable with certain LDAP requests at all.

*clientctrls*
  is a list of :class:`LDAPControl` instances passed to the
  client API and alter the behaviour of the client when processing the
  request.


Sending LDAP requests
---------------------

Most methods on LDAP objects initiate an asynchronous request to the
LDAP server and return a message id that can be used later to retrieve
the result with :meth:`result()`.

Methods with names ending in :const:`_s` are the synchronous form 
and wait for and return with the server's result, or with
:const:`None` if no data is expected.

LDAPObject instances have the following methods:

.. %%------------------------------------------------------------
.. %% abandon
.. method:: LDAPObject.abandon(msgid)

.. method:: LDAPObject.abandon_ext(msgid [, serverctrls=None [, clientctrls=None]])

   Abandons an LDAP operation in progress without waiting for a LDAP response.
   The *msgid* argument should be the message ID of an outstanding LDAP
   operation as returned by the asynchronous methods :meth:`search()`, :meth:`modify()`, etc. 
   The caller can expect that the result of an abandoned operation will not be
   returned from a future call to :meth:`result()`.

   *serverctrls* and *clientctrls* like described above.


.. %%------------------------------------------------------------
.. %% add
.. method:: LDAPObject.add(dn, modlist)

   .. % -> int

.. method:: LDAPObject.add_s(dn, modlist)

   .. % -> None

.. method:: LDAPObject.add_ext(dn, modlist [, serverctrls=None [, clientctrls=None]]) 

   .. % -> int

.. method:: LDAPObject.add_ext_s(dn, modlist [, serverctrls=None [, clientctrls=None]])

   ..  % -> None

   Performs an LDAP add operation. The *dn* argument is the distinguished
   name (DN) of the entry to add, and *modlist* is a list of attributes to be
   added. The modlist is similar the one passed to :meth:`modify()`, except that the
   operation integer is omitted from the tuples in modlist. You might want to
   look into sub-module \refmodule{ldap.modlist} for generating the modlist.

   The asynchronous methods :meth:`add()` and :meth:`add_ext()`
   return the message ID of the initiated request.
   
   *serverctrls* and *clientctrls* like described above.

.. %%------------------------------------------------------------
.. %% bind
.. method:: LDAPObject.bind(who, cred, method)

   .. % -> int

.. method:: LDAPObject.bind_s(who, cred, method)

   .. % -> None

.. method:: LDAPObject.simple_bind([who='' [, cred='']])

   .. % -> int

.. method:: LDAPObject.simple_bind_s([who='' [, cred='']])

   ..  % -> None

   After an LDAP object is created, and before any other operations can be
   attempted over the connection, a bind operation must be performed.

   This method attempts to bind with the LDAP server using 
   either simple authentication, or Kerberos (if available).
   The first and most general method, :meth:`bind()`,
   takes a third parameter, *method* which can currently solely
   be :const:`AUTH_SIMPLE`.
   

.. %%------------------------------------------------------------
.. %% sasl_interactive_bind_s
.. method:: LDAPObject.sasl_interactive_bind_s(who, auth)

   .. % -> None

   This call is used to bind to the directory with a SASL bind request.


.. %%------------------------------------------------------------
.. %% cancel
.. method:: LDAPObject.cancel( cancelid, [, serverctrls=None [, clientctrls=None]])

   Send cancels extended operation for an LDAP operation specified by *cancelid*.
   The *cancelid* should be the message id of an outstanding LDAP operation as returned
   by the asynchronous methods search(), modify() etc.  The caller
   can expect that the result of an abandoned operation will not be
   returned from a future call to :meth:`result()`.
   In opposite to :meth:`abandon()` this extended operation gets an result from
   the server and thus should be preferred if the server supports it.

   *serverctrls* and *clientctrls* like described above.

   :rfc:`3909` - Lightweight Directory Access Protocol (LDAP): Cancel Operation


.. %%------------------------------------------------------------
.. %% compare
.. method:: LDAPObject.compare(dn, attr, value)

   .. % -> int

.. method:: LDAPObject.compare_s(dn, attr, value)

   .. % -> tuple

.. method:: LDAPObject.compare_ext(dn, attr, value [, serverctrls=None [, clientctrls=None]])

   .. % -> int

.. method:: LDAPObject.compare_ext_s(dn, attr, value [, serverctrls=None [, clientctrls=None]])

   .. % -> tuple

   Perform an LDAP comparison between the attribute named *attr* of 
   entry *dn*, and the value *value*. The synchronous forms
   returns :const:`0` for false, or :const:`1` for true.
   The asynchronous forms returns the message ID of the initiated request, 
   and the result of the asynchronous compare can be obtained using 
   :meth:`result()`.  

   Note that the asynchronous technique yields the answer
   by raising the exception objects :exc:`ldap.COMPARE_TRUE` or
   :exc:`ldap.COMPARE_FALSE`.

   *serverctrls* and *clientctrls* like described above.

   .. note::
   
      A design fault in the LDAP API prevents *value* 
      from containing nul characters.

.. %%------------------------------------------------------------
.. %% delete
.. method:: LDAPObject.delete(dn)

   .. % -> int

.. method::  LDAPObject.delete_s(dn)

   .. % -> None

.. method:: LDAPObject.delete_ext(dn [, serverctrls=None [, clientctrls=None]])

   .. % -> int

.. method:: LDAPObject.delete_ext_s(dn [, serverctrls=None [, clientctrls=None]])

   .. % -> None

   Performs an LDAP delete operation on *dn*. The asynchronous form
   returns the message id of the initiated request, and the result can be obtained
   from a subsequent call to :meth:`result()`.

   *serverctrls* and *clientctrls* like described above.

.. %%------------------------------------------------------------
.. %% modify
.. method:: LDAPObject.modify(dn, modlist)

   .. % -> int

.. method:: LDAPObject.modify_s(dn, modlist)

   .. % -> None

.. method:: LDAPObject.modify_ext(dn, modlist [, serverctrls=None [, clientctrls=None]])

   .. % -> int

.. method:: LDAPObject.modify_ext_s(dn, modlist [, serverctrls=None [, clientctrls=None]])

   .. % -> None

   Performs an LDAP modify operation on an entry's attributes. 
   The *dn* argument is the distinguished name (DN) of the entry to modify,
   and *modlist* is a list of modifications to make to that entry.

   Each element in the list *modlist* should be a tuple of the form 
   *(mod_op,mod_type,mod_vals)*,
   where *mod_op* indicates the operation (one of :const:`MOD_ADD`, 
   :const:`MOD_DELETE`, or :const:`MOD_REPLACE`),
   *mod_type* is a string indicating the attribute type name, and 
   *mod_vals* is either a string value or a list of string values to add, 
   delete or replace respectively.  For the delete operation, *mod_vals*
   may be :const:`None` indicating that all attributes are to be deleted.

   *serverctrls* and *clientctrls* like described above.

   The asynchronous methods :meth:`modify()` and :meth:`modify_ext()`
   return the message ID of the initiated request.

   You might want to look into sub-module :mod:`ldap.modlist` for
   generating *modlist*.


.. %%------------------------------------------------------------
.. %% modrdn
.. method:: LDAPObject.modrdn(dn, newrdn [, delold=1])

   .. %-> int


.. method::  LDAPObject.modrdn_s(dn, newrdn [, delold=1])

   .. % -> None

   Perform a ``modify RDN`` operation, (i.e. a renaming operation).
   These routines take *dn* (the DN of the entry whose RDN is to be changed,
   and *newrdn*, the new RDN to give to the entry. The optional parameter
   *delold* is used to specify whether the old RDN should be kept as an
   attribute of the entry or not.
   The asynchronous version returns the initiated message id.

   This operation is emulated by :meth:`rename()` and :meth:`rename_s()` methods
   since the modrdn2* routines in the C library are deprecated.


.. %%------------------------------------------------------------
.. %% passwd
.. method:: LDAPObject.passwd(user, oldpw, newpw [, serverctrls=None [, clientctrls=None]])

   .. %-> int

.. method:: LDAPObject.passwd_s(user, oldpw, newpw [, serverctrls=None [, clientctrls=None]])

   .. % -> None

   Perform a ``LDAP Password Modify Extended Operation`` operation
   on the entry specified by *user*.
   The old password in *oldpw* is replaced with the new
   password in *newpw* by a LDAP server supporting this operation.

   *serverctrls* and *clientctrls* like described above.

   The asynchronous version returns the initiated message id.

   .. seealso::

      :rfc:`3062` - LDAP Password Modify Extended Operation



.. %%------------------------------------------------------------
.. %% rename
.. method:: LDAPObject.rename(dn, newrdn [, newsuperior=None [, delold=1 [, serverctrls=None [, clientctrls=None]]]])

   ..  %-> int

.. method:: LDAPObject.rename_s(dn, newrdn [, newsuperior=None [, delold=1 [, serverctrls=None [, clientctrls=None]]]])

   ..  % -> None

   Perform a ``Rename`` operation, (i.e. a renaming operation).
   These routines take *dn* (the DN of the entry whose RDN is to be changed,
   and *newrdn*, the new RDN to give to the entry.
   The optional parameter *newsuperior* is used to specify
   a new parent DN for moving an entry in the tree
   (not all LDAP servers support this).
   The optional parameter *delold* is used to specify
   whether the old RDN should be kept as an attribute of the entry or not.

   *serverctrls* and *clientctrls* like described above.

.. %%------------------------------------------------------------
.. %% result
.. method:: LDAPObject.result([msgid=RES_ANY [, all=1 [, timeout=-1]]])

   .. % -> 2-tuple

   This method is used to wait for and return the result of an operation
   previously initiated by one of the LDAP *asynchronous* operations
   (eg :meth:`search()`, :meth:`modify()`, etc.) 

   The *msgid* parameter is the integer identifier returned by that method. 
   The identifier is guaranteed to be unique across an LDAP session,
   and tells the :meth:`result()` method to request the result of that
   specific operation.

   If a result is desired from any one of the in-progress operations,
   *msgid* should be specified as the constant :const:`RES_ANY`
   and the method :meth:`result2()` should be used instead.

   The *all* parameter only has meaning for :meth:`search()` responses
   and is used to select whether a single entry of the search
   response should be returned, or to wait for all the results
   of the search before returning.

   A search response is made up of zero or more search entries
   followed by a search result. If *all* is 0, search entries will
   be returned one at a time as they come in, via separate calls
   to :meth:`result()`. If all is 1, the search response will be returned
   in its entirety, i.e. after all entries and the final search
   result have been received.

   For *all* set to 0, result tuples
   trickle in (with the same message id), and with the result types
   :const:`RES_SEARCH_ENTRY` and :const:`RES_SEARCH_REFERENCE`,
   until the final result which has a result type of :const:`RES_SEARCH_RESULT`
   and a (usually) empty data field.  When all is set to 1, only one result is returned,
   with a result type of RES_SEARCH_RESULT, and all the result tuples
   listed in the data field.

   The *timeout* parameter is a limit on the number of seconds that the
   method will wait for a response from the server. 
   If *timeout* is negative (which is the default),
   the method will wait indefinitely for a response.
   The timeout can be expressed as a floating-point value, and
   a value of :const:`0` effects a poll.
   If a timeout does occur, a :exc:`ldap.TIMEOUT` exception is raised,
   unless polling, in which case ``(None, None)`` is returned.

   The :meth:`result()` method returns a tuple of the form 
   ``(result-type, result-data)``.
   The first element, ``result-type`` is a string, being one of
   these module constants:
   :const:`RES_BIND`, :const:`RES_SEARCH_ENTRY`,
   :const:`RES_SEARCH_REFERENCE`, :const:`RES_SEARCH_RESULT`, 
   :const:`RES_MODIFY`, :const:`RES_ADD`, :const:`RES_DELETE`, 
   :const:`RES_MODRDN`, or :const:`RES_COMPARE`.

   If *all* is :const:`0`, one response at a time is returned on
   each call to :meth:`result()`, with termination indicated by 
   ``result-data`` being an empty list.

   See :meth:`search()` for a description of the search result's 
   ``result-data``, otherwise the ``result-data`` is normally meaningless.



.. %%------------------------------------------------------------
.. %% result2
.. method:: LDAPObject.result2([msgid=RES_ANY [, all=1 [, timeout=-1]]])

   .. % -> 3-tuple

   This method behaves almost exactly like :meth:`result()`. But
   it returns a 3-tuple also containing the message id of the
   outstanding LDAP operation a particular result message belongs
   to. This is especially handy if one needs to dispatch results
   obtained with ``msgid=``:const:`RES_ANY` to several consumer
   threads which invoked a particular LDAP operation.


.. %%------------------------------------------------------------
.. %% result3
.. method:: LDAPObject.result3([msgid=RES_ANY [, all=1 [, timeout=-1]]])

   .. % -> 4-tuple

   This method behaves almost exactly like :meth:`result2()`. But it
   returns an extra item in the tuple, the decoded server controls.


.. %%------------------------------------------------------------
.. %% search
.. method:: LDAPObject.search(base, scope [,filterstr='(objectClass=*)' [, attrlist=None [, attrsonly=0]]])
   
   ..  %->int

.. method:: LDAPObject.search_s(base, scope [,filterstr='(objectClass=*)' [, attrlist=None [, attrsonly=0]]])

   .. %->list|None

.. method:: LDAPObject.search_st(base, scope [,filterstr='(objectClass=*)' [, attrlist=None [, attrsonly=0 [, timeout=-1]]]])

.. method:: LDAPObject.search_ext(base, scope [,filterstr='(objectClass=*)' [, attrlist=None [, attrsonly=0 [, serverctrls=None [, clientctrls=None [, timeout=-1 [, sizelimit=0]]]]]]])

   ..  %->int

.. method:: LDAPObject.search_ext_s(base, scope [,filterstr='(objectClass=*)' [, attrlist=None [, attrsonly=0 [, serverctrls=None [, clientctrls=None [, timeout=-1 [, sizelimit=0]]]]]]])

   .. %->list|None

   Perform an LDAP search operation, with *base* as the DN of the entry
   at which to start the search, *scope* being one of 
   :const:`SCOPE_BASE` (to search the object itself), 
   :const:`SCOPE_ONELEVEL` (to search the object's immediate children), or
   :const:`SCOPE_SUBTREE` (to search the object and all its descendants).

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
   function :cfunc:`ldap_get_dn()`, which may raise an exception if the
   DN is malformed.

   If *attrsonly* is non-zero, the values of *attrs* will be meaningless
   (they are not transmitted in the result).

   The retrieved attributes can be limited with the *attrlist* parameter.
   If *attrlist* is :const:`None`, all the attributes of each entry are returned.

   *serverctrls* and *clientctrls* like described above.

   The synchronous form with timeout, :meth:`search_st()` or :meth:`search_ext_s()`,
   will block for at most *timeout* seconds (or indefinitely if *timeout*
   is negative). A :exc:`ldap.TIMEOUT` exception is raised if no result is received
   within the specified time.

   The amount of search results retrieved can be limited with the
   *sizelimit* parameter when using :meth:`search_ext()`
   or :meth:`search_ext_s()` (client-side search limit). If non-zero
   not more than *sizelimit* results are returned by the server.



.. %%------------------------------------------------------------
.. %% start_tls_s
.. method:: LDAPObject.start_tls_s()

   .. % -> None    

    Negotiate TLS with server. The ``version`` attribute must have been
    set to :const:`VERSION3` (which it is by default) before calling this method.
    If TLS could not be started an exception will be raised.

   .. seealso::

      :rfc:`2830` - Lightweight Directory Access Protocol (v3): Extension for Transport Layer Security



.. %%------------------------------------------------------------
.. %% unbind
.. method:: LDAPObject.unbind()

   .. % -> int

.. method:: LDAPObject.unbind_s()

   .. % -> None

.. method:: LDAPObject.unbind_ext([, serverctrls=None [, clientctrls=None]])

   .. % -> int

.. method:: LDAPObject.unbind_ext_s([, serverctrls=None [, clientctrls=None]])

   .. % -> None

   This call is used to unbind from the directory, terminate the
   current association, and free resources. Once called, the connection to the
   LDAP server is closed and the LDAP object is marked invalid.
   Further invocation of methods on the object will yield exceptions.

   *serverctrls* and *clientctrls* like described above.

   These methods are all synchronous in nature.


.. %%------------------------------------------------------------
.. %% whoami_s
.. method:: LDAPObject.whoami_s()

   .. % -> string

   This synchronous method implements the LDAP "Who Am I?"
   extended operation.

   It is useful for finding out to find out which identity
   is assumed by the LDAP server after a SASL bind.

   .. seealso::

      :rfc:`4532` - Lightweight Directory Access Protocol (LDAP) "Who am I?" Operation


Connection-specific LDAP options
--------------------------------

.. %%------------------------------------------------------------
.. %% get_option
.. method:: LDAPObject.get_option(option)

   .. % -> None

   This method returns the value of the LDAPObject option
   specified by *option*.


.. %%------------------------------------------------------------
.. %% set_option
.. method:: LDAPObject.set_option(option, invalue)

   .. % -> None

   This method sets the value of the LDAPObject option
   specified by *option* to *invalue*.


Object attributes
-----------------

If the underlying library provides enough information,
each LDAP object will also have the following attributes.
These attributes are mutable unless described as read-only.

.. %%------------------------------------------------------------
.. %% deref
.. attribute:: LDAPObject.deref

   .. % -> int

   Controls whether aliases are automatically dereferenced.
   This must be one of :const:`DEREF_NEVER`, :const:`DEREF_SEARCHING`, :const:`DEREF_FINDING`,
   or :const:`DEREF_ALWAYS`.
   This option is mapped to option constant :const:`OPT_DEREF`
   and used in the underlying OpenLDAP lib.


.. %%------------------------------------------------------------
.. %% network_timeout
.. attribute:: LDAPObject.network_timeout

   .. % -> int

   Limit on waiting for a network response, in seconds. 
   Defaults to :const:`NO_LIMIT`.
   This option is mapped to option constant :const:`OPT_NETWORK_TIMEOUT`
   and used in the underlying OpenLDAP lib.


.. %%------------------------------------------------------------
.. %% protocol_version
.. attribute:: LDAPObject.protocol_version

   .. % -> int

   Version of LDAP in use (either :const:`VERSION2` for LDAPv2
   or :const:`VERSION3` for LDAPv3).
   This option is mapped to option constant :const:`OPT_PROTOCOL_VERSION`
   and used in the underlying OpenLDAP lib.

   .. note::

      It is highly recommended to set the protocol version after establishing
      a LDAP connection with :func:`initialize()` and before submitting
      the first request.
      

.. %%------------------------------------------------------------
.. %% sizelimit
.. attribute:: LDAPObject.sizelimit

   .. % -> int

   Limit on size of message to receive from server. 
   Defaults to :const:`NO_LIMIT`.
   This option is mapped to option constant :const:`OPT_SIZELIMIT`
   and used in the underlying OpenLDAP lib. Its use is deprecated
   in favour of *sizelimit* parameter when using :meth:`search_ext()`.


.. %%------------------------------------------------------------
.. %% timelimit
.. attribute:: LDAPObject.timelimit

   .. % -> int

   Limit on waiting for any response, in seconds. 
   Defaults to :const:`NO_LIMIT`.
   This option is mapped to option constant :const:`OPT_TIMELIMIT`
   and used in the underlying OpenLDAP lib. Its use is deprecated
   in favour of using *timeout*.


.. %%------------------------------------------------------------
.. %% timeout
.. attribute:: LDAPObject.timeout

   .. % -> int

   Limit on waiting for any response, in seconds. 
   Defaults to :const:`NO_LIMIT`.
   This option is used in the wrapper module.


.. _ldap-example:

Example
=======

The following example demonstrates how to open a connection to an
LDAP server using the :mod:`ldap` module and invoke a synchronous
subtree search.

>>> import ldap
>>> l = ldap.initialize('ldap://localhost:1390')
>>> l.search_s('ou=Testing,dc=stroeder,dc=de',ldap.SCOPE_SUBTREE,'(cn=fred*)',['cn','mail'])
[('cn=Fred Feuerstein,ou=Testing,dc=stroeder,dc=de', {'cn': ['Fred Feuerstein']})]
>>> r = l.search_s('ou=Testing,dc=stroeder,dc=de',ldap.SCOPE_SUBTREE,'(objectClass=*)',['cn','mail'])
>>> for dn,entry in r:
>>>   print 'Processing',repr(dn)
>>>   handle_ldap_entry(entry)



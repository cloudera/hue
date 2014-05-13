#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Utilities for Thrift

import Queue
import logging
import socket
import threading
import time
import sasl
import sys

from thrift.Thrift import TType, TApplicationException
from thrift.transport.TSocket import TSocket
from thrift.transport.TSSLSocket import TSSLSocket
from thrift.transport.TTransport import TBufferedTransport, TFramedTransport, TMemoryBuffer,\
                                        TTransportException
from thrift.protocol.TBinaryProtocol import TBinaryProtocol
from thrift.protocol.TMultiplexedProtocol import TMultiplexedProtocol
from desktop.lib.python_util import create_synchronous_io_multiplexer
from desktop.lib.thrift_sasl import TSaslClientTransport
from desktop.lib.exceptions import StructuredException, StructuredThriftTransportException

# The maximum depth that we will recurse through a "jsonable" structure
# while converting to thrift. This prevents us from infinite recursion
# in the case of circular references.
MAX_RECURSION_DEPTH = 50

# When a thrift call finishes, the level at which we log its duration
# depends on the number of millis the call took.
WARN_LEVEL_CALL_DURATION_MS = 5000
INFO_LEVEL_CALL_DURATION_MS = 1000

class LifoQueue(Queue.Queue):
    '''
    Variant of Queue that retrieves most recently added entries first.

    This LIFO Queue is included in python2.7 (or 2.6) and later,
    but it's a simple subclass, so we "backport" it here.
    '''

    def _init(self, maxsize):
        self.queue = []
        self.maxsize = maxsize

    def _qsize(self, len=len):
        return len(self.queue)

    def _put(self, item):
        self.queue.append(item)

    def _get(self):
        return self.queue.pop()

class ConnectionConfig(object):
  """ Struct-like class encapsulating the configuration of a Thrift client. """
  def __init__(self, klass, host, port, service_name,
               use_sasl=False,
               use_ssl=False,
               kerberos_principal="thrift",
               mechanism='GSSAPI',
               username='hue',
	       password='hue',
               ca_certs=None,
               keyfile=None,
               certfile=None,
               validate=False,
               timeout_seconds=45,
               transport='buffered',
               multiple=False):
    """
    @param klass The thrift client class
    @param host Host to connect to
    @param port Port to connect to
    @param service_name A human-readable name to describe the service
    @param use_sasl If true, will use KERBEROS or PLAIN over SASL to authenticate
    @param use_ssl If true, will use ca_certs, keyfile, and certfile to create TLS connection
    @param mechanism: GSSAPI or PLAIN if SASL
    @param username: username if PLAIN SASL or LDAP only
    @param password: password if PLAIN LDAP only
    @param kerberos_principal The Kerberos service name to connect to.
              NOTE: for a service like fooservice/foo.blah.com@REALM only
              specify "fooservice", NOT the full principal name.
    @param ca_certs certificate authority certificates
    @param keyfile private key file
    @param certfile certificate file
    @param validate Validate the certificate received from server
    @param timeout_seconds Timeout for thrift calls
    @param transport string representation of thrift transport to use
    @param multiple Whether Use MultiplexedProtocol
    """
    self.klass = klass
    self.host = host
    self.port = port
    self.service_name = service_name
    self.use_sasl = use_sasl
    self.use_ssl = use_ssl
    self.mechanism = mechanism
    self.username = username
    self.password = password
    self.kerberos_principal = kerberos_principal
    self.ca_certs = ca_certs
    self.keyfile = keyfile
    self.certfile = certfile
    self.validate = validate
    self.timeout_seconds = timeout_seconds
    self.transport = transport
    self.multiple = multiple

  def __str__(self):
    return ', '.join(map(str, [self.klass, self.host, self.port, self.service_name, self.use_sasl, self.kerberos_principal, self.timeout_seconds,
                               self.mechanism, self.username, self.use_ssl, self.ca_certs, self.keyfile, self.certfile, self.validate, self.transport, self.multiple]))

class ConnectionPooler(object):
  """
  Thread-safe connection pooling for thrift. (With about 3 changes,
  this could be made general).

  Each host,port pair has a connection pool set associated with it.
  Clients can get connections from this pool and then block when
  none are available.

  A connection is a 'SuperClient', which deals with timeout errors
  automatically so we don't have to worry about refreshing a stale pool.

  We could be fancier here - we could reclaim clients ourselves without
  relying on them to be returned but that would increase complexity. The
  benefit would be not having to hit the connection pool on every client call.
  """

  def __init__(self, poolsize=10):
    self.pooldict = {}
    self.poolsize = poolsize
    self.dictlock = threading.Lock()

  def get_client(self, conf,
                 get_client_timeout=None):
    """
    Could block while we wait for the pool to become non-empty.

    @param get_client_timeout: how long (in seconds) to wait on the pool
                               to get a client before failing
    """
    # First up, check to see if we have a pool for this endpoint
    if _get_pool_key(conf) not in self.pooldict:
      # Uh-oh, we need to initialise the queue. Take the dict lock.
      # Note that this is 'double-checked locking'.

      # The reason this pattern doesn't work in Java is that the write to the dict
      # may get issued before the construction of the Queue due to new Queue(..) not
      # being atomic. However in Python this becomes CALL_FUNCTION and STORE_FAST,
      # therefore as long as a) the function doesn't get inlined b) Python's bytecode
      # generator doesn't move the write to q before the function completes there's no
      # way for another thread to observe a partially constructed queue.

      # I haven't found a reference for the Python memory model, so I'm leaving this comment
      # here in case unladen-swallow or something breaks this assumption of correctness.

      self.dictlock.acquire()
      try:
        if _get_pool_key(conf) not in self.pooldict:
          q = LifoQueue(self.poolsize)
          self.pooldict[_get_pool_key(conf)] = q
          for i in xrange(self.poolsize):
            client = construct_superclient(conf)
            client.CID = i
            q.put(client, False)
      finally:
        self.dictlock.release()

    connection = None

    start_pool_get_time = time.time()
    has_waited_for = 0

    while connection is None:
      if get_client_timeout is not None:
        this_round_timeout = max(min(get_client_timeout - has_waited_for, 1), 0)
      else:
        this_round_timeout = None

      try:
        connection = self.pooldict[_get_pool_key(conf)].get(
          block=True, timeout=this_round_timeout)
      except Queue.Empty:
        has_waited_for = time.time() - start_pool_get_time
        if get_client_timeout is not None and has_waited_for > get_client_timeout:
          raise socket.timeout(
            ("Timed out after %.2f seconds waiting to retrieve a " +
             "%s client from the pool.") % (has_waited_for, conf.service_name))
        logging.warn("Waited %d seconds for a thrift client to %s:%d" %
          (has_waited_for, conf.host, conf.port))

    return connection

  def return_client(self, conf, client):
    """
    Add a client back to its pool. It's an error to
    pass back a client that was not retrieved from a pool, and
    you might well get an exception for doing so.
    """
    self.pooldict[_get_pool_key(conf)].put(client)

def _get_pool_key(conf):
  """
  Given a ConnectionConfig, return the tuple used as the key in the dictionary
  of connections by the ConnectionPooler class.
  """
  return (conf.klass, conf.host, conf.port)

def construct_superclient(conf):
  """
  Constructs a thrift client, lazily.
  """
  service, protocol, transport = connect_to_thrift(conf)
  return SuperClient(service, transport, timeout_seconds=conf.timeout_seconds)


def connect_to_thrift(conf):
  """
  Connect to a thrift endpoint as determined by the 'conf' parameter.
  Note that this does *not* open the transport.

  Returns a tuple of (service, protocol, transport)
  """
  if conf.use_ssl:
    sock = TSSLSocket(conf.host, conf.port, validate=conf.validate, ca_certs=conf.ca_certs, keyfile=conf.keyfile, certfile=conf.certfile)
  else:
    sock = TSocket(conf.host, conf.port)
  if conf.timeout_seconds:
    # Thrift trivia: You can do this after the fact with
    # _grab_transport_from_wrapper(self.wrapped.transport).setTimeout(seconds*1000)
    sock.setTimeout(conf.timeout_seconds * 1000.0)
  if conf.use_sasl:
    def sasl_factory():
      saslc = sasl.Client()
      saslc.setAttr("host", str(conf.host))
      saslc.setAttr("service", str(conf.kerberos_principal))
      if conf.mechanism == 'PLAIN':
        saslc.setAttr("username", str(conf.username))
	saslc.setAttr("password", str(conf.password)) # defaults to hue for a non-empty string unless using ldap
      saslc.init()
      return saslc

    transport = TSaslClientTransport(sasl_factory, conf.mechanism, sock)
  elif conf.transport == 'framed':
    transport = TFramedTransport(sock)
  else:
    transport = TBufferedTransport(sock)

  protocol = TBinaryProtocol(transport)
  if conf.multiple:
    protocol = TMultiplexedProtocol(protocol, conf.service_name)
  service = conf.klass(protocol)
  return service, protocol, transport


_connection_pool = ConnectionPooler()

def get_client(klass, host, port, service_name, **kwargs):
  conf = ConnectionConfig(klass, host, port, service_name, **kwargs)
  return PooledClient(conf)

def _grab_transport_from_wrapper(outer_transport):
  if isinstance(outer_transport, TBufferedTransport):
    return outer_transport._TBufferedTransport__trans
  elif isinstance(outer_transport, TSaslClientTransport):
    return outer_transport._trans
  elif isinstance(outer_transport, TFramedTransport):
    return outer_transport._TFramedTransport__trans
  else:
    raise Exception("Unknown transport type: " + outer_transport.__class__)

class PooledClient(object):
  """
  A wrapper for a SuperClient
  """
  def __init__(self, conf):
    self.conf = conf

  def __getattr__(self, attr):
    if attr in self.__dict__:
      return self.__dict__[attr]

    # Fetch the thrift client from the pool
    superclient = _connection_pool.get_client(self.conf)
    res = getattr(superclient, attr)

    if not callable(res):
      # It's a simple attribute. We can put the superclient back in the pool.
      _connection_pool.return_client(self.conf, superclient)
      return res
    else:
      # It's gonna be a thrift call. Add wrapping logic to reopen the transport,
      # and return the connection to the pool when done.
      def wrapper(*args, **kwargs):
        try:
          try:
            # Poke it to see if it's closed on the other end. This can happen if a connection
            # sits in the connection pool longer than the read timeout of the server.
            sock = _grab_transport_from_wrapper(superclient.transport).handle
            if sock and create_synchronous_io_multiplexer().read([sock]):
              # the socket is readable, meaning there is either data from a previous call
              # (i.e our protocol is out of sync), or the connection was shut down on the
              # remote side. Either way, we need to reopen the connection.
              # If the socket was closed remotely, btw, socket.read() will return
              # an empty string.  This is a fairly normal condition, btw, since
              # there are timeouts on both the server and client sides.
              superclient.transport.close()
              superclient.transport.open()

            superclient.set_timeout(self.conf.timeout_seconds)
            return res(*args, **kwargs)
          except TApplicationException, e:
            # Unknown thrift exception... typically IO errors
            logging.info("Thrift saw an application exception: " + str(e), exc_info=False)
            raise StructuredException('THRIFTAPPLICATION', str(e), data=None, error_code=502)
          except socket.error, e:
            logging.info("Thrift saw a socket error: " + str(e), exc_info=False)
            raise StructuredException('THRIFTSOCKET', str(e), data=None, error_code=502)
          except TTransportException, e:
            logging.info("Thrift saw a transport exception: " + str(e), exc_info=False)
            raise StructuredThriftTransportException(e, error_code=502)
          except Exception, e:
            # Stack tends to be only noisy here.
            logging.info("Thrift saw exception: " + str(e), exc_info=False)
            raise
        finally:
          _connection_pool.return_client(self.conf, superclient)
      wrapper.attr = attr # Save the name of the attribute as it is replaced by 'wrapper'
      return wrapper


class SuperClient(object):
  """A wrapper for a Thrift Client that causes it to automatically
  reconnect on failure.

  TODO(todd): get this into the Thrift lib
  """

  def __init__(self, wrapped_client, transport, timeout_seconds=None):
    self.wrapped = wrapped_client
    self.transport = transport
    self.timeout_seconds = timeout_seconds

  def __getattr__(self, attr):
    if attr in self.__dict__:
      return self.__dict__[attr]

    res = getattr(self.wrapped, attr)
    if not hasattr(res, '__call__'):
      return res
    def wrapper(*args, **kwargs):
      tries_left = 3
      while tries_left:
        # clear exception state so our re-raise can't reraise something
        # old. This isn't strictly necessary, but feels safer.
        sys.exc_clear()
        try:
          if not self.transport.isOpen():
            self.transport.open()
          st = time.time()
          logging.debug("Thrift call: %s.%s(args=%s, kwargs=%s)"
            % (str(self.wrapped.__class__), attr, repr(args), repr(kwargs)))
          ret = res(*args, **kwargs)
          log_msg = repr(ret)
          if len(log_msg) > 1000:
            log_msg = log_msg[0:1000] + "..."
          duration = time.time() - st

          # Log the duration at different levels, depending on how long
          # it took.
          logmsg = "Thrift call %s.%s returned in %dms: %s" % (
            str(self.wrapped.__class__), attr, duration*1000, log_msg)
          if duration >= WARN_LEVEL_CALL_DURATION_MS:
            logging.warn(logmsg)
          elif duration >= INFO_LEVEL_CALL_DURATION_MS:
            logging.info(logmsg)
          else:
            logging.debug(logmsg)

          return ret
        except socket.error, e:
          pass
        except TTransportException, e:
          pass
        except Exception, e:
          logging.exception("Thrift saw exception (this may be expected).")
          raise
        self.transport.close()

        if isinstance(e, socket.timeout):
          logging.warn("Not retrying thrift call %s due to socket timeout" % attr)
          raise
        else:
          tries_left -= 1
          if tries_left:
            logging.info("Thrift exception; retrying: " + str(e), exc_info=0)
      logging.warn("Out of retries for thrift call: " + attr)
      raise
    return wrapper

  def set_timeout(self, timeout_seconds):
    if timeout_seconds != self.timeout_seconds:
      self.timeout_seconds = timeout_seconds
      # ugh, None is a valid timeout
      if self.timeout_seconds is not None:
        _grab_transport_from_wrapper(self.transport).setTimeout(self.timeout_seconds * 1000)
      else:
        _grab_transport_from_wrapper(self.transport).setTimeout(None)

def simpler_string(thrift_obj):
  """
  Strips out nulls and empty arrays from the string representation.

  TODO(philip): I don't believe this appropriately recurses into
  lists.
  TODO(philip): Implement a max-string-length argument to
  truncate (with "...") long strings.
  TODO(philip): Use this in SuperClient, above.
  """
  L = []
  for key, value in thrift_obj.__dict__.iteritems():
    if value is None:
      continue
    if hasattr(value, "thrift_spec"):
      L.append("%s=%s" % (key, simpler_string(value)))
    else:
      L.append("%s=%r" % (key, value))

  return '%s(%s)' % (thrift_obj.__class__.__name__, ', '.join(L))

def from_bytes(klass, data):
  """Returns thrift object from a string, using standard binary representation."""
  obj = klass()
  b = TMemoryBuffer(data)
  p = TBinaryProtocol(b)
  obj.read(p)
  return obj

def to_bytes(obj):
  """Creates the standard binary representation of a thrift object."""
  b = TMemoryBuffer()
  p = TBinaryProtocol(b)
  obj.write(p)
  return b.getvalue()

def thrift2json(tft):
  """
  Convert a thrift structure to a JSON compatible dictionary
  by recursing over the dictionary. Will not handle cycles in
  the reference graph!

  Note also that this is not the same as the Thrift C++ and Java bindings
  for a "TJSONProtocol".  This will not survive thrift field renames.

  The set implementation will only work for primitive types.  The Thrift
  wiki suggests (http://wiki.apache.org/thrift/ThriftTypes):
      N.B.: For maximal compatibility, the key type for map should be a basic type
      rather than a struct or container type. There are some languages which do not
      support more complex key types in their native map types. In addition the
      JSON protocol only supports key types that are base types.
  I believe this ought to be true for sets, as well.
  """
  if isinstance(tft,type(None)):
    return None
  if isinstance(tft,(float,int,long,complex,basestring)):
    return tft
  if isinstance(tft,dict):
    d = {}
    for key, val in tft.iteritems():
      d[key] = thrift2json(val)
    return d
  if isinstance(tft,list):
    return [thrift2json(x) for x in tft]
  if isinstance(tft, set):
    return dict( (x, True) for x in tft )

  json = {}
  d = {}
  if hasattr(tft,"__dict__"):
    d = tft.__dict__
  else:
    if hasattr(tft,"__slots__"):
      d = tft.__slots__
    else:
      return {}
  for k in d:
    v = getattr(tft, k)
    json[k] = thrift2json(v)
  return json

def _jsonable2thrift_helper(jsonable, type_enum, spec_args, default, recursion_depth=0):
  """
  Recursive implementation method of jsonable2thrift.

  type_enum corresponds to TType.  spec_args is part of the
  thrift_spec explained in Thrift's code generator.  See
  compiler/cpp/src/generate/t_py_generator.cc .
  default is the default value.

  This method is aggressive about checking types and limits.
  It does not however warn about keys appearing in dictionaries
  that are not represented in the Thrift struct.

  Note that jsonable representations of Thrift objects
  are friendly to read, but they are not backwards-compatible,
  because they are indexed by field names, and not field ids.
  """
  if recursion_depth > MAX_RECURSION_DEPTH:
    raise Exception("Maximum recursion depth exceeded in jsonable2thrift.")

  if jsonable is None:
    return default

  def check_bits(jsonable, bits):
    """
    Helper function to check bounds.

    The Thrift IDL specifies how many bytes numbers can be, and always uses
    signed integers.  This makes sure that the Thrift struct that comes out
    conforms to that schema.
    """
    check_type(jsonable, (int, long))
    # For example, for 8 bits, this yields the range -128 to 127 (inclusive).
    min_val = -1 << (bits-1)
    max_val = (1 << (bits-1)) - 1
    assert min_val <= jsonable, "Value %d <= %d minimum value" % (jsonable, min_val)
    assert max_val >= jsonable, "Value %d >= %d maxium value" % (jsonable, max_val)

  def check_type(jsonable, expected):
    assert isinstance(jsonable, expected), "Value %s has wrong type.  Expected %s." % (repr(jsonable), repr(expected))

  if type_enum == TType.BOOL:
    check_type(jsonable, bool)
    return jsonable

  elif type_enum == TType.BYTE:
    check_bits(jsonable, 8)
    return jsonable

  elif type_enum == TType.I16:
    check_bits(jsonable, 16)
    return jsonable

  elif type_enum == TType.I32:
    check_bits(jsonable, 32)
    return jsonable

  elif type_enum == TType.I64:
    check_bits(jsonable, 64)
    return jsonable

  elif type_enum == TType.DOUBLE:
    check_type(jsonable, float)
    return jsonable

  elif type_enum == TType.STRING:
    assert isinstance(jsonable, basestring)
    return jsonable

  elif type_enum == TType.STRUCT:
    check_type(jsonable, dict)
    thrift_type, thrift_spec = spec_args
    out = thrift_type()
    # Recurse in, field-by-field
    for spec in thrift_spec:
      if spec is None:
        # thrift_spec is indexed by thrift tag id, so None shows up
        continue
      _, cur_type_enum, cur_name, cur_spec_args, cur_default = spec
      value = _jsonable2thrift_helper(jsonable.get(cur_name),
        cur_type_enum, cur_spec_args, cur_default, recursion_depth + 1)
      setattr(out, cur_name, value)
    return out

  elif type_enum == TType.MAP:
    check_type(jsonable, dict)
    key_type_enum, key_spec_args, val_type_enum, val_spec_args = spec_args
    out = dict()
    for k_jsonable, v_jsonable in jsonable.iteritems():
      k = _jsonable2thrift_helper(k_jsonable, key_type_enum, key_spec_args, None, recursion_depth + 1)
      v = _jsonable2thrift_helper(v_jsonable, val_type_enum, val_spec_args, None, recursion_depth + 1)
      out[k] = v
    return out

  elif type_enum == TType.SET:
    # JSON doesn't have native set; set is represented
    # as a map with values True.
    set_type_enum, set_spec_args = spec_args
    out = set()
    for k, v in jsonable.iteritems():
      assert v is True, "Expected set value to be True.  Got: %s" % repr(v)
      out.add(_jsonable2thrift_helper(k, set_type_enum, set_spec_args, None, recursion_depth + 1))
    return out

  elif type_enum == TType.LIST:
    check_type(jsonable, list)
    list_type_enum, list_spec_args = spec_args
    out = list()
    for x in jsonable:
      out.append(_jsonable2thrift_helper(x, list_type_enum, list_spec_args, None, recursion_depth + 1))
    return out

  else:
    raise Exception("Unrecognized type: %s.  Value was %s." % (repr(type_enum), repr(jsonable)))

def jsonable2thrift(jsonable, thrift_class):
  """
  Converts a JSON-able x that represents a thrift struct
  into the struct.  JSON-ables are dicts, lists,
  and primitives, containing the same.  Typically
  they are the result of parsing a JSON string.

  This is compatible with thrift2json.
  """
  return _jsonable2thrift_helper(
    jsonable,
    TType.STRUCT,
    (thrift_class, thrift_class.thrift_spec),
    default=None,
    recursion_depth=0
  )

def enum_as_sequence(enum):
  """
  Returns an array whose entries are the names of the
  enum's constants. We might want this to select a value
  at random, for example. Once Thrift-generated enum classes
  get better, the need for this function might go away.

  If the class has any members which don't begin with __, they
  will be returned. This is therefore perhaps a little flaky.

  Arguments:
  - `enum`: The class of a Thrift-generated enum
  """
  return filter(lambda x: not x.startswith("__")
                and  x not in ["_VALUES_TO_NAMES", "_NAMES_TO_VALUES"],dir(enum))

def fixup_enums(obj, name_class_map, suffix="AsString"):
  """
  Relying on Todd's THRIFT-546 patch, this function adds a string
  representation of an enum to an object that contains only the integer
  version. Callers must supply two arrays of the same length: the list of
  classes that the enums belongs to, and the list of names of attributes to
  lookup and translate.

  This is destructive - it uses setattr.
  """
  for n in name_class_map.keys():
    c = name_class_map[n]
    setattr(obj, n + suffix, c._VALUES_TO_NAMES[getattr(obj,n)])
  return obj

def is_thrift_struct(o):
  return hasattr(o.__class__, "thrift_spec")

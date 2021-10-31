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

from __future__ import absolute_import
from builtins import range
from builtins import object
import logging
import os
import socket
import sys
import threading
import time
import unittest

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock

gen_py_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "gen-py"))
if not gen_py_path in sys.path:
  sys.path.insert(1, gen_py_path)

from djangothrift_test_gen import TestService
from djangothrift_test_gen.ttypes import TestStruct, TestNesting, TestEnum, TestManyTypes
from nose.tools import assert_equal, assert_true, assert_raises
from thrift.protocol.TBinaryProtocol import TBinaryProtocolFactory
from thrift.server import TServer
from thrift.transport import TSocket
from thrift.transport.TTransport import TBufferedTransportFactory, TTransportException

from desktop.lib import python_util, thrift_util
from desktop.lib.thrift_util import jsonable2thrift, thrift2json, _unpack_guid_secret_in_handle
from desktop.conf import USE_THRIFT_HTTP_JWT
from desktop.lib.django_test_util import make_logged_in_client
from desktop.auth.backend import rewrite_user, find_or_create_user, ensure_has_a_group, create_user

from useradmin.models import User

LOG = logging.getLogger(__name__)


class SimpleThriftServer(object):
  socket_family = socket.AF_INET

  """A simple thrift server impl"""
  def __init__(self):
    self.port = python_util.find_unused_port()
    self.pid = 0

  def ping(self, in_val):
    logging.info('ping')
    return in_val * 2

  def start_server_process(self):
    """
    Starts a test server, returns the (pid, port) pair.

    The server needs to be in a subprocess because we need to run a
    TThreadedServer for the concurrency tests. And the only way to stop a
    TThreadedServer is to kill it. So we can't just use a thread.
    """
    self.pid = os.fork()
    if self.pid != 0:
      logging.info("Started SimpleThriftServer (pid %s) on port %s" %
                   (self.pid, self.port))
      self._ensure_online()
      return

    # Child process runs the thrift server loop
    try:
      processor = TestService.Processor(self)
      transport = TSocket.TServerSocket('localhost', self.port, socket_family=self.socket_family)
      server = TServer.TThreadedServer(processor,
                                       transport,
                                       TBufferedTransportFactory(),
                                       TBinaryProtocolFactory())
      server.serve()
    except:
      LOG.exception('failed to start thrift server')
      sys.exit(1)

  def _ensure_online(self):
    """Ensure that the child server is online"""
    deadline = time.time() + 60
    logging.debug("Socket Info: " + str(socket.getaddrinfo('localhost', self.port, socket.AF_UNSPEC, socket.SOCK_STREAM)))
    while time.time() < deadline:
      logging.info("Waiting for service to come online")
      try:
        ping_s = socket.socket(self.socket_family, socket.SOCK_STREAM)
        ping_s.connect(('localhost', self.port))
        ping_s.close()
        return
      except:
        LOG.exception('failed to connect to child server')
        _, status = os.waitpid(self.pid, os.WNOHANG)
        if status != 0:
          logging.info("SimpleThriftServer child process exited with %s" % (status,))
        time.sleep(5)

    logging.info("SimpleThriftServer took too long to come online")
    self.stop_server_process()

  def stop_server_process(self):
    """Stop the server"""
    if self.pid == 0:
      return

    try:
      logging.info("Stopping SimpleThriftServer (pid %s)" % (self.pid,))
      os.kill(self.pid, 15)
    except Exception as ex:
      logging.exception("(Potentially ok) Exception while stopping server")
    os.waitpid(self.pid, 0)
    self.pid = 0


class TestWithThriftServer(object):
  @classmethod
  def setup_class(cls):
    cls.server = SimpleThriftServer()
    cls.server.start_server_process()
    cls.client = thrift_util.get_client(TestService.Client,
                                        'localhost',
                                        cls.server.port,
                                        'Hue Unit Test Client',
                                        timeout_seconds=1)

  @classmethod
  def teardown_class(cls):
    cls.server.stop_server_process()

  def test_basic_operation(self):
    assert_equal(10, self.client.ping(5))

  def test_connection_race(self):
    class Racer(threading.Thread):
      def __init__(self, client, n_iter, begin):
        threading.Thread.__init__(self)
        self.setName("Racer%s" % (begin,))
        self.client = client
        self.n_iter = n_iter
        self.begin = begin
        self.errors = []

      def run(self):
        for i in range(self.begin, self.begin + self.n_iter):
          res = self.client.ping(i)
          if i * 2 != res:
            self.errors.append(i)

    racers = []
    for i in range(10):
      racer = Racer(self.client, n_iter=30, begin=(i * 100))
      racers.append(racer)
      racer.start()

    for racer in racers:
      racer.join()
      assert_equal(0, len(racer.errors))

class ThriftUtilTest(unittest.TestCase):
  def test_simpler_string(self):
    struct = TestStruct()
    self.assertEquals("TestStruct()",
      thrift_util.simpler_string(struct))
    struct.a = "hello world"
    self.assertEquals("TestStruct(a='hello world')",
      thrift_util.simpler_string(struct))
    struct.a = ""
    struct.b = 12345
    self.assertEquals("TestStruct(a='', b=12345)",
      thrift_util.simpler_string(struct))
    struct.a = None
    self.assertEquals("TestStruct(b=12345)",
      thrift_util.simpler_string(struct))

    nested = TestNesting()
    nested.nested_struct = struct
    self.assertEquals("TestNesting(nested_struct=TestStruct(b=12345))",
      thrift_util.simpler_string(nested))

  def test_to_from_bytes(self):
    struct = TestStruct()
    struct.a = "hello world"
    struct.b = 12345

    self.assertEquals(struct, thrift_util.from_bytes(TestStruct, thrift_util.to_bytes(struct)))
    self.assertEquals(thrift_util.to_bytes(struct),
      thrift_util.to_bytes(thrift_util.from_bytes(TestStruct, thrift_util.to_bytes(struct))))

  def test_empty_string_vs_none(self):
    struct1 = TestStruct()
    struct2 = TestStruct()
    struct2.a = ""

    self.assertNotEquals(thrift_util.to_bytes(struct1), thrift_util.to_bytes(struct2))
    self.assertNotEquals(struct1, struct2)

  def test_enum_as_sequence(self):
    seq = thrift_util.enum_as_sequence(TestEnum)
    self.assertEquals(len(seq), 3)
    self.assertEquals(sorted(seq), sorted(['ENUM_ONE', 'ENUM_TWO', 'ENUM_THREE']))

  def test_is_thrift_struct(self):
    self.assertTrue(thrift_util.is_thrift_struct(TestStruct()))
    self.assertFalse(thrift_util.is_thrift_struct("a string"))

  def test_fixup_enums(self):
    enum = TestEnum()
    struct1 = TestStruct()
    self.assertTrue(hasattr(enum, "_VALUES_TO_NAMES"))
    struct1.myenum = 0
    thrift_util.fixup_enums(struct1, {"myenum": TestEnum})
    self.assertTrue(hasattr(struct1, "myenumAsString"))
    self.assertEquals(struct1.myenumAsString, 'ENUM_ONE')

  def test_unpack_guid_secret_in_handle(self):
    if sys.version_info[0] > 2:
      hive_handle = ("(TGetTablesReq(sessionHandle=TSessionHandle(sessionId=THandleIdentifier(guid=%s, secret=%s)), catalogName=None,"
      " schemaName='default', tableName='customers', tableTypes=None),"
      ")") % (str(b'N\xc5\xed\x14k\xbeI\xda\xb9\x14\xe7\xf2\x9a\xb7\xf0\xa5'), str(b']s(\xb5\xf6ZO\x03\x99\x955\xacl\xb4\x98\xae'))

      self.assertEqual(_unpack_guid_secret_in_handle(hive_handle), ("(TGetTablesReq(sessionHandle=TSessionHandle(sessionId="
      "THandleIdentifier(guid=da49be6b14edc54e:a5f0b79af2e714b9, secret=034f5af6b528735d:ae98b46cac359599)), catalogName=None, "
      "schemaName=\'default\', tableName=\'customers\', tableTypes=None),)"))

      impala_handle = ("(TExecuteStatementReq(sessionHandle=TSessionHandle(sessionId=THandleIdentifier(guid=%s, secret=%s)), "
      "statement=b\'USE `default`\', confOverlay={\'QUERY_TIMEOUT_S\': \'300\'}, runAsync=False)"
      ",)") % (str(b'\xc4\xccnI\xf1\xbdJ\xc3\xb2\n\xd5[9\xe1Mr'), str(b'\xb0\x9d\xfd\x82\x94%L\xae\x9ch$f=\xfa{\xd0'))

      self.assertEqual(_unpack_guid_secret_in_handle(impala_handle), ("(TExecuteStatementReq(sessionHandle=TSessionHandle("
      "sessionId=THandleIdentifier(guid=c34abdf1496eccc4:724de1395bd50ab2, secret=ae4c259482fd9db0:d07bfa3d6624689c)), "
      "statement=b\'USE `default`\', confOverlay={\'QUERY_TIMEOUT_S\': \'300\'}, runAsync=False),)"))
    else:
      hive_handle = ("(TExecuteStatementReq(confOverlay={}, sessionHandle=TSessionHandle(sessionId=THandleIdentifier("
      "secret=\'\x1aOYj\xf3\x86M\x95\xbb\xc8\xe9/;\xb0{9\', guid=\'\x86\xa6$\xb2\xb8\xdaF\xbd\xbd\xf5\xc5\xf4\xcb\x96\x03<\')), "
      'runAsync=True, statement="SELECT \'Hello World!\'"),)')

      self.assertEqual(_unpack_guid_secret_in_handle(hive_handle), ("(TExecuteStatementReq(confOverlay={}, sessionHandle=TSessionHandle("
      "sessionId=THandleIdentifier(secret=954d86f36a594f1a:397bb03b2fe9c8bb, guid=bd46dab8b224a686:3c0396cbf4c5f5bd)), runAsync=True, "
      'statement="SELECT \'Hello World!\'"),)'))

      impala_handle = ("(TGetTablesReq(schemaName=u\'default\', sessionHandle=TSessionHandle(sessionId=THandleIdentifier(secret="
      "\'\x7f\x98\x97s\xe1\xa8G\xf4\x8a\x8a\\r\x0e6\xc2\xee\xf0\', guid=\'\xfa\xb0/\x04 \xfeDX\x99\xfcq\xff2\x07\x02\xfe\')), "
      "tableName=u\'customers\', tableTypes=None, catalogName=None),)")

      self.assertEqual(_unpack_guid_secret_in_handle(impala_handle), ("(TGetTablesReq(schemaName=u\'default\', sessionHandle="
      "TSessionHandle(sessionId=THandleIdentifier(secret=f447a8e17397987f:f0eec2360e0d8a8a, guid=5844fe20042fb0fa:fe020732ff71fc99)),"
      " tableName=u\'customers\', tableTypes=None, catalogName=None),)"))

    # Following should be added to test, but fails because eval doesn't handle null bytes
    # impala_handle = ("(TGetTablesReq(schemaName=u\'default\', sessionHandle=TSessionHandle(sessionId=THandleIdentifier(secret="
    # "\'\x7f\x98\x97s\xe1\xa8G\xf4\x8a\x8a\\r\x0e6\xc2\xee\xf0\', guid=\'\xd23\xfa\x150\xf5D\x91\x00\x00\x00\x00\xd7\xef\x91\x00\')), "
    # "tableName=u\'customers\', tableTypes=None, catalogName=None),)")

    # self.assertEqual(_unpack_guid_secret_in_handle(impala_handle), ("(TGetTablesReq(schemaName=u\'default\', "
    # "sessionHandle=TSessionHandle(sessionId=THandleIdentifier(secret=f447a8e17397987f:f0eec2360e0d8a8a, "
    # "guid=9144f53015fa33d2:0091efd700000000)), tableName=u\'customers\', tableTypes=None, catalogName=None),)"))

class TestJsonable2Thrift(unittest.TestCase):
  """
  Tests a handful of permutations of jsonable2thrift.
  """
  def assertBackAndForth(self, obj):
    """
    Checks that conversion to json and back is idempotent.
    """
    jsonable = thrift2json(obj)
    back = jsonable2thrift(jsonable, type(obj))
    self.assertEquals(obj, back)

  def test_basic_types(self):
    def help(key, value, expect_failure=False):
      x = TestManyTypes()
      setattr(x, key, value)
      self.assertBackAndForth(x)
    help("a_bool", True)
    help("a_bool", False)
    help("a_byte", 123)
    help("a_i16", 1234)
    help("a_i32", 1 << 30)
    help("a_i64", 1 << 62)
    help("a_double", 3.1415)
    help("a_string", "hello there")
    help("a_binary", "bye bye")

  def test_default(self):
    x = jsonable2thrift(dict(), TestManyTypes)
    self.assertEquals(TestManyTypes(a_string_with_default="the_default"), x)

  def test_struct(self):
    x = TestManyTypes()
    inner = TestStruct(a="foo")
    x.a_struct = inner
    self.assertBackAndForth(x)

  def test_set(self):
    x = TestManyTypes()
    x.a_set = set([1, 2, 3, 4, 5])
    self.assertBackAndForth(x)

  def test_list(self):
    x = TestManyTypes()
    x.a_list = [TestStruct(b=i) for i in range(4)]
    self.assertBackAndForth(x)

  def test_map(self):
    x = TestManyTypes()
    x.a_map = dict([(i, TestStruct(b=i)) for i in range(4)])
    self.assertBackAndForth(x)

  def test_limits(self):
    """
    Checks that bound checking works.
    """
    self.assertRaises(AssertionError, jsonable2thrift,
      dict(a_byte=128), TestManyTypes)
    self.assertRaises(AssertionError, jsonable2thrift,
      dict(a_byte=-129), TestManyTypes)
    self.assertRaises(AssertionError, jsonable2thrift,
      dict(a_byte="not_a_number"), TestManyTypes)

  def test_list_of_strings(self):
    """
    Tests unicode and non-unicode strings.

    (This test arose as a bug.)
    """
    self.assertBackAndForth(TestManyTypes(a_string_list=["alpha", "beta"]))
    self.assertBackAndForth(TestManyTypes(a_string_list=[u"alpha", u"beta"]))


class TestSuperClient(unittest.TestCase):

  def test_wrapper_no_retry(self):
    wrapped_client, transport = Mock(), Mock()
    wrapped_client.my_call = Mock(
      side_effect=TTransportException(message='read operation timed out')
    )

    client = thrift_util.SuperClient(wrapped_client, transport)

    with self.assertRaises(TTransportException):
      client.my_call()
      # Could check output for "Not retrying thrift call my_call due to socket timeout"


  def test_wrapper_with_retry(self):
    wrapped_client, transport = Mock(), Mock()
    wrapped_client.my_call = Mock(
      side_effect=TTransportException(message='some error')
    )

    client = thrift_util.SuperClient(wrapped_client, transport)

    with self.assertRaises(TTransportException):
      client.my_call()
      # Could check output for several "Thrift exception; retrying: some error"


class TestThriftJWT(unittest.TestCase):
  def setUp(self):
    self.sample_token = "some_jwt_token"

    self.client = make_logged_in_client(username="test_user", groupname="default", recreate=True, is_superuser=False)
    self.user = rewrite_user(User.objects.get(username="test_user"))


  def test_jwt_thrift(self):
    with patch('desktop.lib.thrift_util.TBinaryProtocol'):
      with patch('desktop.lib.thrift_util.TBufferedTransport'):
        with patch('desktop.lib.thrift_util.TBufferedTransport'):
          with patch('desktop.lib.thrift_util.THttpClient.set_bearer_auth') as set_bearer_auth:

            self.user.profile.update_data({'jwt_access_token': self.sample_token})
            self.user.profile.save()

            reset = USE_THRIFT_HTTP_JWT.set_for_testing(True)

            conf = Mock(
              klass=Mock(),
              username="test_user",
              transport_mode='http',
              timeout_seconds=None,
              use_sasl=None,
              http_url='some_http_url'
            )

            try:
              service, protocol, transport = thrift_util.connect_to_thrift(conf)
              set_bearer_auth.assert_called_with('some_jwt_token')
            finally:
              reset()


  def test_jwt_thrift_exceptions(self):
    with patch('desktop.lib.thrift_util.TBinaryProtocol'):
      with patch('desktop.lib.thrift_util.TBufferedTransport'):
        with patch('desktop.lib.thrift_util.TBufferedTransport'):
          with patch('desktop.lib.thrift_util.THttpClient.set_bearer_auth') as set_bearer_auth:
            reset = USE_THRIFT_HTTP_JWT.set_for_testing(True)

            try:
              # When token not stored in user profile
              conf = Mock(
                klass=Mock(),
                username="test_user",
                transport_mode='http',
                timeout_seconds=None,
                use_sasl=None,
                http_url='some_http_url'
              )

              assert_raises(Exception, thrift_util.connect_to_thrift, conf)

              # When user not found
              self.user.profile.update_data({'jwt_access_token': self.sample_token})
              self.user.profile.save()

              conf = Mock(
                klass=Mock(),
                username="test_not_user",
                transport_mode='http',
                timeout_seconds=None,
                use_sasl=None,
                http_url='some_http_url'
              )
              assert_raises(Exception, thrift_util.connect_to_thrift, conf)
            finally:
              reset()


if __name__ == '__main__':
  unittest.main()

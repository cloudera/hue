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
import os
import socket
import sys
import threading
import unittest
import time
import logging

gen_py_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "gen-py"))
if not gen_py_path in sys.path:
  sys.path.insert(1, gen_py_path)

from djangothrift_test_gen.ttypes import TestStruct, TestNesting, TestEnum, TestManyTypes
from djangothrift_test_gen import TestService

import thrift_util
from thrift_util import jsonable2thrift, thrift2json

from thrift.server import TServer
from thrift.transport import TSocket

from nose.tools import assert_equal
from nose.plugins.skip import SkipTest

class TestSuperClient(unittest.TestCase):
  class TestHandler(object):
    def ping(self, in_val):
      return in_val * 2

    @classmethod
    def start_server_thread(cls):
      """Starts a test server, returns the ServerThread object started."""
      handler = cls()
      processor = TestService.Processor(handler)
      transport = TSocket.TServerSocket(0)
      server = TServer.TSimpleServer(processor, transport)

      class ServerThread(threading.Thread):
        def __init__(self, server):
          threading.Thread.__init__(self)
          self.server = server
          self.stopped = False

        def run(self):
          try:
            logging.info("About to serve...")
            self.server.serve()
            logging.info("Done serving...")
          except:
            assert self.stopped

        def get_port(self):
          return self.server.serverTransport.handle.getsockname()[1]

        def stop(self):
          # This closes the listening socket, but the current accept()
          # call keeps going. So we have to ping that port
          self.stopped = True
          port = self.get_port()
          self.server.serverTransport.close() # hopefully this works?
          ping_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          ping_s.connect(('localhost', port))
          ping_s.close()
          logging.info("Waiting for server to stop")
          self.join()

      thr = ServerThread(server)
      thr.start()
      while not transport.isOpen():
        logging.info("Waiting for server to start")
        time.sleep(0.1)

      return thr

  # TODO(todd) I couldn't get this to work after much effort.
  # Thrift's server doesn't really have a reasonable lifecycle
  # interface, so hard to bring up a thrift server inside a test.
  def test_basic_operation(self):
    raise SkipTest()
    server = TestSuperClient.TestHandler.start_server_thread()
    try:
      test_client = thrift_util.get_client(TestService.Client,
                                           '127.0.0.1',
                                           server.get_port(),
                                           timeout_seconds=1)
      assert_equal(10, test_client.ping(5))
    finally:
      server.stop()

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
    self.assertEquals(len(seq),3)
    self.assertEquals(sorted(seq),sorted(['ENUM_ONE','ENUM_TWO','ENUM_THREE']))

  def test_is_thrift_struct(self):
    self.assertTrue(thrift_util.is_thrift_struct(TestStruct()))
    self.assertFalse(thrift_util.is_thrift_struct("a string"))

  def test_fixup_enums(self):
    enum = TestEnum()
    struct1 = TestStruct()
    self.assertTrue(hasattr(enum,"_VALUES_TO_NAMES"))
    struct1.myenum = 0
    thrift_util.fixup_enums(struct1,{"myenum":TestEnum})
    self.assertTrue(hasattr(struct1,"myenumAsString"))
    self.assertEquals(struct1.myenumAsString,'ENUM_ONE')

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
    x.a_set=set([1,2,3,4,5])
    self.assertBackAndForth(x)

  def test_list(self):
    x = TestManyTypes()
    x.a_list = [ TestStruct(b=i) for i in range(4) ]
    self.assertBackAndForth(x)

  def test_map(self):
    x = TestManyTypes()
    x.a_map = dict([ (i, TestStruct(b=i)) for i in range(4) ])
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

if __name__ == '__main__':
  unittest.main()

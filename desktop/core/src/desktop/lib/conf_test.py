#!/usr/bin/python
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

import configobj
from cStringIO import StringIO
import logging
import re

from desktop.lib.conf import *
from nose.tools import assert_true, assert_false, assert_equals, assert_raises

def my_dynamic_default():
  """
  Calculates a sum
  """
  return 3 + 4

class TestConfig(object):
  """Unit tests for the configuration module."""

  # Some test configurations to load
  CONF_ONE="""
  foo = 123
  list=a,b,c
  """
  CONF_TWO = """
  req = 345
  hello.greeting = "hello world"

  [clusters]
  [[clustera]]
  host="localhost"

  [[clusterb]]
  host="philipscomputer"
  """

  @classmethod
  def setup_class(cls):
    logging.basicConfig(level=logging.DEBUG)
    cls.conf = ConfigSection(
      members=dict(
        FOO           = Config("foo",
                               help="A vanilla configuration param",
                               type=int),
        BAR           = Config("bar", default=456,
                               help="Config with default",
                               type=int),
        REQ           = Config("req", required=True,
                               help="A required config",
                               type=int),
        OPT_NOT_THERE = Config("blahblah"),
        REQ_NOT_THERE = Config("blah", required=True, help="Another required"),
        PRIVATE_CONFIG= Config("dontseeme",private=True),
        DYNAMIC_DEF   = Config("dynamic_default", dynamic_default=my_dynamic_default,
                               type=int),
        SOME_SECTION  = ConfigSection(
          "some_section",
          private=True,
          members=dict(BAZ = Config("baz", default="baz_default"))),
        LIST          = Config("list", type=list),
        CLUSTERS      = UnspecifiedConfigSection(
          "clusters",
          help="Details about your Hadoop cluster(s)",
          each=ConfigSection(
            help="Details about a cluster - one section for each.",
            members=dict(HOST = Config("host", help="Hostname for the NN",
                                       required=True),
                         PORT = Config("port", help="Thrift port for the NN",
                                       type=int, default=10090))))))
    cls.conf = cls.conf.bind(
      load_confs([configobj.ConfigObj(infile=StringIO(cls.CONF_ONE)),
                  configobj.ConfigObj(infile=StringIO(cls.CONF_TWO))]),
      prefix='')

  def test_type_safety(self):
    assert_raises(ValueError, Config, key="test_type", type=42)
    assert_raises(ValueError, Config, key="test_type", type=str, default=42)
    assert_raises(ValueError, Config, key="test_type", default=False)
    bool_conf = Config("bool_conf", type=bool)
    assert_true(bool_conf.type == coerce_bool)

  def test_dynamic_default(self):
    assert_equals(7, self.conf.DYNAMIC_DEF.get())

  def test_load(self):
    assert_equals(123, self.conf.FOO.get())
    assert_equals(456, self.conf.BAR.get())
    assert_equals(345, self.conf.REQ.get())

    assert_equals(None, self.conf.OPT_NOT_THERE.get())
    assert_raises(KeyError, self.conf.REQ_NOT_THERE.get)

  def test_list_values(self):
    assert_equals(["a","b","c"], self.conf.LIST.get())

  def test_sections(self):
    assert_equals(2, len(self.conf.CLUSTERS))
    assert_equals(['clustera', 'clusterb'], sorted(self.conf.CLUSTERS.keys()))
    assert_true("clustera" in self.conf.CLUSTERS)
    assert_equals("localhost", self.conf.CLUSTERS['clustera'].HOST.get())
    assert_equals(10090, self.conf.CLUSTERS['clustera'].PORT.get())

  def test_full_key_name(self):
    assert_equals(self.conf.REQ.get_fully_qualifying_key(), 'req')
    assert_equals(self.conf.CLUSTERS.get_fully_qualifying_key(), 'clusters')
    assert_equals(self.conf.CLUSTERS['clustera'].get_fully_qualifying_key(),
                      'clusters.clustera')
    assert_equals(self.conf.CLUSTERS['clustera'].HOST.get_fully_qualifying_key(),
                      'clusters.clustera.host')

  def test_set_for_testing(self):
    # Test base case
    assert_equals(123, self.conf.FOO.get())
    # Override with 456
    close_foo = self.conf.FOO.set_for_testing(456)
    try:
      assert_equals(456, self.conf.FOO.get())
      # Check nested overriding
      close_foo2 = self.conf.FOO.set_for_testing(789)
      try:
        assert_equals(789, self.conf.FOO.get())
      finally:
        close_foo2()

      # Check that we pop the stack appropriately.
      assert_equals(456, self.conf.FOO.get())
      # Check default values
      close_foo3 = self.conf.FOO.set_for_testing(present=False)
      try:
        assert_equals(None, self.conf.FOO.get())
      finally:
        close_foo3()
    finally:
      close_foo()
    # Check that it got set back correctly
    assert_equals(123, self.conf.FOO.get())

    # Test something inside an unspecified config setting with a default
    close = self.conf.CLUSTERS['clustera'].PORT.set_for_testing(123)
    try:
      assert_equals(123, self.conf.CLUSTERS['clustera'].PORT.get())
    finally:
      close()
    assert_equals(10090, self.conf.CLUSTERS['clustera'].PORT.get())

    # Test something inside a config section that wasn't provided in conf file
    assert_equals("baz_default", self.conf.SOME_SECTION.BAZ.get())
    close = self.conf.SOME_SECTION.BAZ.set_for_testing("hello")
    try:
      assert_equals("hello", self.conf.SOME_SECTION.BAZ.get())
    finally:
      close()
    assert_equals("baz_default", self.conf.SOME_SECTION.BAZ.get())


  def test_coerce_bool(self):
    assert_equals(False, coerce_bool(False))
    assert_equals(False, coerce_bool("FaLsE"))
    assert_equals(False, coerce_bool("no"))
    assert_equals(False, coerce_bool("0"))
    assert_equals(True, coerce_bool("TrUe"))
    assert_equals(True, coerce_bool("YES"))
    assert_equals(True, coerce_bool("1"))
    assert_equals(True, coerce_bool(True))
    assert_raises(Exception, coerce_bool, tuple("foo"))

  def test_print_help(self):
    out = StringIO()
    self.conf.print_help(out=out, skip_header=True)
    out = out.getvalue().strip()
    assert_false("dontseeme" in out)
    assert_equals(re.sub("^    (?m)", "", """
    Key: bar (optional)
      Default: 456
      Config with default

    Key: blah (required)
      Another required

    Key: blahblah (optional)
      [no help text provided]

    [clusters]
      Details about your Hadoop cluster(s)

      Consists of some number of sections like:
      [<user specified name>]
        Details about a cluster - one section for each.

        Key: host (required)
          Hostname for the NN

        Key: port (optional)
          Default: 10090
          Thrift port for the NN

    Key: dynamic_default (optional)
      Dynamic default: Calculates a sum
      [no help text provided]

    Key: foo (optional)
      A vanilla configuration param

    Key: list (optional)
      [no help text provided]

    Key: req (required)
      A required config
    """).strip(), out)

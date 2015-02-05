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

import json
import logging
import tempfile

from desktop.redaction.engine import RedactionEngine, \
                                     RedactionRule, \
                                     parse_redaction_policy_from_file
from desktop.redaction.logfilter import add_log_redaction_filter_to_logger
from nose.tools import assert_true, assert_equal, assert_not_equal


class MockLoggingHandler(logging.Handler):
  def __init__(self, *args, **kwargs):
    logging.Handler.__init__(self, *args, **kwargs)

    self.records = []

  def emit(self, record):
    self.records.append(record)

  def reset(self):
    del self.records[:]


class TestRedactionRule(object):
  def test_redaction_rule_works(self):
    rule = RedactionRule('password=', 'password=".*"', 'password="???"')

    test_strings = [
        ('message', 'message'),
        ('password="a password"', 'password="???"'),
        ('before password="a password" after', 'before password="???" after'),
    ]

    for message, redacted_message in test_strings:
      assert_equal(rule.redact(message), redacted_message)

  def test_non_redacted_string_returns_same_string(self):
    rule = RedactionRule('password=', 'password=".*"', 'password="???"')

    message = 'message'
    assert_true(rule.redact(message) is message)

  def test_equality(self):
    rule1 = RedactionRule('password=', 'password=".*"', 'password="???"')
    rule2 = RedactionRule('password=', 'password=".*"', 'password="???"')
    rule3 = RedactionRule('ssn=', 'ssn=\d{3}-\d{2}-\d{4}', 'ssn=XXX-XX-XXXX'),

    assert_equal(rule1, rule2)
    assert_not_equal(rule1, rule3)


  def test_parse_redaction_policy_from_file(self):
    with tempfile.NamedTemporaryFile() as f:
      json.dump({
          'version': 1,
          'rules': [
            {
              'description': 'redact passwords',
              'trigger': 'password=',
              'search': 'password=".*"',
              'replace': 'password="???"',
            },
            {
              'description': 'redact social security numbers',
              'search': '\d{3}-\d{2}-\d{4}',
              'replace': 'XXX-XX-XXXX',
            },
          ]
      }, f)

      f.flush()

      policy = parse_redaction_policy_from_file(f.name)

      assert_equal(policy.rules, [
        RedactionRule(u'password=', u'password=".*"', u'password="???"'),
        RedactionRule(None, u'\d{3}-\d{2}-\d{4}', u'XXX-XX-XXXX'),
      ])


class TestRedactionEngine(object):
  def test_redaction_works(self):
    redaction_engine = RedactionEngine([
      RedactionRule('password=', 'password=".*"', 'password="???"'),
      RedactionRule('ssn=', 'ssn=\d{3}-\d{2}-\d{4}', 'ssn=XXX-XX-XXXX'),
    ])

    test_strings = [
        ('message', 'message'),
        ('password="a password"', 'password="???"'),
        ('before password="a password" after', 'before password="???" after'),
        ('an ssn=123-45-6789', 'an ssn=XXX-XX-XXXX'),
    ]

    for message, redacted_message in test_strings:
      assert_equal(redaction_engine.redact(message), redacted_message)

  def test_equality(self):
    engine1 = RedactionEngine([
        RedactionRule('password=', 'password=".*"', 'password="???"'),
    ])
    engine2 = RedactionEngine([
        RedactionRule('password=', 'password=".*"', 'password="???"'),
    ])
    engine3 = RedactionEngine([
        RedactionRule('ssn=', 'ssn=\d{3}-\d{2}-\d{4}', 'ssn=XXX-XX-XXXX'),
    ])

    assert_equal(engine1, engine2)
    assert_not_equal(engine1, engine3)


class TestRedactionLogFilter(object):

  @classmethod
  def setUpClass(cls):
    cls.logger = logging.getLogger(cls.__name__)

    cls.handler = MockLoggingHandler()
    cls.logger.addHandler(cls.handler)

    engine = RedactionEngine([
      RedactionRule('password=', 'password=".*"', 'password="???"'),
      RedactionRule('ssn=', 'ssn=\d{3}-\d{2}-\d{4}', 'ssn=XXX-XX-XXXX'),
    ])

    add_log_redaction_filter_to_logger(engine, cls.logger)

  @classmethod
  def tearDownClass(cls):
    cls.logger.handlers = []

  def tearDown(self):
    self.handler.reset()

  def test_redaction_filter(self):
    test_strings = [
        {
          'message': 'message',
          'result_message': 'message',
          'result_msg': 'message',
          'result_args': (),
        },
        {
          'message': 'message %s',
          'args': ['an arg'],
          'result_message': 'message an arg',
          'result_msg': 'message %s',
          'result_args': ('an arg',),
        },
        {
          'message': 'password="a password"',
          'result_message': 'password="???"',
        },
        {
          'message': 'password="%s"',
          'args': ['a password'],
          'result_message': 'password="???"',
        },
        {
          'message': 'password=%s',
          'args': ['"a password"'],
          'result_message': 'password="???"',
        },
        {
          'message': 'before password="%s" after',
          'args': ['a password'],
          'result_message': 'before password="???" after',
        },

        {
          'message': 'ssn=%s-%s-%s',
          'args': ['123', '45', '6789'],
          'result_message': 'ssn=XXX-XX-XXXX',
        },
    ]

    for test in test_strings:
      self.logger.debug(test['message'], *test.get('args', ()))

    for test, record in zip(test_strings, self.handler.records):
      assert_equal(record.getMessage(), test['result_message'])
      assert_equal(record.message, test['result_message'])
      assert_equal(record.msg, test.get('result_msg', test['result_message']))
      assert_equal(record.args, test.get('result_args'))

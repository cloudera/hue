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
import os
import random
import re
import tempfile
import threading

from desktop.redaction.engine import RedactionEngine, \
                                     RedactionPolicy, \
                                     RedactionRule, \
                                     parse_redaction_policy_from_file, \
                                     _convert_java_pattern_to_python
from desktop.redaction.logfilter import add_log_redaction_filter_to_logger
from nose.tools import assert_true, assert_equal, assert_not_equal, raises

MESSAGE = "This string is not redacted"

def get_path(filename):
  return os.path.join(os.path.dirname(__file__), 'test_data', filename)


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

  def test_redact_empty_string(self):
    engine = RedactionEngine([
        RedactionRule('password=', 'password=".*"', 'password="???"'),
    ])

    assert_equal(engine.redact(None), None)
    assert_equal(engine.redact(''), '')


class TestRedactionLogFilter(object):

  @classmethod
  def setUpClass(cls):
    cls.logger = logging.getLogger(cls.__name__)

    cls.handler = MockLoggingHandler()
    cls.logger.addHandler(cls.handler)

    policy = RedactionPolicy([
      RedactionRule('password=', 'password=".*"', 'password="???"'),
      RedactionRule('ssn=', 'ssn=\d{3}-\d{2}-\d{4}', 'ssn=XXX-XX-XXXX'),
    ])

    engine = RedactionEngine([policy])

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

  def test_convert_java_pattern_to_python(self):
    assert_equal(_convert_java_pattern_to_python('1-2'), '1-2')
    assert_equal(_convert_java_pattern_to_python('$1-$2'), '\\1-\\2')
    assert_equal(_convert_java_pattern_to_python('\\$1-$2'), '$1-\\2')
    assert_equal(_convert_java_pattern_to_python('\\$$1-$2'), '$\\1-\\2')

  @raises(IOError)
  def test_does_not_exist(self):
    path = get_path('thisfiledoesnotexist.json')
    parse_redaction_policy_from_file(path)

  @raises(IOError)
  def test_is_dir(self):
    path = '/tmp'
    parse_redaction_policy_from_file(path)

  @raises(IOError)
  def test_is_not_json(self):
    path = get_path('not-json.json')
    parse_redaction_policy_from_file(path)

  @raises(ValueError)
  def test_no_version(self):
    path = get_path('no-version.json')
    parse_redaction_policy_from_file(path)

  @raises(ValueError)
  def test_unknown_version(self):
    path = get_path('unknown-version.json')
    parse_redaction_policy_from_file(path)

  @raises(ValueError)
  def test_alpha_version(self):
    path = get_path('alpha-version.json')
    parse_redaction_policy_from_file(path)

  @raises(ValueError)
  def test_no_search(self):
    path = get_path('no-search.json')
    parse_redaction_policy_from_file(path)

  @raises(ValueError)
  def test_no_replace(self):
    path = get_path('no-replace.json')
    parse_redaction_policy_from_file(path)

  @raises(ValueError)
  def test_no_brace(self):
    path = get_path('no-brace.json')
    parse_redaction_policy_from_file(path)

  @raises(re.error)
  def test_bad_regex(self):
    path = get_path('bad-regex.json')
    parse_redaction_policy_from_file(path)

  @raises(ValueError)
  def test_extra_attr(self):
    path = get_path('extra-attr.json')
    parse_redaction_policy_from_file(path)

  def test_empty_file(self):
    path = get_path('empty.json')
    policy = parse_redaction_policy_from_file(path)
    assert_equal(MESSAGE, policy.redact(MESSAGE))

  def test_empty_rules(self):
    path = get_path('empty-rules.json')
    policy = parse_redaction_policy_from_file(path)
    assert_equal(MESSAGE, policy.redact(MESSAGE))

  def test_basic_good1(self):
    path = get_path('good-1.json')
    policy = parse_redaction_policy_from_file(path)
    assert_equal("Hxllx, wxrld", policy.redact("Hello, world"))

  def test_int_version(self):
    path = get_path('verint.json')
    policy = parse_redaction_policy_from_file(path)
    assert_equal("Hxllx, wxrld", policy.redact("Hello, world"))

  def test_real_rules(self):
    path = get_path('real-1.json')
    policy = parse_redaction_policy_from_file(path)

    messages = [
      ("Hello, world", "Hello, world"),
      ("CC 1234-2345-3456-4576", "CC XXXX-XXXX-XXXX-XXXX"),
      ("CC 1234234534654576", "CC XXXXXXXXXXXXXXXX"),
      ("CC 1234,2345,3456,4576", "CC XXXX-XXXX-XXXX-XXXX"),
      ("SSN 123-45-6789", "SSN XXX-XX-XXXX"),
      ("SSN 123456789", "SSN XXXXXXXXX"),
      ("My password=Hello123", "My password=xxxxx"),
      ("Host www.cloudera.com", "Host HOSTNAME.REDACTED"),
      ("www.c1-foo.org rules!", "HOSTNAME.REDACTED rules!"),
      ("IP1 8.8.8.8", "IP1 0.0.0.0"),
      ("IP2 192.168.0.1", "IP2 0.0.0.0"),
      ("My email is myoder@cloudera.com", "My email is email@redacted.host"),
      ("hello.world@ex.x-1.fr is interesting", "email@redacted.host is interesting"),
      ("Multi 1234-2345-3456-4567\nLine 123-45-6789", "Multi XXXX-XXXX-XXXX-XXXX\nLine XXX-XX-XXXX"),
    ]

    for message, redacted_message in messages:
      assert_equal(redacted_message, policy.redact(message))

  def test_huge_rules(self):
    path = get_path('huge-1.json')
    policy = parse_redaction_policy_from_file(path)
    assert_equal("This string is not redadted", policy.redact(MESSAGE))

  def test_back_refs(self):
    path = get_path('replace-1.json')
    policy = parse_redaction_policy_from_file(path)

    messages = [
      ("Hello, world", "Hello, world"),
      ("1234-2345-3456-4576", "XXXX-XXXX-XXXX-4576"),
      ("Words www.gmail.com is cool", "Words HOSTNAME.REDACTED.com is cool"),
      ("short.org", "HOSTNAME.REDACTED.org"),
      ("long.n4me.h-1.co.fr", "HOSTNAME.REDACTED.fr"),
      ("Ping 192.168.0.1", "Ping 0.192.1.168"),
      ("Magic word", "word: Magic word, word"),
    ]

    for message, redacted_message in messages:
      assert_equal(redacted_message, policy.redact(message))

  def test_ordering(self):
    path = get_path('ordering-1.json')
    policy = parse_redaction_policy_from_file(path)

    messages = [
      ("Hello, world", "Hello, world"),
      ("one", "four"),
      ("This one is a nice one", "This four is a nice four"),
      ("Please help me: ten", "Please help me: thirteen"),
      ("HappY abc", "HappY stu"),
    ]

    for message, redacted_message in messages:
      assert_equal(redacted_message, policy.redact(message))

  def test_case_sensitivity(self):
    path = get_path('case-1.json')
    policy = parse_redaction_policy_from_file(path)

    messages = [
      ("Hello, world", "Hello, world"),
      ("Say aAa! aaa! AAAAAA!", "Say bbb! bbb! bbbbbb!"),
      ("I like dddogs. dDd", "I like dddogs. dDd"),
      ("Cccats. Dddogs", "Cccats. eEeogs"),
      ("Trigger fff gGg", "Trigger fff gGg"),
      ("Trigger fFf Ggg", "Trigger fFf Ggg"),
      ("Trigger fFf gGg", "Trigger fFf hHh"),
    ]

    for message, redacted_message in messages:
      assert_equal(redacted_message, policy.redact(message))

  def test_multithreading(self):
    path = get_path('numbers.json')
    policy = parse_redaction_policy_from_file(path)

    assert_equal("asdf####fdas### H#ll# w#rld", policy.redact("asdf1234fdas666 H3ll0 w0rld"))

    errors = []
    lock = threading.Lock()

    regex = re.compile(r"[0-9]")

    class TestThread(threading.Thread):
      def run(self):
        for i in xrange(500):
          message = u''.join(random_utf8_char() for _ in xrange(128))
          redacted_message = policy.redact(message)

          if regex.search(redacted_message):
            with lock:
              errors.append((message, redacted_message))
              break

    threads = []
    for i in xrange(10):
      threads.append(TestThread())

    for thread in threads:
      thread.start()

    for thread in threads:
      thread.join()

    assert_equal(errors, [])

def byte_range(first, last):
    return list(range(first, last+1))

first_values = byte_range(0x00, 0x7F) + byte_range(0xC2, 0xF4)
trailing_values = byte_range(0x80, 0xBF)

def random_utf8_char():
    first = random.choice(first_values)
    if first <= 0x7F:
        value = bytearray([first])
    elif first <= 0xDF:
        value = bytearray([first, random.choice(trailing_values)])
    elif first == 0xE0:
        value = bytearray([first, random.choice(byte_range(0xA0, 0xBF)), random.choice(trailing_values)])
    elif first == 0xED:
        value = bytearray([first, random.choice(byte_range(0x80, 0x9F)), random.choice(trailing_values)])
    elif first <= 0xEF:
        value = bytearray([first, random.choice(trailing_values), random.choice(trailing_values)])
    elif first == 0xF0:
        value = bytearray([first, random.choice(byte_range(0x90, 0xBF)), random.choice(trailing_values), random.choice(trailing_values)])
    elif first <= 0xF3:
        value = bytearray([first, random.choice(trailing_values), random.choice(trailing_values), random.choice(trailing_values)])
    elif first == 0xF4:
        value = bytearray([first, random.choice(byte_range(0x80, 0x8F)), random.choice(trailing_values), random.choice(trailing_values)])

    return value.decode('utf8')

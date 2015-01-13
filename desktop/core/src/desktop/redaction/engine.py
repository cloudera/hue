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

import re


class RedactionEngine(object):
  """
  `RedactionEngine` applies a list of `RedactionRule`s to redact a string.
  """

  def __init__(self, rules=None):
    if rules is None:
      rules = []

    self.rules = rules

  def add_rule(self, rule):
    self.rules.append(rule)

  def add_rules(self, rules):
    self.rules.extend(rules)

  def add_rules_from_string(self, string):
    self.rules.extend(parse_redaction_rules_from_string(string))

  def add_rules_from_file(self, filename):
    self.rules.extend(parse_redaction_rules_from_filename(filename))

  def redact(self, message):
    """
    Apply the redaction rules to this message. If the message was not redacted
    it will return the original string unmodified.
    """

    for rule in self.rules:
      message = rule.redact(message)

    return message

  def is_enabled(self):
    """
    Return if the redaction engine contains any redaction rules.
    """
    return bool(self.rules)

  def __repr__(self):
    return 'RedactionEngine(%r)' % self.rules

  def __eq__(self, other):
    return \
        isinstance(other, self.__class__) and \
        self.rules == other.rules

  def __ne__(self, other):
    return not self == other


class RedactionRule(object):
  """
  `RedactionRule` implements the logic to parse a log message and redact out
  any sensitive information. It does this by searching a log message for a
  `trigger` string. If found, then it will use the specified `regex` to search
  for the sensitive information and replace it with the `redaction_mask`.
  """

  def __init__(self, trigger, regex, redaction_mask):
    self.trigger = trigger
    self.regex = re.compile(regex)
    self.redaction_mask = redaction_mask

  def redact(self, message):
    """
    Perform the message redaction. If the message does not contain the
    `trigger` string then it will return the original string unmodified.
    """

    if self.trigger in message:
      return self.regex.sub(self.redaction_mask, message)
    else:
      return message

  def __repr__(self):
    return 'RedactionRule(%r, %r, %r)' % (
        self.trigger,
        self.regex.pattern,
        self.redaction_mask)

  def __eq__(self, other):
    return \
        isinstance(other, self.__class__) and \
        self.trigger == other.trigger and \
        self.regex == other.regex and \
        self.redaction_mask == other.redaction_mask

  def __ne__(self, other):
    return not self == other


def parse_redaction_rules_from_string(string):
  """
  Parse a string into a `RedactionFilter`, where each rule is separated by
  `||`, and each rule uses the format specified in `parse_one_rule_from_string`.
  """

  return [parse_one_rule_from_string(line.rstrip()) for line in string.split('||')]


def parse_redaction_rules_from_file(filename):
  """
  Parse a file into a `RedactionFilter`, where each line comprises a redaction
  rule string as described in `parse_rules_from_string`.
  """

  with open(filename) as f:
    return [parse_one_rule_from_string(line.rstrip()) for line in f]


def parse_one_rule_from_string(string):
  """
  `parse_one_rule_from_string` parses a `Rule` from a string comprised of:

    [TRIGGER]::[REGEX]::[REDACTION_MASK]

  Where the `TRIGGER` and `REDACTION_MASK` are strings, and `REGEX` is a python
  regular expression.
  """

  trigger, regex, redaction_mask = string.split('::', 3)
  return RedactionRule(trigger, regex, redaction_mask)

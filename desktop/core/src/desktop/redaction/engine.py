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
import re


class RedactionEngine(object):
  """
  `RedactionEngine` applies a list of `RedactionRule`s to redact a string.
  """

  def __init__(self, policies=None):
    if policies is None:
      policies = []

    self.policies = policies

  def add_policy(self, policy):
    self.policies.append(policy)

  def add_policy_from_file(self, filename):
    self.policies.append(parse_redaction_policy_from_filename(filename))

  def redact(self, message):
    """
    Apply the redaction rules to this message. If the message was not redacted
    it will return the original string unmodified.
    """

    for policy in self.policies:
      message = policy.redact(message)

    return message

  def is_enabled(self):
    """
    Return if the redaction engine contains any redaction rules.
    """
    return bool(self.policies)

  def __repr__(self):
    return 'RedactionEngine(%r)' % self.policies

  def __eq__(self, other):
    return \
        isinstance(other, self.__class__) and \
        self.policies == other.policies

  def __ne__(self, other):
    return not self == other


class RedactionPolicy(object):
  def __init__(self, rules):
    self.rules = rules

  def redact(self, message):
    for rule in self.rules:
      message = rule.redact(message)

    return message


class RedactionRule(object):
  """
  `RedactionRule` implements the logic to parse a log message and redact out
  any sensitive information. It does this by searching a log message for a
  `trigger` string. If found, then it will use the specified `regex` to search
  for the sensitive information and replace it with the `redaction_mask`.
  """

  def __init__(self, trigger, search, replace):
    self.trigger = trigger
    self.regex = re.compile(search)
    self.replace = replace

  def redact(self, message):
    """
    Perform the message redaction. If the message does not contain the
    `trigger` string then it will return the original string unmodified.
    """

    if not self.trigger or self.trigger in message:
      return self.regex.sub(self.replace, message)
    else:
      return message

  def __repr__(self):
    return 'RedactionRule(%r, %r, %r)' % (
        self.trigger,
        self.regex.pattern,
        self.replace)

  def __eq__(self, other):
    return \
        isinstance(other, self.__class__) and \
        self.trigger == other.trigger and \
        self.regex == other.regex and \
        self.replace == other.replace

  def __ne__(self, other):
    return not self == other


def parse_redaction_policy_from_file(filename):
  """
  Parse a file into a `RedactionPolicy`, where each line comprises a redaction
  rule string as described in `parse_rules_from_string`.
  """

  with open(filename) as f:
    scheme = json.load(f)

    try:
      version = scheme['version']
    except KeyError:
      raise ValueError('Redaction policy is missing `version` field')

    if version != 1:
      raise ValueError('unknown version %s' % version)

    try:
      rules = scheme['rules']
    except KeyError:
      raise ValueError('Redaction policy is missing `rules` field')

    rules = [parse_one_rule_from_dict(rule) for rule in rules]

    return RedactionPolicy(rules)


def parse_one_rule_from_dict(rule):
  """
  `parse_one_rule_from_dict` parses a `RedactionRule` from a dictionary like:

    {
      "description": "This is the first rule",
      "trigger": "triggerstring 1",
      "search": "regex 1",
      "replace": "replace 1"
    }

  Where the `trigger` and `replace` are strings, and `search` is a python
  regular expression.
  """

  trigger = rule.get('trigger')

  try:
    search = rule['search']
  except KeyError:
    raise ValueError('Redaction rule is missing `search` field')

  try:
    replace = rule['replace']
  except KeyError:
    raise ValueError('Redaction rule is missing `replace` field')

  return RedactionRule(trigger, search, replace)

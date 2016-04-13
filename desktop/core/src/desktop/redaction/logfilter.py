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

import logging


class RedactionFilter(logging.Filter):
  """
  This is a filter that can be configured to automatically redact any
  information logged by Hue.
  """

  def __init__(self, engine):
    self._redaction_engine = engine

  def add_rule(self, *args, **kwargs):
    self._redaction_engine.add_rule(*args, **kwargs)

  def filter(self, record):
    """
    Apply the redaction rules to the record. This is done by calling
    `record.getMessage()` to get the evaluated message string and applying the
    redaction rules to it. If it turns out there is nothing to be redacted in
    this string, the record is returned unmodified. Otherwise, the record's
    `msg` is replaced with the redacted message, and it's `args` is set to
    `None`.
    """
    original_message = record.getMessage()
    message = self._redaction_engine.redact(original_message)

    if message != original_message:
      record.msg = message
      record.args = None

    return True


def add_log_redaction_filter_to_logger(engine, logger):
  """
  `add_redaction_filter` injects the redaction filter into all of the `logger`
  handlers. This must be called after all of the handlers have been added to
  `logger`, otherwise those handlers may expose unredacted strings.
  """

  if engine.policies:
    redaction_filter = RedactionFilter(engine)

    for handler in logger.handlers:
      handler.addFilter(redaction_filter)

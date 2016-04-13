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
from desktop.redaction import logfilter
from desktop.redaction.engine import RedactionEngine


global_redaction_engine = RedactionEngine()

def redact(string):
  """
  Redact a string using the global redaction engine.
  """

  return global_redaction_engine.redact(string)


def register_log_filtering(policy):
  """
  `add_redaction_filter` injects the redaction filter into all of the `logger`
  handlers. This must be called after all of the handlers have been added to
  `logger`, otherwise those handlers may expose unredacted strings.
  """

  if policy:
    global_redaction_engine.add_policy(policy)
    logfilter.add_log_redaction_filter_to_logger(global_redaction_engine, logging.root)

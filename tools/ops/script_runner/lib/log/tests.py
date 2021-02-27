#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import tempfile

from nose.tools import assert_true, assert_false, assert_equal, assert_not_equal

from desktop.log import get_audit_logger, AuditHandler
from desktop.conf import AUDIT_EVENT_LOG_DIR, AUDIT_LOG_MAX_FILE_SIZE


def test_one_audit():
  with tempfile.NamedTemporaryFile("w+t") as log_tmp:

    # KB
    reset = [
        AUDIT_EVENT_LOG_DIR.set_for_testing(log_tmp.name),
        AUDIT_LOG_MAX_FILE_SIZE.set_for_testing('25KB')
    ]

    audit_logger = get_audit_logger()
    audit_handler = audit_logger.handlers[0]

    assert_equal(25 * 1024 ** 1, audit_handler.maxBytes)
    assert_equal(len(audit_logger.handlers), 1, audit_logger.handlers)
    assert_true(isinstance(audit_handler, AuditHandler), audit_logger.handlers)

    audit_logger = get_audit_logger()
    assert_equal(len(audit_logger.handlers), 1, audit_logger.handlers) # Not adding handler twice

    # Cleanup
    audit_logger.removeHandler(audit_handler)

    for r in reset:
      r()

    # MB
    reset = [
        AUDIT_EVENT_LOG_DIR.set_for_testing(log_tmp.name),
        AUDIT_LOG_MAX_FILE_SIZE.set_for_testing('25MB')
    ]

    audit_logger = get_audit_logger()
    audit_handler = audit_logger.handlers[0]

    assert_equal(25 * 1024 ** 2, audit_handler.maxBytes)
    assert_equal(len(audit_logger.handlers), 1, audit_logger.handlers)
    assert_true(isinstance(audit_handler, AuditHandler), audit_logger.handlers)

    audit_logger = get_audit_logger()
    assert_equal(len(audit_logger.handlers), 1, audit_logger.handlers) # Not adding handler twice

    # Cleanup
    audit_logger.removeHandler(audit_handler)

    for r in reset:
      r()

    # GB
    reset = [
        AUDIT_EVENT_LOG_DIR.set_for_testing(log_tmp.name),
        AUDIT_LOG_MAX_FILE_SIZE.set_for_testing('25GB')
    ]

    audit_logger = get_audit_logger()
    audit_handler = audit_logger.handlers[0]

    assert_equal(25 * 1024 ** 3, audit_handler.maxBytes)
    assert_equal(len(audit_logger.handlers), 1, audit_logger.handlers)
    assert_true(isinstance(audit_handler, AuditHandler), audit_logger.handlers)

    audit_logger = get_audit_logger()
    assert_equal(len(audit_logger.handlers), 1, audit_logger.handlers) # Not adding handler twice

    # Cleanup
    audit_logger.removeHandler(audit_handler)

    for r in reset:
      r()

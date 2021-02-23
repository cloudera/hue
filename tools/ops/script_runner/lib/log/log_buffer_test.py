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
#
# A couple of test cases for the log buffer
#

import log_buffer
import logging
import unittest

class TestLogBuffer(unittest.TestCase):
  def test_logger(self):
    logger = logging.getLogger()
    handler = log_buffer.FixedBufferHandler()
    logger.addHandler(handler)
    msg = "My test logging message"
    logger.warn(msg)
    self.assertEquals(msg, str(handler.buf))

  def test_overflow(self):
    buffer = log_buffer.FixedBuffer(maxsize=10)
    buffer.insert("0123456789")
    buffer.insert("abcde")
    self.assertEquals("56789\nabcde", str(buffer))

if __name__ == '__main__':
  unittest.main()

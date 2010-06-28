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

import unittest
import logging
import StringIO
import random

import xxd

from subprocess import Popen, PIPE

logger = logging.getLogger(__name__)

LENGTH = 1024*10 # 10KB

class XxdTest(unittest.TestCase):
  def test_mask_not_alphanumeric(self):
    self.assertEquals( (1, ". X"), xxd.mask_not_alphanumeric("\n X"))

  def test_mask_not_printable(self):
    self.assertEquals( (2, "..@"), xxd.mask_not_alphanumeric("\xff\x90\x40"))


  def test_compare_to_xxd(self):
    """
    Runs xxd on some random text, and compares output with our xxd.

    It's conceivable that this isn't portable: xxd may have different
    default options.

    To be honest, this test was written after this was working.
    I tested using a temporary file and a side-by-side diff tool (vimdiff).
    """
    # /dev/random tends to hang on Linux, so we use python instead.
    # It's inefficient, but it's not terrible.
    random_text = "".join(chr(random.getrandbits(8)) for _ in range(LENGTH))
    p = Popen(["xxd"], shell=True, stdin=PIPE, stdout=PIPE, close_fds=True)
    (stdin, stderr) = p.communicate(random_text)
    self.assertFalse(stderr)

    output = StringIO.StringIO()
    xxd.main(StringIO.StringIO(random_text), output)
    self.assertEquals(stdin, output.getvalue())

if __name__ == "__main__":
  unittest.main()

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
import random
import StringIO
import subprocess

import xxd

from nose.plugins.skip import SkipTest

from subprocess import Popen, PIPE

LOG = logging.getLogger(__name__)

LENGTH = 1024*10 # 10KB

class XxdTest(unittest.TestCase):
  def test_mask_not_alphanumeric(self):
    self.assertEquals( (1, ". X"), xxd.mask_not_alphanumeric("\n X"))

  def test_mask_not_printable(self):
    self.assertEquals( (2, "..@"), xxd.mask_not_alphanumeric("\xff\x90\x40"))

  def _get_offset_width(self, line):
    offset, match, _ = line.partition(":")
    if not match:
      raise ValueError("No offset was found in the xxd output")
    return len(offset)

  def _is_offset_width_same(self, expected, actual):
    return self._get_offset_width(expected) == self._get_offset_width(actual)

  def _remove_padding(self, line):
    for index, c in enumerate(line):
      if c != '0':
        return line[index:]
    return ''

  def _standardize_xxd_output(self, xxd_output):
    return "\n".join(self._remove_padding(line) for line in xxd_output.splitlines())

  def _verify_content(self, expected, actual):
    if self._is_offset_width_same(expected, actual):
      self.assertEquals(expected, actual)
    else:
      # Not all distributions have the same amount of bits in their 'Offset'
      # This corrects for this to avoid having this test fail when that is the only problem
      corrected_expected = self._standardize_xxd_output(expected)
      corrected_actual = self._standardize_xxd_output(actual)
      self.assertEquals(corrected_expected, corrected_actual)

  def test_compare_to_xxd(self):
    """
    Runs xxd on some random text, and compares output with our xxd.

    It's conceivable that this isn't portable: xxd may have different
    default options.

    To be honest, this test was written after this was working.
    I tested using a temporary file and a side-by-side diff tool (vimdiff).
    """
    try:
      subprocess.check_output('type xxd', shell=True)
    except subprocess.CalledProcessError as e:
      LOG.warn('xxd not found')
      raise SkipTest
    # /dev/random tends to hang on Linux, so we use python instead.
    # It's inefficient, but it's not terrible.
    random_text = "".join(chr(random.getrandbits(8)) for _ in range(LENGTH))
    p = Popen(["xxd"], shell=True, stdin=PIPE, stdout=PIPE, close_fds=True)
    (stdin, stderr) = p.communicate(random_text)
    self.assertFalse(stderr)

    output = StringIO.StringIO()
    xxd.main(StringIO.StringIO(random_text), output)
    self._verify_content(stdin, output.getvalue())

if __name__ == "__main__":
  unittest.main()

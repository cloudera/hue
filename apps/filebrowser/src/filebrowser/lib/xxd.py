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
"""
Implements xxd-like functionality.
"""
from __future__ import division
from builtins import map
from builtins import range
from past.utils import old_div
import string
import sys

import re

def make_re(mask):
  """Makes a regex from an iterable of characters."""
  as_string = "".join(mask)
  r = '[^' + re.escape(as_string) + ']'
  return re.compile(r)

# All the printable characters, without tabs and newlines, but including spaces.
NON_FANCY_PRINTABLE = make_re(set(string.printable).difference(string.whitespace).union(" "))
PRINTABLE = make_re(string.printable)

def mask_not_printable(contents, mask_re=PRINTABLE):
  """
  Replaces non-printable characters with "."
  Returns (number_of_replacements, masked_string).
  """
  out, cnt = mask_re.subn('.', contents)
  return cnt, out

def mask_not_alphanumeric(data):
  """
  Same as above, except also masks out tab and newline.
  """
  return mask_not_printable(data, NON_FANCY_PRINTABLE)

def xxd(shift, data, bytes_per_line, bytes_per_sentence):
  """
  A generator of (offset, [[byte ordinal]], printable) strings,
  to support something similar to the xxd command.  Essentially,
  this splits up a string into chunks.

  In the output below, there are 8 sentences, each of 2 bytes.  The
  offset is 0, and the printable representation is on the right.

  0000000: 565b 373a 4fd1 ff78 4aa6 023d e4bb 2f92  V[7:O..xJ..=../.

  @param shift: Shifts the returned offsets by this amount.
  """
  current = 0
  for current in range(0, len(data), bytes_per_line):
    line = data[current:current+bytes_per_line]
    line_printable = mask_not_alphanumeric(line)[1]
    line_ordinals = list(map(ord, line))
    offsets = list(range(0, len(line_ordinals), bytes_per_sentence))
    line_ordinal_words = [ line_ordinals[x:x+bytes_per_sentence] for x in offsets ]

    yield (shift + current, line_ordinal_words, line_printable)

def main(input, output):
  """
  Prints out input just as xxd would do it.
  """
  offset = 0
  bytes_per_line = 16
  bytes_per_sentence = 2

  # Must be multiple of bytes_per_line
  input_chunk = bytes_per_line * 10

  while True:
    data = input.read(bytes_per_line)
    if data == '':
      return

    for off, ordinals, printable in xxd(offset, data, bytes_per_line, bytes_per_sentence):
      def ashex(ord):
        return "%02x" % ord
      hex = " ".join([ "".join(map(ashex, sentence)) for sentence in ordinals])
      # 2 characters per byte, 1 extra for spacing, and 1 extra at the end.
      hex = hex.ljust(bytes_per_line*2 + (old_div(bytes_per_line,bytes_per_sentence)) - 1)
      output.write("%07x: %s  %s\n" % (off, hex, printable))

    offset += len(data)

if __name__ == "__main__":
  main(sys.stdin, sys.stdout)

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
We would like to keep the last X characters
of log message around for us to view in case of emergency.

This log handler lets us do that.
"""

import logging, collections

class FixedBuffer(object):
  """
  The what: a buffer that maintains a fixed-size sliding window on
  the log history. As messages come in, old messages get pushed out.

  The plan: use a deque to keep a list of messages by reference (so
  minimal copying required). If the total size in characters exceeds
  some maximum, pop off messages until we get below the max, and then
  pad back up with the last maxsize-size characters of the most recently
  removed message to bring us back up to the maximum.

  Net cost is eventually one string copy per insert and a linear amount of
  reference manipulation. Benefit is the ability to save a slice through
  the really big messages (although huge messages are rare) rather than
  lose them completely when they get popped.
  """
  def __init__(self, maxsize=50000):
    """
    maxsize is in characters, not bytes.
    """
    self.buffer = collections.deque()
    self.maxsize = maxsize
    self.size = 0

  def insert(self, message):
    self.size += len(message)
    self.buffer.append(message)
    if self.size > self.maxsize:
      while self.size > self.maxsize:
        last = self.buffer.popleft()
        self.size -= len(last)
      # Prepend only as many characters of the outgoing string
      # as we can fit in the buffer
      self.buffer.appendleft(last[-(self.maxsize-self.size):])
      self.size = self.maxsize

  def __str__(self):
    return '\n'.join([m for m in self.buffer])

  def __iter__(self):
    return iter(self.buffer)

class FixedBufferHandler(logging.Handler):
  """
  Super simple log handler.
  """
  def __init__(self,buffer_size=50000):
    logging.Handler.__init__(self)
    self.buf = FixedBuffer(buffer_size)

  def emit(self,record):
    self.buf.insert(self.format(record))

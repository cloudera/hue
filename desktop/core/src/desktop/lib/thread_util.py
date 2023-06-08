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

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import logging
import socket
import sys
import threading
import traceback

if sys.version_info[0] > 2:
  from io import StringIO as string_io
else:
  from cStringIO import StringIO as string_io

LOG = logging.getLogger()


def dump_traceback(file=sys.stderr, all_threads=True):
  """Print a thread stacktrace"""

  current_thread = threading.current_thread()

  if all_threads:
    threads = threading.enumerate()
  else:
    threads = [current_thread]

  for thread in threads:
    if thread == current_thread:
      name = "Current thread"
    else:
      name = "Thread"

    trace_buffer = string_io()
    print("%s: %s %s %s (most recent call last):" % (socket.gethostname(), name, thread.name, thread.ident), file=trace_buffer)
    frame = sys._current_frames()[thread.ident]
    traceback.print_stack(frame, file=trace_buffer)

    print(trace_buffer.getvalue(), file=file)
    logging.debug(trace_buffer.getvalue())

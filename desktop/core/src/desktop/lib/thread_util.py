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

import sys
import threading
import traceback

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

    print >> file, "%s %s %s (most recent call last):" % (name, thread.name, thread.ident)
    frame = sys._current_frames()[thread.ident]
    traceback.print_stack(frame, file=file)
    print >> file

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

from future import standard_library
standard_library.install_aliases()
import sys
import threading
import time

from nose.tools import assert_true
from desktop.lib.thread_util import dump_traceback

if sys.version_info[0] > 2:
  from io import StringIO as string_io
else:
  from cStringIO import StringIO as string_io

def test_dump_traceback():
  started = threading.Event()
  stopped = threading.Event()

  class Thread(threading.Thread):
    def run(self):
      started.set()
      stopped.wait(10.0)
      assert_true(stopped.is_set())

  thread = Thread(name='thread_util_test thread')
  thread.start()
  thread_ident = str(thread.ident)

  header = 'Thread thread_util_test thread %s' % thread_ident

  try:
    started.wait(10.0)
    assert_true(started.is_set())

    out = string_io()
    dump_traceback(file=out)

    assert_true(header in out.getvalue())

    out = string_io()
    dump_traceback(file=out, all_threads=False)

    assert_true(header not in out.getvalue())
  finally:
    stopped.set()
    thread.join()

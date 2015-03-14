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

import spark.conf

def _start_livy_server():
  import atexit
  import subprocess
  import sys
  import time

  p = subprocess.Popen([sys.executable, sys.argv[0], 'livy_server'])

  def cleanup():
    p.terminate()
    for _ in xrange(5):
      if p.poll() == None:
        time.sleep(1)
      else:
        break
    else:
      p.kill()

  atexit.register(cleanup)

if spark.conf.START_LIVY_SERVER.get():
  _start_livy_server()

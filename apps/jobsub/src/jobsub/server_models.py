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
Models used by the jobsubd server.
"""
from django.db import models

# TODO(philip): Move into separate django app?
class ServerSubmissionState(models.Model):
  """
  Used by jobsubd (the daemon) to keep information
  about running processes.

  The webapp should not access this directly.
  """
  # Temporary directory where this job is running
  tmp_dir = models.CharField(max_length=128)
  # pid may be useful for debugging.
  pid = models.IntegerField(null=True)
  # This is an enum from jobsubd.thrift:State
  submission_state = models.IntegerField()
  start_time = models.DateTimeField(auto_now_add=True)
  end_time = models.DateTimeField(null=True)

#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os

from django.core.management.base import BaseCommand
from notebook.conf import DBPROXY_EXTRA_CLASSPATH


LOG = logging.getLogger(__name__)


class Command(BaseCommand):
  """
  Starts DBProxy server for providing a JDBC gateway.
  """

  help = 'start DBProxy server for providing a JDBC gateway'

  def handle(self, *args, **kwargs):
    env = os.environ.copy()

    cmd = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "librdbms", "java", "bin", "dbproxy")

    if DBPROXY_EXTRA_CLASSPATH.get():
      env['CLASSPATH'] = '%s:%s' % (DBPROXY_EXTRA_CLASSPATH.get(), env.get('CLASSPATH', ''))

    LOG.info("Executing %r (%r) (%r)" % (cmd, args, env))

    # Use exec, so that this takes only one process.
    os.execvpe(cmd, args, env)

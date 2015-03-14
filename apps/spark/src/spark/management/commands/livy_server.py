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
import subprocess

from django.core.management.base import NoArgsCommand
import spark.conf


LOG = logging.getLogger(__name__)


class Command(NoArgsCommand):
  """
  Starts livy server.
  """

  help = 'start livy server'

  def handle(self, *args, **kwargs):
    env = os.environ.copy()
    classpath = env.get('CLASSPATH', '').split(os.pathsep)

    jar = spark.conf.LIVY_ASSEMBLY_JAR.get()
    classpath.insert(0, jar)

    # Add the hadoop classpath if it's available.
    try:
      p = subprocess.Popen(['hadoop', 'classpath'], stdout=subprocess.PIPE)
    except OSError:
      pass
    else:
      hadoop_classpath = p.communicate()[0]
      if p.wait() == 0:
        classpath.append(hadoop_classpath)

    args = [
      "java",
    ]

    args.extend(("-cp", os.pathsep.join(classpath)))

    server_host = spark.conf.LIVY_SERVER_HOST.get()
    args.append("-Dlivy.server.host=" + server_host)

    server_port = spark.conf.LIVY_SERVER_PORT.get()
    args.append("-Dlivy.server.port=" + server_port)

    session_factory = spark.conf.LIVY_SERVER_SESSION_KIND.get()
    args.append("-Dlivy.server.session.factory=" + session_factory)

    livy_yarn_jar = spark.conf.LIVY_YARN_JAR.get()
    if livy_yarn_jar:
      args.append("-Dlivy.yarn.jar=" + livy_yarn_jar)

    args.append("com.cloudera.hue.livy.server.Main")

    LOG.info("Executing %r (%r) (%r)" % (args[0], args, env))

    # Use exec, so that this takes only one process.
    os.execvpe(args[0], args, env)

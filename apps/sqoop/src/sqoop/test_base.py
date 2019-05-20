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

import atexit
import logging
import os
import socket
import subprocess
import threading
import time

from django.conf import settings
from nose.plugins.skip import SkipTest

from desktop.lib.paths import get_run_root
from desktop.lib.rest.http_client import RestException
from hadoop import pseudo_hdfs4
from hadoop.pseudo_hdfs4 import is_live_cluster

from sqoop.client import SqoopClient
from sqoop.conf import SERVER_URL


service_lock = threading.Lock()

LOG = logging.getLogger(__name__)


class SqoopServerProvider(object):
  """
  Setup a Sqoop server.
  """
  TEST_PORT = '19080'
  TEST_SHUTDOWN_PORT = '19081'
  HOME = get_run_root('ext/sqoop/sqoop')

  requires_hadoop = True
  integration = True

  is_running = False

  @classmethod
  def setup_class(cls):

    if not is_live_cluster():
      raise SkipTest()

    cls.cluster = pseudo_hdfs4.shared_cluster()
    cls.client, callback = cls.get_shared_server()
    cls.shutdown = [callback]

  @classmethod
  def initialize(cls, tmpdir):
    hadoop_conf_dir = os.path.join(tmpdir, 'conf')
    base_dir = os.path.join(tmpdir, 'sqoop')
    log_dir = os.path.join(base_dir, 'logs')
    conf_dir = os.path.join(base_dir, 'conf')
    old_conf_dir = os.path.join(SqoopServerProvider.HOME, 'server/conf')

    if not os.path.exists(hadoop_conf_dir):
      os.mkdir(hadoop_conf_dir)
    if not os.path.exists(base_dir):
      os.mkdir(base_dir)
    if not os.path.exists(log_dir):
      os.mkdir(log_dir)
    if not os.path.exists(conf_dir):
      os.mkdir(conf_dir)

    for _file in ('sqoop.properties', 'sqoop_bootstrap.properties'):
      with open(os.path.join(old_conf_dir, _file), 'r') as _original:
        with open(os.path.join(conf_dir, _file), 'w') as _new:
          for _line in _original:
            line = _line.replace('${test.log.dir}', log_dir)
            line = line.replace('${test.hadoop.conf.dir}', hadoop_conf_dir)
            line = line.replace('${test.base.dir}', base_dir)
            _new.write(line)
    # This sets JAVA_OPTS with a sqoop conf... we need to use our own.
    os.chmod(os.path.join(SqoopServerProvider.HOME, 'server/bin/setenv.sh'), 0)

  @classmethod
  def start(cls, cluster):
    """
    Start oozie process.
    """
    SqoopServerProvider.initialize(cluster._tmpdir)

    env = os.environ
    env['CATALINA_HOME'] = os.path.join(SqoopServerProvider.HOME, 'server')
    env['CATALINA_PID'] = os.path.join(cluster._tmpdir, 'sqoop/sqoop.pid')
    env['CATALINA_OPTS'] = """
      -Dtest.log.dir=%(log_dir)s
      -Dtest.host.local=%(host)s
      -Dsqoop.http.port=%(http_port)s
      -Dsqoop.admin.port=%(admin_port)s
    """ % {
      'log_dir': os.path.join(cluster._tmpdir, 'sqoop/logs'),
      'host': socket.getfqdn(),
      'http_port': SqoopServerProvider.TEST_PORT,
      'admin_port': SqoopServerProvider.TEST_SHUTDOWN_PORT
    }
    env['SQOOP_HTTP_PORT'] = SqoopServerProvider.TEST_PORT
    env['SQOOP_ADMIN_PORT'] = SqoopServerProvider.TEST_SHUTDOWN_PORT
    env['JAVA_OPTS'] = '-Dsqoop.config.dir=%s' % os.path.join(cluster._tmpdir, 'sqoop/conf')
    args = [os.path.join(SqoopServerProvider.HOME, 'bin/sqoop.sh'), 'server', 'start']

    LOG.info("Executing %s, env %s, cwd %s" % (repr(args), repr(env), cluster._tmpdir))
    process = subprocess.Popen(args=args, env=env, cwd=cluster._tmpdir, stdin=subprocess.PIPE)
    return process

  @classmethod
  def get_shared_server(cls, username='sqoop', language=settings.LANGUAGE_CODE):
    callback = lambda: None

    with service_lock:
      if not SqoopServerProvider.is_running:
        # Setup
        cluster = pseudo_hdfs4.shared_cluster()

        if is_live_cluster():
          finish = ()
        else:
          LOG.info('\nStarting a Mini Sqoop. Requires "tools/jenkins/jenkins.sh" to be previously ran.\n')

          finish = (
            SERVER_URL.set_for_testing("http://%s:%s/sqoop" % (socket.getfqdn(), SqoopServerProvider.TEST_PORT)),
          )

          p = cls.start(cluster)

          def kill():
            with open(os.path.join(cluster._tmpdir, 'sqoop/sqoop.pid'), 'r') as pidfile:
              pid = pidfile.read()
              LOG.info("Killing Sqoop server (pid %s)." % pid)
              os.kill(int(pid), 9)
              p.wait()
          atexit.register(kill)

        start = time.time()
        started = False
        sleep = 0.01

        client = SqoopClient(SERVER_URL.get(), username, language)

        while not started and time.time() - start < 60.0:
          LOG.info('Check Sqoop status...')
          try:
            version = client.get_version()
          except RestException, e:
            LOG.exception('Exception fetching the Sqoop server version')

            # Don't loop if we had an authentication error.
            if e.code == 401:
              raise
          except Exception, e:
            LOG.info('Sqoop server not started yet: %s' % e)
          else:
            if version:
              started = True
              break

          time.sleep(sleep)
          sleep *= 2

        if not started:
          raise Exception("Sqoop server took too long to come up.")

        def shutdown():
          for f in finish:
            f()
          cluster.stop()
        callback = shutdown

        SqoopServerProvider.is_running = True
      else:
        client = SqoopClient(SERVER_URL.get(), username, language)

      return client, callback

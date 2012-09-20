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
Starts the beeswax server.
"""

from django.core.management.base import NoArgsCommand
import beeswax.conf
import beeswax.hive_site
import desktop.conf
import hadoop.cluster

import logging
import os
import sys

LOG = logging.getLogger(__name__)

class Command(NoArgsCommand):
  """ Starts beeswax daemon.  """

  def handle_noargs(self, **options):
    cluster_conf = hadoop.cluster.get_cluster_conf_for_job_submission()
    if cluster_conf is None:
      LOG.error("Configuration does not contain any MR/Yarn clusters with "
                "`submit_to' enabled. Cannot start BeeswaxServer.")
      sys.exit(1)

    env = os.environ.copy()
    def set_if_present(name, val):
      if val:
        env[name] = val

    env['HADOOP_BIN'] = cluster_conf.HADOOP_BIN.get()
    set_if_present('HADOOP_MAPRED_HOME', cluster_conf.HADOOP_MAPRED_HOME.get())
    set_if_present('HADOOP_CONF_DIR', cluster_conf.HADOOP_CONF_DIR.get())
    set_if_present('HADOOP_HEAPSIZE', beeswax.conf.BEESWAX_SERVER_HEAPSIZE.get())
    set_if_present('HIVE_HOME', beeswax.conf.BEESWAX_HIVE_HOME_DIR.get())
    set_if_present('HIVE_CONF_DIR', beeswax.conf.BEESWAX_HIVE_CONF_DIR.get())

    bin = beeswax.conf.BEESWAX_SERVER_BIN.get()

    # Host that desktop is running on
    # - If the ip is configured to be 0, assume localhost
    dt_host = desktop.conf.HTTP_HOST.get()
    if dt_host == '0.0.0.0':
      dt_host = '127.0.0.1'

    if 'beeswax_server_port' in beeswax.conf.QUERY_SERVERS['bind_to']:
      server_port = beeswax.conf.QUERY_SERVERS['default'].SERVER_PORT.get()
    else:
      server_port = beeswax.conf.BEESWAX_SERVER_PORT.get()

    args = [
      os.path.basename(bin),
      '--beeswax',
      str(server_port),
      '--desktop-host',
      str(dt_host),
      '--desktop-port',
      str(desktop.conf.HTTP_PORT.get()),
      '--query-lifetime',
      str(beeswax.conf.BEESWAX_RUNNING_QUERY_LIFETIME.get()),
    ]

    # Pass in keytab if security is turned on. Beeswax periodically renews
    # the ticket.
    if cluster_conf.SECURITY_ENABLED.get():
      args += [
        '--keytab',
        desktop.conf.KERBEROS.HUE_KEYTAB.get(),
        '--principalConf',
        desktop.conf.KERBEROS.HUE_PRINCIPAL.get(),
      ]

    # Running on HTTPS?
    if desktop.conf.is_https_enabled():
      args.append('--desktop-https')
      args.append('true')

    # Start metastore as well?
    is_local, host, port = beeswax.hive_site.get_metastore()
    if not is_local:
      LOG.info("Beeswax configured to use external metastore at %s:%s" % (host, port))
    else:
      args += [ '--metastore', str(beeswax.conf.BEESWAX_META_SERVER_PORT.get()) ]

    LOG.info("Executing %r (%r) (%r)" % (bin, args, env))
    # Use exec, so that this takes only one process.
    os.execve(bin, args, env)

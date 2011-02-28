#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
#

"""
Common infrastructure for beeswax tests
"""

import atexit
import logging
import pwd
import os
import re
import subprocess
import time

import fb303.ttypes
from nose.tools import assert_true, assert_false

from desktop.lib.django_test_util import make_logged_in_client

from hadoop import mini_cluster
import hadoop.conf

import beeswax.conf


_INITIALIZED = False
_SHARED_BEESWAX_SERVER_PROCESS = None


BEESWAXD_TEST_PORT = 6969
LOG = logging.getLogger(__name__)

def _start_server(cluster):
  """
  Start beeswaxd and metastore
  """
  script = beeswax.conf.BEESWAX_SERVER_BIN.get()
  args = [
    script,
    '--beeswax',
    str(BEESWAXD_TEST_PORT),
    '--metastore',
    str(BEESWAXD_TEST_PORT + 1),
    '--superuser',
    pwd.getpwuid(os.getuid())[0],
    '--desktop-host',
    str('127.0.0.1'),
    '--desktop-port',
    str('42'),           # Make up a port here. Tests don't start an actual server.
  ]
  env = {
    'HADOOP_HOME': hadoop.conf.HADOOP_HOME.get(),
    'HADOOP_CONF_DIR': cluster.config_dir,
    'HIVE_CONF_DIR': beeswax.conf.BEESWAX_HIVE_CONF_DIR.get(),
    'HIVE_HOME' : beeswax.conf.BEESWAX_HIVE_HOME_DIR.get(),
    'HADOOP_EXTRA_CLASSPATH_STRING': hadoop.conf.HADOOP_EXTRA_CLASSPATH_STRING.get()
  }
  if os.getenv("JAVA_HOME"):
    env["JAVA_HOME"] = os.getenv("JAVA_HOME")

  LOG.info("Executing %s, env %s, cwd %s" % (repr(args), repr(env), cluster.tmpdir))
  process = subprocess.Popen(args=args, env=env, cwd=cluster.tmpdir, stdin=subprocess.PIPE)
  return process



def get_shared_beeswax_server():
  # Copy hive-default.xml from BEESWAX_HIVE_CONF_DIR before it is set to
  # /my/bogus/path
  default_xml = file(beeswax.conf.BEESWAX_HIVE_CONF_DIR.get()+"/hive-default.xml").read()

  finish = (
    beeswax.conf.BEESWAX_SERVER_HOST.set_for_testing("localhost"),
    beeswax.conf.BEESWAX_SERVER_PORT.set_for_testing(BEESWAXD_TEST_PORT),
    beeswax.conf.BEESWAX_META_SERVER_HOST.set_for_testing("localhost"),
    beeswax.conf.BEESWAX_META_SERVER_PORT.set_for_testing(BEESWAXD_TEST_PORT + 1),
    # Use a bogus path to avoid loading the normal hive-site.xml
    beeswax.conf.BEESWAX_HIVE_CONF_DIR.set_for_testing('/my/bogus/path')
  )

  cluster = mini_cluster.shared_cluster(conf=True)

  # Copy hive-default.xml into the mini_cluster's conf dir, which happens to be
  # in the cluster's tmpdir. This tmpdir is determined during the mini_cluster
  # startup, during which BEESWAX_HIVE_CONF_DIR needs to be set to
  # /my/bogus/path. Hence the step of writing to memory.
  # hive-default.xml will get picked up by the beeswax_server during startup
  file(cluster.tmpdir+"/conf/hive-default.xml", 'w').write(default_xml)

  global _SHARED_BEESWAX_SERVER_PROCESS
  if _SHARED_BEESWAX_SERVER_PROCESS is None:
    p = _start_server(cluster)
    _SHARED_BEESWAX_SERVER_PROCESS = p
    def kill():
      LOG.info("Killing beeswax server (pid %d)." % p.pid)
      os.kill(p.pid, 9)
      p.wait()
    atexit.register(kill)
    # Wait for server to come up, by repeatedly trying.
    start = time.time()
    started = False
    sleep = 0.001
    while not started and time.time() - start < 20.0:
      try:
        client = beeswax.db_utils.db_client()
        meta_client = beeswax.db_utils.meta_client()

        client.echo("echo")
        if meta_client.getStatus() == fb303.ttypes.fb_status.ALIVE:
          started = True
          break
        time.sleep(sleep)
        sleep *= 2
      except:
        time.sleep(sleep)
        sleep *= 2
        pass
    if not started:
      raise Exception("Beeswax server took too long to come up.")

    # Make sure /tmp is 0777
    cluster.fs.setuser(cluster.superuser)
    if not cluster.fs.isdir('/tmp'):
      cluster.fs.mkdir('/tmp', 0777)
    else:
      cluster.fs.chmod('/tmp', 0777)

  def s():
    for f in finish:
      f()
    cluster.shutdown()

  return cluster, s


REFRESH_RE = re.compile('<\s*meta\s+http-equiv="refresh"\s+content="\d*;([^"]*)"\s*/>', re.I)

def wait_for_query_to_finish(client, response, max=30.0):
  logging.info(str(response.template) + ": " + str(response.content))
  start = time.time()
  sleep_time = 0.05
  # We don't check response.template == "watch_wait.mako" here,
  # because Django's response.template stuff is not thread-safe.
  while "Waiting for query..." in response.content:
    time.sleep(sleep_time)
    sleep_time = min(1.0, sleep_time * 2) # Capped exponential
    if (time.time() - start) > max:
      message = "Query took too long! %d seconds" % (time.time() - start,)
      LOG.warning(message)
      raise Exception(message)

    # Find out url to retry
    match = REFRESH_RE.search(response.content)
    if match is not None:
      url = match.group(1)
      url = url.lstrip('url=')
    else:
      url = response.request['PATH_INFO']
    response = client.get(url, follow=True)
  return response


def make_query(client, query, submission_type="Execute",
               udfs=None, settings=None, resources=None,
               wait=False, name=None, desc=None, local=True,
               is_parameterized=True, max=30.0, **kwargs):
  """
  Prepares arguments for the execute view.

  If wait is True, waits for query to finish as well.
  """

  if settings is None:
    settings = []
  if local:
    # Tests run faster if not run against the real cluster.
    settings.append( ("mapred.job.tracker", "local") )

  # Prepares arguments for the execute view.
  parameters = {
    'query-query': query,
    'query-is_parameterized': is_parameterized and "on"
  }
  if submission_type == 'Execute':
    parameters['button-submit'] = 'Whatever'
  elif submission_type == 'Explain':
    parameters['button-explain'] = 'Whatever'
  elif submission_type == 'Save':
    parameters['saveform-save'] = 'True'

  if name:
    parameters['saveform-name'] = name
  if desc:
    parameters['saveform-desc'] = desc

  parameters["functions-next_form_id"] = str(len(udfs or []))
  for i, udf_pair in enumerate(udfs or []):
    name, klass = udf_pair
    parameters["functions-%d-name" % i] = name
    parameters["functions-%d-class_name" % i] = klass
    parameters["functions-%d-_exists" % i] = 'True'
  parameters["settings-next_form_id"] = str(len(settings))
  for i, settings_pair in enumerate(settings or []):
    key, value = settings_pair
    parameters["settings-%d-key" % i] = key
    parameters["settings-%d-value" % i] = value
    parameters["settings-%d-_exists" % i] = 'True'
  parameters["file_resources-next_form_id"] = str(len(resources or []))
  for i, resources_pair in enumerate(resources or []):
    type, path = resources_pair
    parameters["file_resources-%d-type" % i] = type
    parameters["file_resources-%d-path" % i] = path
    parameters["file_resources-%d-_exists" % i] = 'True'

  kwargs.setdefault('follow', True)
  response = client.post("/beeswax/execute", parameters, **kwargs)

  if wait:
    return wait_for_query_to_finish(client, response, max)
  return response


def verify_history(client, fragment, design=None, reverse=False):
  """
  Verify that the query fragment and/or design are in the query history.
  If reverse is True, verify the opposite.
  Return the size of the history; -1 if we fail to determine it.
  """
  resp = client.get('/beeswax/query_history')
  my_assert = reverse and assert_false or assert_true
  my_assert(fragment in resp.content)
  if design:
    my_assert(design in resp.content)

  if resp.context:
    try:
      return len(resp.context['page'].object_list)
    except KeyError:
      pass

  # This could happen if we issue multiple requests in parallel.
  # The capturing of Django response context is not thread safe.
  # Also see:
  #   http://docs.djangoproject.com/en/1.2/topics/testing/#testing-responses
  LOG.warn('Cannot find history size. Response context clobbered')
  return -1


class BeeswaxSampleProvider(object):
  """
  Setup the test db and install sample data
  """
  @classmethod
  def setup_class(cls):
    cls.cluster, shutdown = get_shared_beeswax_server()
    cls.client = make_logged_in_client()
    # Weird redirection to avoid binding nonsense.
    cls.shutdown = [ shutdown ]
    cls.init_beeswax_db()

  @classmethod
  def teardown_class(cls):
    cls.cluster.fs.setuser(cls.cluster.superuser)
    try:
      cls.cluster.fs.rmtree('/tmp/beeswax')
    except IOError, ex:
      LOG.warn('Failed to cleanup /tmp/beeswax: %s' % (ex,))
    cls.shutdown[0]()

  @classmethod
  def init_beeswax_db(cls):
    """
    Install the common test tables (only once)
    """
    global _INITIALIZED
    if _INITIALIZED:
      return

    data_file = u'/tmp/beeswax/sample_data_échantillon_%d.tsv'

    # Create a "test_partitions" table.
    CREATE_PARTITIONED_TABLE = """
      CREATE TABLE test_partitions (foo INT, bar STRING)
      PARTITIONED BY (baz STRING, boom STRING)
      ROW FORMAT DELIMITED
        FIELDS TERMINATED BY '\t'
        LINES TERMINATED BY '\n'
    """
    make_query(cls.client, CREATE_PARTITIONED_TABLE, wait=True)
    cls._make_data_file(data_file % 1)

    LOAD_DATA = """
      LOAD DATA INPATH '%s'
      OVERWRITE INTO TABLE test_partitions
      PARTITION (baz='baz_one', boom='boom_two')
    """ % (data_file % 1,)
    make_query(cls.client, LOAD_DATA, wait=True, local=False)

    # Create a bunch of other tables
    CREATE_TABLE = """
      CREATE TABLE `%(name)s` (foo INT, bar STRING)
      COMMENT "%(comment)s"
      ROW FORMAT DELIMITED
        FIELDS TERMINATED BY '\t'
        LINES TERMINATED BY '\n'
    """

    # Create a "test" table.
    table_info = dict(name='test', comment='Test table')
    cls._make_data_file(data_file % 2)
    cls._make_table(table_info['name'], CREATE_TABLE % table_info, data_file % 2)

    # Create a "test_utf8" table.
    table_info = dict(name='test_utf8', comment=cls.get_i18n_table_comment())
    cls._make_i18n_data_file(data_file % 3, 'utf-8')
    cls._make_table(table_info['name'], CREATE_TABLE % table_info, data_file % 3)

    # Create a "test_latin1" table.
    table_info = dict(name='test_latin1', comment=cls.get_i18n_table_comment())
    cls._make_i18n_data_file(data_file % 4, 'latin1')
    cls._make_table(table_info['name'], CREATE_TABLE % table_info, data_file % 4)

    _INITIALIZED = True

  @staticmethod
  def get_i18n_table_comment():
    return u'en-hello pt-Olá ch-你好 ko-안녕 ru-Здравствуйте'

  @classmethod
  def _make_table(cls, table_name, create_ddl, filename):
    make_query(cls.client, create_ddl, wait=True)
    LOAD_DATA = """
      LOAD DATA INPATH '%s' OVERWRITE INTO TABLE %s
    """ % (filename, table_name)
    make_query(cls.client, LOAD_DATA, wait=True, local=False)

  @classmethod
  def _make_data_file(cls, filename):
    """
    Create data to be loaded into tables.
    Data contains two columns of:
      <num>     0x<hex_num>
    where <num> goes from 0 to 255 inclusive.
    """
    cls.cluster.fs.setuser(cls.cluster.superuser)
    f = cls.cluster.fs.open(filename, "w")
    for x in xrange(256):
      f.write("%d\t0x%x\n" % (x, x))
    f.close()

  @classmethod
  def _make_i18n_data_file(cls, filename, encoding):
    """
    Create i18n data to be loaded into tables.
    Data contains two columns of:
      <num>     <unichr(num)>
    where <num> goes from 0 to 255 inclusive.
    """
    cls.cluster.fs.setuser(cls.cluster.superuser)
    f = cls.cluster.fs.open(filename, "w")
    for x in xrange(256):
      f.write("%d\t%s\n" % (x, unichr(x).encode(encoding)))
    f.close()

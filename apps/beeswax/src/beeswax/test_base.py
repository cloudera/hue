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

import atexit
import json
import logging
import os
import subprocess
import threading
import time

from nose.tools import assert_true, assert_false
from django.urls import reverse
from django.contrib.auth.models import User

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.paths import get_run_root
from desktop.lib.python_util import find_unused_port
from desktop.lib.exceptions import StructuredThriftTransportException
from desktop.lib.security_util import get_localhost_name
from desktop.lib.test_utils import add_to_group, grant_access
from hadoop import cluster, pseudo_hdfs4
from hadoop.pseudo_hdfs4 import is_live_cluster, get_db_prefix

import beeswax.conf

from beeswax.server.dbms import get_query_server_config
from beeswax.server import dbms


HIVE_SERVER_TEST_PORT = find_unused_port()
_INITIALIZED = False
_SHARED_HIVE_SERVER_PROCESS = None
_SHARED_HIVE_SERVER = None
_SHARED_HIVE_SERVER_LOCK = threading.Lock()
_SHARED_HIVE_SERVER_CLOSER = None
_SUPPORTED_EXECUTION_ENGINES = ['mr', 'spark', 'tez']


LOG = logging.getLogger(__name__)


def is_hive_on_spark():
  return os.environ.get('ENABLE_HIVE_ON_SPARK', 'false').lower() == 'true'


def get_available_execution_engines():
  available_engines = os.environ.get('AVAILABLE_EXECUTION_ENGINES_FOR_TEST', 'mr').lower().split(",")
  if any(engine not in _SUPPORTED_EXECUTION_ENGINES for engine in available_engines):
    raise ValueError("Unknown available execution engines: " + available_engines +
                     ". Supported engines are: " + _SUPPORTED_EXECUTION_ENGINES)
  return available_engines


def _start_server(cluster):
  args = [beeswax.conf.HIVE_SERVER_BIN.get()]

  env = cluster._mr2_env.copy()

  hadoop_cp_proc = subprocess.Popen(args=[get_run_root('ext/hadoop/hadoop') + '/bin/hadoop', 'classpath'], env=env, cwd=cluster._tmpdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  hadoop_cp_proc.wait()
  hadoop_cp = hadoop_cp_proc.stdout.read().strip()

  env.update({
    'HADOOP_HOME': get_run_root('ext/hadoop/hadoop'), # Used only by Hive for some reason
    'HIVE_CONF_DIR': beeswax.conf.HIVE_CONF_DIR.get(),
    'HIVE_SERVER2_THRIFT_PORT': str(HIVE_SERVER_TEST_PORT),
    'HADOOP_MAPRED_HOME': get_run_root('ext/hadoop/hadoop') + '/share/hadoop/mapreduce',
    # Links created in jenkins script.
    # If missing classes when booting HS2, check here.
    'AUX_CLASSPATH':
       get_run_root('ext/hadoop/hadoop') + '/share/hadoop/hdfs/hadoop-hdfs.jar'
       + ':' +
       get_run_root('ext/hadoop/hadoop') + '/share/hadoop/common/lib/hadoop-auth.jar'
       + ':' +
       get_run_root('ext/hadoop/hadoop') + '/share/hadoop/common/hadoop-common.jar'
       + ':' +
       get_run_root('ext/hadoop/hadoop') + '/share/hadoop/mapreduce/hadoop-mapreduce-client-core.jar'
       ,
      'HADOOP_CLASSPATH': hadoop_cp,
  })

  if os.getenv("JAVA_HOME"):
    env["JAVA_HOME"] = os.getenv("JAVA_HOME")

  LOG.info("Executing %s, env %s, cwd %s" % (repr(args), repr(env), cluster._tmpdir))
  return subprocess.Popen(args=args, env=env, cwd=cluster._tmpdir, stdin=subprocess.PIPE)


def get_shared_beeswax_server(db_name='default'):
  global _SHARED_HIVE_SERVER
  global _SHARED_HIVE_SERVER_CLOSER

  with _SHARED_HIVE_SERVER_LOCK:
    if _SHARED_HIVE_SERVER is None:
      cluster = pseudo_hdfs4.shared_cluster()

      if is_live_cluster():
        def s():
          pass
      else:
        s = _start_mini_hs2(cluster)

      start = time.time()
      started = False
      sleep = 1

      make_logged_in_client()
      user = User.objects.get(username='test')
      query_server = get_query_server_config()
      db = dbms.get(user, query_server)

      while not started and time.time() - start <= 60:
        try:
          db.open_session(user)
        except StructuredThriftTransportException, e:
          LOG.exception('Failed to open Hive Server session')

          # Don't loop if we had an authentication error.
          if 'Bad status: 3' in e.message:
            raise
        except Exception, e:
          LOG.exception('Failed to open Hive Server session')
        else:
          started = True
          break

        time.sleep(sleep)
        sleep *= 2

      if not started:
        raise Exception("Server took too long to come up.")

      _SHARED_HIVE_SERVER, _SHARED_HIVE_SERVER_CLOSER = cluster, s

    return _SHARED_HIVE_SERVER, _SHARED_HIVE_SERVER_CLOSER


def _start_mini_hs2(cluster):
  HIVE_CONF = cluster.hadoop_conf_dir
  finish = (
     beeswax.conf.HIVE_SERVER_HOST.set_for_testing(get_localhost_name()),
     beeswax.conf.HIVE_SERVER_PORT.set_for_testing(HIVE_SERVER_TEST_PORT),
     beeswax.conf.HIVE_SERVER_BIN.set_for_testing(get_run_root('ext/hive/hive') + '/bin/hiveserver2'),
     beeswax.conf.HIVE_CONF_DIR.set_for_testing(HIVE_CONF)
   )

  default_xml = """<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>

<configuration>

<property>
 <name>javax.jdo.option.ConnectionURL</name>
 <value>jdbc:derby:;databaseName=%(root)s/metastore_db;create=true</value>
 <description>JDBC connect string for a JDBC metastore</description>
</property>

<property>
  <name>hive.server2.enable.impersonation</name>
  <value>false</value>
</property>

<property>
 <name>hive.querylog.location</name>
 <value>%(querylog)s</value>
</property>

</configuration>
""" % {'root': cluster._tmpdir, 'querylog': cluster.log_dir + '/hive'}

  file(HIVE_CONF + '/hive-site.xml', 'w').write(default_xml)

  global _SHARED_HIVE_SERVER_PROCESS

  if _SHARED_HIVE_SERVER_PROCESS is None:
    p = _start_server(cluster)
    LOG.info("started")
    cluster.fs.do_as_superuser(cluster.fs.chmod, '/tmp', 01777)

    _SHARED_HIVE_SERVER_PROCESS = p
    def kill():
      LOG.info("Killing server (pid %d)." % p.pid)
      os.kill(p.pid, 9)
      p.wait()
    atexit.register(kill)

  def s():
    for f in finish:
      f()
    cluster.stop()

  return s


def wait_for_query_to_finish(client, response, max=60.0):
  # Take a async API execute_query() response in input

  start = time.time()
  sleep_time = 0.05

  if is_finished(response): # aka Has error at submission
    return response

  content = json.loads(response.content)

  watch_url = content['watch_url']

  response = client.get(watch_url, follow=True)

  # Loop and check status
  while not is_finished(response):
    time.sleep(sleep_time)
    sleep_time = min(1.0, sleep_time * 2) # Capped exponential
    if (time.time() - start) > max:
      message = "Query took too long! %d seconds" % (time.time() - start)
      LOG.warning(message)
      raise Exception(message)

    response = client.get(watch_url, follow=True)

  return response


def is_finished(response):
  status = json.loads(response.content)
  return 'error' in status \
      or status.get('isSuccess') \
      or status.get('isFailure') \
      or status.get('status') == -1


def fetch_query_result_data(client, status_response, n=0, server_name='beeswax'):
  # Take a wait_for_query_to_finish() response in input
  status = json.loads(status_response.content)

  response = client.get("/%(server_name)s/results/%(id)s/%(n)s?format=json" % {'server_name': server_name, 'id': status.get('id'), 'n': n})
  content = json.loads(response.content)

  return content

def make_query(client, query, submission_type="Execute",
               udfs=None, settings=None, resources=None,
               wait=False, name=None, desc=None, local=True,
               is_parameterized=True, max=60.0, database='default', email_notify=False, params=None, server_name='beeswax', **kwargs):
  """
  Prepares arguments for the execute view.

  If wait is True, waits for query to finish as well.
  """

  if settings is None:
    settings = []
  if params is None:
    params = []
  if local:
    # Tests run faster if not run against the real cluster.
    settings.append(('mapreduce.framework.name', 'local'))

  # Prepares arguments for the execute view.
  parameters = {
    'query-query': query,
    'query-name': name if name else '',
    'query-desc': desc if desc else '',
    'query-is_parameterized': is_parameterized and "on",
    'query-database': database,
    'query-email_notify': email_notify and "on",
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
    parameters["settings-%d-key" % i] = str(key)
    parameters["settings-%d-value" % i] = str(value)
    parameters["settings-%d-_exists" % i] = 'True'
  parameters["file_resources-next_form_id"] = str(len(resources or []))
  for i, resources_pair in enumerate(resources or []):
    type, path = resources_pair
    parameters["file_resources-%d-type" % i] = str(type)
    parameters["file_resources-%d-path" % i] = str(path)
    parameters["file_resources-%d-_exists" % i] = 'True'
  for name, value in params:
    parameters["parameterization-%s" % name] = value

  kwargs.setdefault('follow', True)
  execute_url = reverse("%(server_name)s:api_execute" % {'server_name': server_name})

  if submission_type == 'Explain':
    execute_url += "?explain=true"
  if submission_type == 'Save':
    execute_url = reverse("%(server_name)s:api_save_design" % {'server_name': server_name})

  response = client.post(execute_url, parameters, **kwargs)

  if wait:
    return wait_for_query_to_finish(client, response, max)

  return response


def verify_history(client, fragment, design=None, reverse=False, server_name='beeswax'):
  """
  Verify that the query fragment and/or design are in the query history.
  If reverse is True, verify the opposite.
  Return the size of the history; -1 if we fail to determine it.
  """
  resp = client.get('/%(server_name)s/query_history' % {'server_name': server_name})
  my_assert = reverse and assert_false or assert_true
  my_assert(fragment in resp.content, resp.content)
  if design:
    my_assert(design in resp.content, resp.content)

  if resp.context:
    try:
      return len(resp.context['page'].object_list)
    except KeyError:
      pass

  LOG.warn('Cannot find history size. Response context clobbered')
  return -1


class BeeswaxSampleProvider(object):
  integration = True

  """
  Setup the test db and install sample data
  """
  @classmethod
  def setup_class(cls, load_data=True):
    cls.load_data = load_data

    cls.db_name = get_db_prefix(name='hive')
    cls.cluster, shutdown = get_shared_beeswax_server(cls.db_name)
    cls.set_execution_engine()

    cls.client = make_logged_in_client(username='test', is_superuser=False)
    add_to_group('test', 'test')
    grant_access('test', 'test', 'beeswax')
    grant_access('test', 'test', 'metastore')

    # Weird redirection to avoid binding nonsense.
    cls.shutdown = [ shutdown ]
    cls.init_beeswax_db()

  @classmethod
  def teardown_class(cls):
    if is_live_cluster():
      # Delete test DB and tables
      query_server = get_query_server_config()
      client = make_logged_in_client()
      user = User.objects.get(username='test')

      db = dbms.get(user, query_server)

      # Kill Spark context if running
      if is_hive_on_spark() and cluster.is_yarn():
        # TODO: We should clean up the running Hive on Spark job here
        pass

      for db_name in [cls.db_name, '%s_other' % cls.db_name]:
        databases = db.get_databases()

        if db_name in databases:
          tables = db.get_tables(database=db_name)
          for table in tables:
            make_query(client, 'DROP TABLE IF EXISTS `%(db)s`.`%(table)s`' % {'db': db_name, 'table': table}, wait=True)
          make_query(client, 'DROP VIEW IF EXISTS `%(db)s`.`myview`' % {'db': db_name}, wait=True)
          make_query(client, 'DROP DATABASE IF EXISTS %(db)s' % {'db': db_name}, wait=True)

          # Check the cleanup
          databases = db.get_databases()
          assert_false(db_name in databases)

      global _INITIALIZED
      _INITIALIZED = False

  @classmethod
  def set_execution_engine(cls):
    query_server = get_query_server_config()

    if query_server['server_name'] == 'beeswax' and is_hive_on_spark():
      user = User.objects.get(username='test')
      db = dbms.get(user, query_server)

      LOG.info("Setting Hive execution engine to Spark")
      db.execute_statement('SET hive.execution.engine=spark')

  @classmethod
  def init_beeswax_db(cls):
    """
    Install the common test tables (only once)
    """
    global _INITIALIZED
    if _INITIALIZED:
      return

    make_query(cls.client, 'CREATE DATABASE IF NOT EXISTS %(db)s' % {'db': cls.db_name}, wait=True)
    make_query(cls.client, 'CREATE DATABASE IF NOT EXISTS %(db)s_other' % {'db': cls.db_name}, wait=True)

    if cls.load_data:

      data_file = cls.cluster.fs_prefix + u'/beeswax/sample_data_échantillon_%d.tsv'

      # Create a "test_partitions" table.
      CREATE_PARTITIONED_TABLE = """
        CREATE TABLE `%(db)s`.`test_partitions` (foo INT, bar STRING)
        PARTITIONED BY (baz STRING, boom INT)
        ROW FORMAT DELIMITED
          FIELDS TERMINATED BY '\t'
          LINES TERMINATED BY '\n'
      """ % {'db': cls.db_name}
      make_query(cls.client, CREATE_PARTITIONED_TABLE, wait=True)
      cls._make_data_file(data_file % 1)

      LOAD_DATA = """
        LOAD DATA INPATH '%(data_file)s'
        OVERWRITE INTO TABLE `%(db)s`.`test_partitions`
        PARTITION (baz='baz_one', boom=12345)
      """ % {'db': cls.db_name, 'data_file': data_file % 1}
      make_query(cls.client, LOAD_DATA, wait=True, local=False)

      # Insert additional partition data into "test_partitions" table
      ADD_PARTITION = """
        ALTER TABLE `%(db)s`.`test_partitions` ADD PARTITION(baz='baz_foo', boom=67890) LOCATION '%(fs_prefix)s/baz_foo/boom_bar'
      """ % {'db': cls.db_name, 'fs_prefix': cls.cluster.fs_prefix}
      make_query(cls.client, ADD_PARTITION, wait=True, local=False)

      # Create a bunch of other tables
      CREATE_TABLE = """
        CREATE TABLE `%(db)s`.`%(name)s` (foo INT, bar STRING)
        COMMENT "%(comment)s"
        ROW FORMAT DELIMITED
          FIELDS TERMINATED BY '\t'
          LINES TERMINATED BY '\n'
      """

      # Create a "test" table.
      table_info = {'db': cls.db_name, 'name': 'test', 'comment': 'Test table'}
      cls._make_data_file(data_file % 2)
      cls._make_table(table_info['name'], CREATE_TABLE % table_info, data_file % 2)

      if is_live_cluster():
        LOG.warn('HUE-2884: We cannot create Hive UTF8 tables when live cluster testing at the moment')
      else:
        # Create a "test_utf8" table.
        table_info = {'db': cls.db_name, 'name': 'test_utf8', 'comment': cls.get_i18n_table_comment()}
        cls._make_i18n_data_file(data_file % 3, 'utf-8')
        cls._make_table(table_info['name'], CREATE_TABLE % table_info, data_file % 3)

        # Create a "test_latin1" table.
        table_info = {'db': cls.db_name, 'name': 'test_latin1', 'comment': cls.get_i18n_table_comment()}
        cls._make_i18n_data_file(data_file % 4, 'latin1')
        cls._make_table(table_info['name'], CREATE_TABLE % table_info, data_file % 4)

      # Create a "myview" view.
      make_query(cls.client, "CREATE VIEW `%(db)s`.`myview` (foo, bar) as SELECT * FROM `%(db)s`.`test`" % {'db': cls.db_name}, wait=True)

    _INITIALIZED = True

  @staticmethod
  def get_i18n_table_comment():
    return u'en-hello pt-Olá ch-你好 ko-안녕 ru-Здравствуйте'

  @classmethod
  def _make_table(cls, table_name, create_ddl, filename):
    make_query(cls.client, create_ddl, wait=True, database=cls.db_name)
    LOAD_DATA = """
      LOAD DATA INPATH '%(filename)s' OVERWRITE INTO TABLE `%(db)s`.`%(table_name)s`
    """ % {'filename': filename, 'table_name': table_name, 'db': cls.db_name}
    make_query(cls.client, LOAD_DATA, wait=True, local=False, database=cls.db_name)

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

  @classmethod
  def _make_custom_data_file(cls, filename, data):
    f = cls.cluster.fs.open(filename, "w")
    for x in data:
      f.write("%s\n" % x)
    f.close()

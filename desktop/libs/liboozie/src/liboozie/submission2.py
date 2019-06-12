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

import errno
import logging
import os
import time

from string import Template

from django.utils.functional import wraps
from django.utils.translation import ugettext as _

from beeswax.hive_site import get_hive_site_content
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_str
from desktop.lib.parameterization import find_variables
from desktop.lib.paths import get_desktop_root
from desktop.models import Document2
from indexer.conf import CONFIG_JDBC_LIBS_PATH
from metadata.conf import ALTUS
from oozie.utils import convert_to_server_timezone

from hadoop import cluster
from hadoop.fs.hadoopfs import Hdfs

from liboozie.conf import REMOTE_DEPLOYMENT_DIR, USE_LIBPATH_FOR_JARS
from liboozie.credentials import Credentials
from liboozie.oozie_api import get_oozie


LOG = logging.getLogger(__name__)


def submit_dryrun(run_func):
  def decorate(self, deployment_dir=None):
    if self.oozie_id is not None:
      raise Exception(_("Submission already submitted (Oozie job id %s)") % (self.oozie_id,))

    jt_address = cluster.get_cluster_addr_for_job_submission()

    if deployment_dir is None:
      self._update_properties(jt_address) # Needed as we need to set some properties like Credentials before
      deployment_dir = self.deploy()

    self._update_properties(jt_address, deployment_dir)
    if self.properties.get('dryrun'):
      self.api.dryrun(self.properties)
    return run_func(self, deployment_dir)
  return wraps(run_func)(decorate)


class Submission(object):
  """
  Represents one unique Oozie submission.

  Actions are:
  - submit
  - rerun
  """
  def __init__(self, user, job=None, fs=None, jt=None, properties=None, oozie_id=None, local_tz=None):
    self.job = job
    self.user = user
    self.fs = fs
    self.jt = jt # Deprecated with YARN, we now use logical names only for RM
    self.oozie_id = oozie_id
    self.api = get_oozie(self.user)

    if properties is not None:
      self.properties = properties
    else:
      self.properties = {}

    if local_tz and isinstance(self.job.data, dict):
      local_tz = self.job.data.get('properties')['timezone']

    # Modify start_date & end_date only when it's a coordinator
    from oozie.models2 import Coordinator
    if type(self.job) is Coordinator:
      if 'start_date' in self.properties:
        properties['start_date'] = convert_to_server_timezone(self.properties['start_date'], local_tz)
      if 'end_date' in self.properties:
        properties['end_date'] = convert_to_server_timezone(self.properties['end_date'], local_tz)

    if 'nominal_time' in self.properties:
      properties['nominal_time'] = convert_to_server_timezone(self.properties['nominal_time'], local_tz)

    self.properties['security_enabled'] = self.api.security_enabled

  def __str__(self):
    if self.oozie_id:
      res = "Submission for job '%s'." % (self.oozie_id,)
    else:
      res = "Submission for job '%s' (id %s, owner %s)." % (self.job.name, self.job.id, self.user)
    if self.oozie_id:
      res += " -- " + self.oozie_id
    return res

  @submit_dryrun
  def run(self, deployment_dir=None):
    """
    Take care of all the actions of submitting a Oozie workflow.
    Returns the oozie job id if all goes well.
    """

    if self.properties and 'oozie.use.system.libpath' not in self.properties:
      self.properties['oozie.use.system.libpath'] = 'true'

    self.oozie_id = self.api.submit_job(self.properties)
    LOG.info("Submitted: %s" % (self,))

    if self._is_workflow():
      self.api.job_control(self.oozie_id, 'start')
      LOG.info("Started: %s" % (self,))

    return self.oozie_id

  def rerun(self, deployment_dir, fail_nodes=None, skip_nodes=None):
    jt_address = cluster.get_cluster_addr_for_job_submission()

    self._update_properties(jt_address, deployment_dir)
    self.properties.update({'oozie.wf.application.path': deployment_dir})

    if 'oozie.coord.application.path' in self.properties:
      self.properties.pop('oozie.coord.application.path')

    if 'oozie.bundle.application.path' in self.properties:
      self.properties.pop('oozie.bundle.application.path')

    if fail_nodes:
      self.properties.update({'oozie.wf.rerun.failnodes': fail_nodes})
    elif not skip_nodes:
      self.properties.update({'oozie.wf.rerun.failnodes': 'false'}) # Case empty 'skip_nodes' list
    else:
      self.properties.update({'oozie.wf.rerun.skip.nodes': skip_nodes})

    self.api.rerun(self.oozie_id, properties=self.properties)

    LOG.info("Rerun: %s" % (self,))

    return self.oozie_id


  def rerun_coord(self, deployment_dir, params):
    jt_address = cluster.get_cluster_addr_for_job_submission()

    self._update_properties(jt_address, deployment_dir)
    self.properties.update({'oozie.coord.application.path': deployment_dir})

    self.api.job_control(self.oozie_id, action='coord-rerun', properties=self.properties, parameters=params)
    LOG.info("Rerun: %s" % (self,))

    return self.oozie_id

  def update_coord(self):
    self.api = get_oozie(self.user, api_version="v2")
    self.api.job_control(self.oozie_id, action='update', properties=self.properties, parameters=None)
    LOG.info("Update: %s" % (self,))

    return self.oozie_id

  def rerun_bundle(self, deployment_dir, params):
    jt_address = cluster.get_cluster_addr_for_job_submission()

    self._update_properties(jt_address, deployment_dir)
    self.properties.update({'oozie.bundle.application.path': deployment_dir})
    self.api.job_control(self.oozie_id, action='bundle-rerun', properties=self.properties, parameters=params)
    LOG.info("Rerun: %s" % (self,))

    return self.oozie_id


  def deploy(self, deployment_dir=None):
    try:
      if not deployment_dir:
        deployment_dir = self._create_deployment_dir()
    except Exception, ex:
      msg = _("Failed to create deployment directory: %s" % ex)
      LOG.exception(msg)
      raise PopupException(message=msg, detail=str(ex))

    if self.api.security_enabled:
      jt_address = cluster.get_cluster_addr_for_job_submission()
      self._update_properties(jt_address) # Needed for coordinator deploying workflows with credentials

    if hasattr(self.job, 'nodes'):
      for action in self.job.nodes:
        # Make sure XML is there
        # Don't support more than one level sub-workflow
        if action.data['type'] == 'subworkflow':
          from oozie.models2 import Workflow
          workflow = Workflow(document=Document2.objects.get_by_uuid(user=self.user, uuid=action.data['properties']['workflow']))
          sub_deploy = Submission(self.user, workflow, self.fs, self.jt, self.properties)
          workspace = sub_deploy.deploy()

          self.job.override_subworkflow_id(action, workflow.id) # For displaying the correct graph
          self.properties['workspace_%s' % workflow.uuid] = workspace # For pointing to the correct workspace

        elif action.data['type'] == 'altus' or \
            (action.data['type'] == 'spark-document' and 'altus' in self.properties.get('cluster', '')) or \
            (self.properties.get('auto-cluster') and 'document' in action.data['type']):
          is_altus_job = 'altus' in self.properties.get('cluster', '') and action.data['type'] != 'altus'
          is_scheduled_altus_job = self.properties.get('auto-cluster')

          self._create_file(deployment_dir, action.data['name'] + '.sh', '''#!/usr/bin/env bash

export PYTHONPATH=`pwd`

echo 'Starting Altus command...'

python altus.py

          ''')

          if is_altus_job:
            shell_script = self._generate_altus_job_action_script(
                service='dataeng',
                cluster=self.properties['cluster'],
                jobs=[{
                    'sparkJob': {
                        'jars': [u's3a://datawarehouse-customer360/ETL/spark-examples.jar'],
                        'mainClass': u'org.apache.spark.examples.SparkPi ',
                        'applicationArguments': [u'10']
                      },
                    'name': None,
                    'failureAction': 'NONE'
                }],
                auth_key_id=ALTUS.AUTH_KEY_ID.get(),
                auth_key_secret=ALTUS.AUTH_KEY_SECRET.get().replace('\\n', '\n')
            )
          elif is_scheduled_altus_job:
            shell_script = self._generate_altus_job_action_script(
                service='dataeng',
                cluster=self.properties['auto-cluster'],
                jobs=[],
                auth_key_id=ALTUS.AUTH_KEY_ID.get(),
                auth_key_secret=ALTUS.AUTH_KEY_SECRET.get().replace('\\n', '\n')
            )
          else:
            if action.data['properties'].get('service', '').lower().strip().startswith('query'):
              shell_script = self._generate_altus_warehouse_query_script(
                cluster_crn=action.data['properties'].get('service').split(' ')[-1],
                query=action.data['properties'].get('command'),
                auth_key_id=ALTUS.AUTH_KEY_ID.get(),
                auth_key_secret=ALTUS.AUTH_KEY_SECRET.get().replace('\\n', '\n')
              )
            else:
              shell_script = self._generate_altus_action_script(
                  service=action.data['properties'].get('service'),
                  command=action.data['properties'].get('command'),
                  arguments=dict([arg.split('=', 1) for arg in action.data['properties'].get('arguments', [])]),
                  auth_key_id=ALTUS.AUTH_KEY_ID.get(),
                  auth_key_secret=ALTUS.AUTH_KEY_SECRET.get().replace('\\n', '\n')
              )
            
          self._create_file(deployment_dir, 'altus.py', shell_script)

          ext_py_lib_path = os.path.join(get_desktop_root(), 'core', 'ext-py')
          lib_dir_path = os.path.join(self.job.deployment_dir, 'lib')
          libs = [
            (os.path.join(ext_py_lib_path, 'navoptapi-0.1.0'), 'navoptapi'),
            (os.path.join(ext_py_lib_path, 'navoptapi-0.1.0'), 'altuscli'),
            (os.path.join(ext_py_lib_path, 'asn1crypto-0.24.0'), 'asn1crypto'),
            (os.path.join(ext_py_lib_path, 'rsa-3.4.2'), 'rsa'),
            (os.path.join(ext_py_lib_path, 'pyasn1-0.1.8'), 'pyasn1'),
          ]
          for source_path, name in libs:
            destination_path = os.path.join(lib_dir_path, name)
            if not self.fs.do_as_user(self.user, self.fs.exists, destination_path):
              # Note: would be much faster to have only one zip archive
              self.fs.do_as_user(self.user, self.fs.copyFromLocal, os.path.join(source_path, name), destination_path)

        elif action.data['type'] == 'impala' or action.data['type'] == 'impala-document':
          from oozie.models2 import _get_impala_url
          from impala.impala_flags import get_ssl_server_certificate

          if action.data['type'] == 'impala-document':
            from notebook.models import Notebook
            if action.data['properties'].get('uuid'):
              notebook = Notebook(document=Document2.objects.get_by_uuid(user=self.user, uuid=action.data['properties']['uuid']))
              statements = notebook.get_str()
              statements = Template(statements).safe_substitute(**self.properties)
              script_name = action.data['name'] + '.sql'
              self._create_file(deployment_dir, script_name, statements)
          else:
            script_name = os.path.basename(action.data['properties'].get('script_path'))

          if self.api.security_enabled:
            kinit = 'kinit -k -t *.keytab %(user_principal)s' % {
              'user_principal': self.properties.get('user_principal', action.data['properties'].get('user_principal'))
            }
          else:
            kinit = ''

          shell_script = """#!/bin/bash

# Needed to launch impala shell in oozie
export PYTHON_EGG_CACHE=./myeggs

%(kinit)s

impala-shell %(kerberos_option)s %(ssl_option)s -i %(impalad_host)s -f %(query_file)s""" % {
  'impalad_host': action.data['properties'].get('impalad_host') or _get_impala_url(),
  'kerberos_option': '-k' if self.api.security_enabled else '',
  'ssl_option': '--ssl' if get_ssl_server_certificate() else '',
  'query_file': script_name,
  'kinit': kinit
  }

          self._create_file(deployment_dir, action.data['name'] + '.sh', shell_script)

        elif action.data['type'] == 'hive-document':
          from notebook.models import Notebook
          if action.data['properties'].get('uuid'):
            notebook = Notebook(document=Document2.objects.get_by_uuid(user=self.user, uuid=action.data['properties']['uuid']))
            statements = notebook.get_str(from_oozie_action=True)
          else:
            statements = action.data['properties'].get('statements')

          if self.properties.get('send_result_path'):
            statements = """
INSERT OVERWRITE DIRECTORY '%s'
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
   "separatorChar" = "\t",
   "quoteChar"     = "'",
   "escapeChar"    = "\\"
)
STORED AS TEXTFILE %s""" % (self.properties.get('send_result_path'), '\n\n\n'.join([snippet['statement_raw'] for snippet in notebook.get_data()['snippets']]))

          if statements is not None:
            self._create_file(deployment_dir, action.data['name'] + '.sql', statements)

        elif action.data['type'] in ('java-document', 'java', 'mapreduce-document'):
          if action.data['type'] == 'java-document' or action.data['type'] == 'mapreduce-document':
            from notebook.models import Notebook
            notebook = Notebook(document=Document2.objects.get_by_uuid(user=self.user, uuid=action.data['properties']['uuid']))
            properties = notebook.get_data()['snippets'][0]['properties']
          else:
            properties = action.data['properties']

          if properties.get('app_jar'):
            LOG.debug("Adding to oozie.libpath %s" % properties['app_jar'])
            paths = [properties['app_jar']]
            if self.properties.get('oozie.libpath'):
              paths.append(self.properties['oozie.libpath'])
            self.properties['oozie.libpath'] = ','.join(paths)

        elif action.data['type'] == 'pig-document':
          from notebook.models import Notebook
          notebook = Notebook(document=Document2.objects.get_by_uuid(user=self.user, uuid=action.data['properties']['uuid']))
          statements = notebook.get_data()['snippets'][0]['statement_raw']

          self._create_file(deployment_dir, action.data['name'] + '.pig', statements)
        elif action.data['type'] in ('spark', 'spark-document') or self._check_sqoop_statement(action):
          if not [f for f in action.data.get('properties').get('files', []) if f.get('value').endswith('hive-site.xml')]:
            hive_site_lib = Hdfs.join(deployment_dir + '/lib/', 'hive-site.xml')
            hive_site_content = get_hive_site_content()
            if not self.fs.do_as_user(self.user, self.fs.exists, hive_site_lib) and hive_site_content:
              self.fs.do_as_user(self.user, self.fs.create, hive_site_lib, overwrite=True, permission=0700, data=smart_str(hive_site_content))
          if action.data['type'] in ('sqoop', 'sqoop-document'):
            if CONFIG_JDBC_LIBS_PATH.get() and CONFIG_JDBC_LIBS_PATH.get() not in self.properties.get('oozie.libpath', ''):
              LOG.debug("Adding to oozie.libpath %s" % CONFIG_JDBC_LIBS_PATH.get())
              paths = [CONFIG_JDBC_LIBS_PATH.get()]
              if self.properties.get('oozie.libpath'):
                paths.append(self.properties['oozie.libpath'])
              self.properties['oozie.libpath'] = ','.join(paths)

    oozie_xml = self.job.to_xml(self.properties)
    self._do_as(self.user.username, self._copy_files, deployment_dir, oozie_xml, self.properties)

    return deployment_dir

  def _check_sqoop_statement(self, action):
    statement = ''
    if action.data['type'] == 'sqoop' and 'command' in action.data['properties']:         # Sqoop Workflow
      statement = action.data['properties']['command']
    elif action.data['type'] == 'sqoop-document' and 'uuid' in action.data['properties']: # Sqoop Editor
      from notebook.models import Notebook
      notebook = Notebook(document=Document2.objects.get_by_uuid(user=self.user, uuid=action.data['properties']['uuid']))
      statement = notebook.get_data()['snippets'][0]['statement_raw']
    return '--hive-import' in statement

  def get_external_parameters(self, application_path):
    """From XML and job.properties HDFS files"""
    deployment_dir = os.path.dirname(application_path)
    xml = self.fs.do_as_user(self.user, self.fs.read, application_path, 0, 1 * 1024**2)

    properties_file = deployment_dir + '/job.properties'
    if self.fs.do_as_user(self.user, self.fs.exists, properties_file):
      properties = self.fs.do_as_user(self.user, self.fs.read, properties_file, 0, 1 * 1024**2)
    else:
      properties = None

    return self._get_external_parameters(xml, properties)

  def _get_external_parameters(self, xml, properties=None):
    from oozie.models import DATASET_FREQUENCY
    parameters = dict([(var, '') for var in find_variables(xml, include_named=False) if not self._is_coordinator() or var not in DATASET_FREQUENCY])

    if properties:
      parameters.update(dict([line.strip().split('=')
                              for line in properties.split('\n') if not line.startswith('#') and len(line.strip().split('=')) == 2]))
    return parameters

  def _update_properties(self, jobtracker_addr, deployment_dir=None):
    LOG.info('Using FS %s and JT %s' % (self.fs, self.jt))

    if self.jt and self.jt.logical_name:
      jobtracker_addr = self.jt.logical_name

    if self.fs.logical_name:
      fs_defaultfs = self.fs.logical_name
    else:
      fs_defaultfs = self.fs.fs_defaultfs

    self.properties.update({
      'jobTracker': jobtracker_addr,
      'nameNode': fs_defaultfs,
    })

    if self.job and deployment_dir:
      self.properties.update({
        self.job.PROPERTY_APP_PATH: self.fs.get_hdfs_path(deployment_dir),
        self.job.HUE_ID: self.job.id
      })

    # Generate credentials when using security
    if self.api.security_enabled:
      credentials = Credentials()
      credentials.fetch(self.api)
      self.properties['credentials'] = credentials.get_properties()

      self._update_credentials_from_hive_action(credentials)


  def _update_credentials_from_hive_action(self, credentials):
    """
    Hive JDBC url from conf should be replaced when URL is set in hive action. Use _HOST from
    this URL to update the hive2_host in hive principal hive/hive2_host@YOUR-REALM.COM
    """
    if hasattr(self.job, 'nodes'):
      for action in self.job.nodes:
        if action.data['type'] in ('hive2', 'hive-document') and \
                        credentials.hiveserver2_name in self.properties['credentials'] and \
                        action.data['properties']['jdbc_url'] and \
                        len(action.data['properties']['jdbc_url'].split('//')) > 1:
          try:
            hive_jdbc_url = action.data['properties']['jdbc_url']
            hive_host_from_action = hive_jdbc_url.split('//')[1].split(':')[0]

            hive_principal_from_conf = self.properties['credentials'][credentials.hiveserver2_name]['properties'][1][1]
            updated_hive_principal = hive_principal_from_conf.split('/')[0] + '/' + hive_host_from_action + '@' + hive_principal_from_conf.split('@')[1]

            self.properties['credentials'][credentials.hiveserver2_name]['properties'] = [
              ('hive2.jdbc.url', hive_jdbc_url),
              ('hive2.server.principal', updated_hive_principal)
            ]
          except Exception, ex:
            msg = 'Failed to update the Hive JDBC URL from %s action properties: %s' % (action.data['type'], str(ex))
            LOG.error(msg)
            raise PopupException(message=_(msg), detail=str(ex))



  def _create_deployment_dir(self):
    """
    Return the job deployment directory in HDFS, creating it if necessary.
    The actual deployment dir should be 0711 owned by the user
    """
    # Automatic setup of the required directories if needed
    create_directories(self.fs)

    # Check if job owner owns the deployment directory.
    has_deployment_dir_access = False
    if self.job.deployment_dir and self.fs.exists(self.job.deployment_dir):
      statbuf = self.fs.stats(self.job.deployment_dir)
      has_deployment_dir_access = statbuf and (statbuf.user == self.user.username)

    # Case of a shared job
    if self.job.document and self.user != self.job.document.owner or not has_deployment_dir_access:
      path = REMOTE_DEPLOYMENT_DIR.get().replace('$USER', self.user.username).replace('$TIME', str(time.time())).replace('$JOBID', str(self.job.id))
      # Shared coords or bundles might not have any existing workspaces
      if self.fs.exists(self.job.deployment_dir):
        self.fs.copy_remote_dir(self.job.deployment_dir, path, owner=self.user)
      else:
        self._create_dir(path)
    else:
      path = self.job.deployment_dir
      self._create_dir(path)
    return path

  def _create_dir(self, path, perms=None):
    """
    Return the directory in HDFS, creating it if necessary.
    """
    try:
      statbuf = self.fs.stats(path)
      if not statbuf.isDir:
        msg = _("Path is not a directory: %s.") % (path,)
        LOG.error(msg)
        raise Exception(msg)
    except IOError, ex:
      if ex.errno != errno.ENOENT:
        msg = _("Error accessing directory '%s': %s.") % (path, ex)
        LOG.exception(msg)
        raise IOError(ex.errno, msg)

    if not self.fs.exists(path):
      self._do_as(self.user.username, self.fs.mkdir, path, perms)

    if perms is not None:
      self._do_as(self.user.username, self.fs.chmod, path, perms)

    return path

  def _copy_files(self, deployment_dir, oozie_xml, oozie_properties):
    """
    Copy XML and the jar_path files from Java or MR actions to the deployment directory.
    This should run as the workflow user.
    """

    self._create_file(deployment_dir, self.job.XML_FILE_NAME, oozie_xml)
    self._create_file(deployment_dir, 'job.properties', data='\n'.join(['%s=%s' % (key, val) for key, val in oozie_properties.iteritems()]))

    # List jar files
    files = []
    lib_path = self.fs.join(deployment_dir, 'lib')
    if hasattr(self.job, 'nodes'):
      for node in self.job.nodes:
        jar_path = node.data['properties'].get('jar_path')
        if jar_path:
          if not jar_path.startswith('/'): # If workspace relative path
            jar_path = self.fs.join(self.job.deployment_dir, jar_path)
          if not jar_path.startswith(lib_path): # If not already in lib
            files.append(jar_path)

    if USE_LIBPATH_FOR_JARS.get():
      # Add the jar files to the oozie.libpath
      if files:
        files = list(set(files))
        LOG.debug("Adding to oozie.libpath %s" % files)
        if self.properties.get('oozie.libpath'):
          files.append(self.properties['oozie.libpath'])
        self.properties['oozie.libpath'] = ','.join(files)
    else:
      # Copy the jar files to the workspace lib
      if files:
        for jar_file in files:
          LOG.debug("Updating %s" % jar_file)
          jar_lib_path = self.fs.join(lib_path, self.fs.basename(jar_file))
          # Refresh if needed
          if self.fs.exists(jar_lib_path) and self.fs.exists(jar_file):
            stat_src = self.fs.stats(jar_file)
            stat_dest = self.fs.stats(jar_lib_path)
            if stat_src.fileId != stat_dest.fileId:
              self.fs.remove(jar_lib_path, skip_trash=True)
          self.fs.copyfile(jar_file, jar_lib_path)

  def _do_as(self, username, fn, *args, **kwargs):
    prev_user = self.fs.user
    try:
      self.fs.setuser(username)
      return fn(*args, **kwargs)
    finally:
      self.fs.setuser(prev_user)

  def remove_deployment_dir(self):
    """Delete the workflow deployment directory."""
    try:
      path = self.job.deployment_dir
      if self._do_as(self.user.username , self.fs.exists, path):
        self._do_as(self.user.username , self.fs.rmtree, path)
    except Exception, ex:
      LOG.warn("Failed to clean up workflow deployment directory for %s (owner %s). Caused by: %s", self.job.name, self.user, ex)

  def _is_workflow(self):
    from oozie.models2 import Workflow
    return Workflow.PROPERTY_APP_PATH in self.properties

  def _is_coordinator(self):
    from oozie.models2 import Coordinator
    return Coordinator.PROPERTY_APP_PATH in self.properties

  def _create_file(self, deployment_dir, file_name, data, do_as=False):
    file_path = self.fs.join(deployment_dir, file_name)
    if do_as:
      self.fs.do_as_user(self.user, self.fs.create, file_path, overwrite=True, permission=0644, data=smart_str(data))
    else:
      self.fs.create(file_path, overwrite=True, permission=0644, data=smart_str(data))
    LOG.debug("Created/Updated %s" % (file_path,))

  def _generate_altus_action_script(self, service, command, arguments, auth_key_id, auth_key_secret):
    if service == 'analyticdb' or service == 'dataware':
      hostname = ALTUS.HOSTNAME_ANALYTICDB.get()
    elif service == 'dataeng':
      hostname = ALTUS.HOSTNAME_DATAENG.get()
    elif service == 'wa':
      hostname = ALTUS.HOSTNAME_WA.get()
    else:
      hostname = ALTUS.HOSTNAME.get()

    return """#!/usr/bin/env python

from navoptapi.api_lib import ApiLib

hostname = '%(hostname)s'
auth_key_id = '%(auth_key_id)s'
auth_key_secret = '''%(auth_key_secret)s'''

def _exec(service, command, parameters=None):
  if parameters is None:
    parameters = {}

  try:
    api = ApiLib(service, hostname, auth_key_id, auth_key_secret)
    resp = api.call_api(command, parameters)
    return resp.json()
  except Exception, e:
    print e
    raise e

print _exec('%(service)s', '%(command)s', %(args)s)

""" % {
      'hostname': hostname,
      'service': service,
      'command': command,
      'args': arguments,
      'auth_key_id': auth_key_id,
      'auth_key_secret': auth_key_secret
    }

  def _generate_altus_job_action_script(self, service, cluster, jobs, auth_key_id, auth_key_secret):
    if service == 'analyticdb' or service == 'dataware':
      hostname = ALTUS.HOSTNAME_ANALYTICDB.get()
    elif service == 'dataeng':
      hostname = ALTUS.HOSTNAME_DATAENG.get()
    elif service == 'wa':
      hostname = ALTUS.HOSTNAME_WA.get()
    else:
      hostname = ALTUS.HOSTNAME.get()

    if type(cluster) == dict:
      command = 'createAWSCluster'
      arguments = cluster
    else:
      command = 'submitJobs'
      arguments = {'clusterName': cluster, 'jobs': jobs}

    return """#!/usr/bin/env python

import time

from ast import literal_eval

from navoptapi.api_lib import ApiLib

hostname = '%(hostname)s'
arguments = literal_eval("%(arguments)s")
auth_key_id = '%(auth_key_id)s'
auth_key_secret = '''%(auth_key_secret)s'''

def _exec(service, command, parameters=None):
  if parameters is None:
    parameters = {}

  try:
    api = ApiLib(service, hostname, auth_key_id, auth_key_secret)
    resp = api.call_api(command, parameters)
    return resp.json()
  except Exception, e:
    print e
    raise e


try:    
  handle = _exec('%(service)s', '%(command)s', arguments)
  
  if 'create' in '%(command)s':
    handle = _exec('%(service)s', 'listJobs', {'clusterCrn': handle['cluster']['crn']})

  while handle['jobs']:
    job = handle['jobs'].pop(0)
    status = 'QUEUED'
    print 'Job submitted: %%(jobId)s' %% job
  
    while status in ('QUEUED', 'RUNNING', 'SUBMITTING'):
      time.sleep(5)
  
      print 'Checking status...'
      status = _exec('%(service)s', 'describeJob', {'jobId': job['jobId']})['job']['status']
  
    if status != 'COMPLETED':
      raise Exception('Job %%s failed %%s' %% (job['jobId'], status))
    else:
      print 'Job %%(jobId)s completed successfully' %% job
except Exception, e:
  print e
  raise e

""" % {
      'service': service,
      'hostname': hostname,      
      'command': command,
      'arguments': repr(arguments),
      'auth_key_id': auth_key_id,
      'auth_key_secret': auth_key_secret
    }

  def _generate_altus_warehouse_query_script(self, cluster_crn, query, auth_key_id, auth_key_secret):
    service = 'dataware'
    hostname = ALTUS.HOSTNAME_ANALYTICDB.get()

    return """#!/usr/bin/env python

import urllib

from navoptapi.api_lib import ApiLib

hostname = '%(hostname)s'
auth_key_id = '%(auth_key_id)s'
auth_key_secret = '''%(auth_key_secret)s'''
query = '%(query)s'
cluster_crn = '%(cluster_crn)s'
payload = '''%(payload)s'''.replace('show+tables', urllib.quote_plus(query.replace('\\n', ' ')))

def _exec(service, command, parameters=None):
  if parameters is None:
    parameters = {}

  try:
    api = ApiLib(service, hostname, auth_key_id, auth_key_secret)
    resp = api.call_api(command, parameters)
    return resp.json()
  except Exception, e:
    print e
    raise e

print _exec('%(service)s', 'submitHueQuery', {'clusterCrn': cluster_crn, 'payload': payload})

""" % {
      'hostname': hostname,
      'service': service,
      'cluster_crn': cluster_crn,
      'query': query,
      'auth_key_id': auth_key_id,
      'auth_key_secret': auth_key_secret,
      'payload': '''{
              "method": "POST",
              "url": "http://127.0.0.1:8000/notebook/api/execute/impala",
              "httpVersion": "HTTP/1.1",
              "headers": [
                {
                  "name": "Accept-Encoding",
                  "value": "gzip, deflate, br"
                },
                {
                  "name": "Content-Type",
                  "value": "application/x-www-form-urlencoded; charset=UTF-8"
                },
                {
                  "name": "Accept",
                  "value": "*/*"
                },
                {
                  "name": "X-Requested-With",
                  "value": "XMLHttpRequest"
                },
                {
                  "name": "Connection",
                  "value": "keep-alive"
                }
              ],
              "queryString": [],
              "cookies": [
              ],
              "postData": {
                "mimeType": "application/x-www-form-urlencoded; charset=UTF-8",
                "text": "notebook=%7B%22uuid%22%3A%22f2b8a233-c34c-44b8-a8a1-0e6123996216%22%2C%22name%22%3A%22%22%2C%22description%22%3A%22%22%2C%22type%22%3A%22query-impala%22%2C%22initialType%22%3A%22impala%22%2C%22coordinatorUuid%22%3Anull%2C%22isHistory%22%3Atrue%2C%22isManaged%22%3Afalse%2C%22parentSavedQueryUuid%22%3Anull%2C%22isSaved%22%3Afalse%2C%22onSuccessUrl%22%3Anull%2C%22pubSubUrl%22%3Anull%2C%22isPresentationModeDefault%22%3Afalse%2C%22isPresentationMode%22%3Afalse%2C%22isPresentationModeInitialized%22%3Atrue%2C%22presentationSnippets%22%3A%7B%7D%2C%22isHidingCode%22%3Afalse%2C%22snippets%22%3A%5B%7B%22id%22%3A%22dd5755a3-e8db-82d9-4f98-9f4fb5a99a06%22%2C%22name%22%3A%22%22%2C%22type%22%3A%22impala%22%2C%22isBatchable%22%3Atrue%2C%22aceCursorPosition%22%3A%7B%22column%22%3A33%2C%22row%22%3A0%7D%2C%22errors%22%3A%5B%5D%2C%22aceErrorsHolder%22%3A%5B%5D%2C%22aceWarningsHolder%22%3A%5B%5D%2C%22aceErrors%22%3A%5B%5D%2C%22aceWarnings%22%3A%5B%5D%2C%22editorMode%22%3Atrue%2C%22dbSelectionVisible%22%3Afalse%2C%22isSqlDialect%22%3Atrue%2C%22namespaceRefreshEnabled%22%3Afalse%2C%22availableNamespaces%22%3A%5B%5D%2C%22availableComputes%22%3A%5B%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22default-romain%22%2C%22id%22%3A%22default-romain%22%2C%22name%22%3A%22default-romain%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22compute1%22%2C%22id%22%3A%22compute1%22%2C%22name%22%3A%22compute1%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22compute2%22%2C%22id%22%3A%22compute2%22%2C%22name%22%3A%22compute2%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22altus%22%2C%22namespace%22%3A%22Altus%22%2C%22id%22%3A%22Altus%22%2C%22name%22%3A%22Altus%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22storage1%22%2C%22id%22%3A%22storage1%22%2C%22name%22%3A%22storage1%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22storage2%22%2C%22id%22%3A%22storage2%22%2C%22name%22%3A%22storage2%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22Default%22%2C%22id%22%3A%22Default%22%2C%22name%22%3A%22default%22%7D%5D%2C%22compute%22%3A%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22default-romain%22%2C%22id%22%3A%22default-romain%22%2C%22name%22%3A%22default-romain%22%7D%2C%22database%22%3A%22default%22%2C%22currentQueryTab%22%3A%22queryHistory%22%2C%22pinnedContextTabs%22%3A%5B%5D%2C%22loadingQueries%22%3Afalse%2C%22queriesHasErrors%22%3Afalse%2C%22queriesCurrentPage%22%3A1%2C%22queriesTotalPages%22%3A1%2C%22queriesFilter%22%3A%22%22%2C%22queriesFilterVisible%22%3Afalse%2C%22statementType%22%3A%22text%22%2C%22statementTypes%22%3A%5B%22text%22%2C%22file%22%5D%2C%22statementPath%22%3A%22%22%2C%22externalStatementLoaded%22%3Afalse%2C%22associatedDocumentLoading%22%3Atrue%2C%22associatedDocumentUuid%22%3Anull%2C%22statement_raw%22%3A%22show+tables%3B%22%2C%22statementsList%22%3A%5B%22show+tables%3B%22%5D%2C%22aceSize%22%3A100%2C%22status%22%3A%22running%22%2C%22statusForButtons%22%3A%22executing%22%2C%22properties%22%3A%7B%22files%22%3A%5B%5D%2C%22functions%22%3A%5B%5D%2C%22arguments%22%3A%5B%5D%2C%22settings%22%3A%5B%5D%7D%2C%22viewSettings%22%3A%7B%22placeHolder%22%3A%22Example%3A+SELECT+*+FROM+tablename%2C+or+press+CTRL+%2B+space%22%2C%22sqlDialect%22%3Atrue%7D%2C%22variables%22%3A%5B%5D%2C%22hasCurlyBracketParameters%22%3Atrue%2C%22variableNames%22%3A%5B%5D%2C%22variableValues%22%3A%7B%7D%2C%22statement%22%3A%22show+tables%3B%22%2C%22result%22%3A%7B%22id%22%3A%2206840534-9434-33b5-5eca-2cd08432ceb3%22%2C%22type%22%3A%22table%22%2C%22hasResultset%22%3Atrue%2C%22handle%22%3A%7B%22has_more_statements%22%3Afalse%2C%22statement_id%22%3A0%2C%22statements_count%22%3A1%2C%22previous_statement_hash%22%3A%22acb6478fcf28c31b5e76d49de7d77bbe46fe5e4f9436c16c0ca8ed5f%22%7D%2C%22meta%22%3A%5B%5D%2C%22rows%22%3Anull%2C%22hasMore%22%3Afalse%2C%22statement_id%22%3A0%2C%22statement_range%22%3A%7B%22start%22%3A%7B%22row%22%3A0%2C%22column%22%3A0%7D%2C%22end%22%3A%7B%22row%22%3A0%2C%22column%22%3A0%7D%7D%2C%22statements_count%22%3A1%2C%22previous_statement_hash%22%3Anull%2C%22metaFilter%22%3A%7B%22query%22%3A%22%22%2C%22facets%22%3A%7B%7D%2C%22text%22%3A%5B%5D%7D%2C%22isMetaFilterVisible%22%3Afalse%2C%22filteredMetaChecked%22%3Atrue%2C%22filteredMeta%22%3A%5B%5D%2C%22fetchedOnce%22%3Afalse%2C%22startTime%22%3A%222018-06-12T16%3A15%3A01.951Z%22%2C%22endTime%22%3A%222018-06-12T16%3A15%3A01.951Z%22%2C%22executionTime%22%3A0%2C%22data%22%3A%5B%5D%2C%22explanation%22%3A%22%22%2C%22logs%22%3A%22%22%2C%22logLines%22%3A0%2C%22hasSomeResults%22%3Afalse%7D%2C%22showGrid%22%3Atrue%2C%22showChart%22%3Afalse%2C%22showLogs%22%3Atrue%2C%22progress%22%3A0%2C%22jobs%22%3A%5B%5D%2C%22isLoading%22%3Afalse%2C%22resultsKlass%22%3A%22results+impala%22%2C%22errorsKlass%22%3A%22results+impala+alert+alert-error%22%2C%22is_redacted%22%3Afalse%2C%22chartType%22%3A%22bars%22%2C%22chartSorting%22%3A%22none%22%2C%22chartScatterGroup%22%3Anull%2C%22chartScatterSize%22%3Anull%2C%22chartScope%22%3A%22world%22%2C%22chartTimelineType%22%3A%22bar%22%2C%22chartLimits%22%3A%5B5%2C10%2C25%2C50%2C100%5D%2C%22chartLimit%22%3Anull%2C%22chartX%22%3Anull%2C%22chartXPivot%22%3Anull%2C%22chartYSingle%22%3Anull%2C%22chartYMulti%22%3A%5B%5D%2C%22chartData%22%3A%5B%5D%2C%22chartMapType%22%3A%22marker%22%2C%22chartMapLabel%22%3Anull%2C%22chartMapHeat%22%3Anull%2C%22hideStacked%22%3Atrue%2C%22hasDataForChart%22%3Afalse%2C%22previousChartOptions%22%3A%7B%22chartLimit%22%3Anull%2C%22chartX%22%3Anull%2C%22chartXPivot%22%3Anull%2C%22chartYSingle%22%3Anull%2C%22chartMapType%22%3A%22marker%22%2C%22chartMapLabel%22%3Anull%2C%22chartMapHeat%22%3Anull%2C%22chartYMulti%22%3A%5B%5D%2C%22chartScope%22%3A%22world%22%2C%22chartTimelineType%22%3A%22bar%22%2C%22chartSorting%22%3A%22none%22%2C%22chartScatterGroup%22%3Anull%2C%22chartScatterSize%22%3Anull%7D%2C%22isResultSettingsVisible%22%3Afalse%2C%22settingsVisible%22%3Afalse%2C%22checkStatusTimeout%22%3Anull%2C%22topRisk%22%3Anull%2C%22suggestion%22%3A%22%22%2C%22hasSuggestion%22%3Anull%2C%22compatibilityCheckRunning%22%3Afalse%2C%22compatibilitySourcePlatform%22%3A%22impala%22%2C%22compatibilitySourcePlatforms%22%3A%5B%7B%22name%22%3A%22Teradata%22%2C%22value%22%3A%22teradata%22%7D%2C%7B%22name%22%3A%22Oracle%22%2C%22value%22%3A%22oracle%22%7D%2C%7B%22name%22%3A%22Netezza%22%2C%22value%22%3A%22netezza%22%7D%2C%7B%22name%22%3A%22Impala%22%2C%22value%22%3A%22impala%22%7D%2C%7B%22name%22%3A%22impala%22%2C%22value%22%3A%22impala%22%7D%2C%7B%22name%22%3A%22DB2%22%2C%22value%22%3A%22db2%22%7D%2C%7B%22name%22%3A%22Greenplum%22%2C%22value%22%3A%22greenplum%22%7D%2C%7B%22name%22%3A%22MySQL%22%2C%22value%22%3A%22mysql%22%7D%2C%7B%22name%22%3A%22PostgreSQL%22%2C%22value%22%3A%22postgresql%22%7D%2C%7B%22name%22%3A%22Informix%22%2C%22value%22%3A%22informix%22%7D%2C%7B%22name%22%3A%22SQL+Server%22%2C%22value%22%3A%22sqlserver%22%7D%2C%7B%22name%22%3A%22Sybase%22%2C%22value%22%3A%22sybase%22%7D%2C%7B%22name%22%3A%22Access%22%2C%22value%22%3A%22access%22%7D%2C%7B%22name%22%3A%22Firebird%22%2C%22value%22%3A%22firebird%22%7D%2C%7B%22name%22%3A%22ANSISQL%22%2C%22value%22%3A%22ansisql%22%7D%2C%7B%22name%22%3A%22Generic%22%2C%22value%22%3A%22generic%22%7D%5D%2C%22compatibilityTargetPlatform%22%3A%22impala%22%2C%22compatibilityTargetPlatforms%22%3A%5B%7B%22name%22%3A%22Impala%22%2C%22value%22%3A%22impala%22%7D%2C%7B%22name%22%3A%22impala%22%2C%22value%22%3A%22impala%22%7D%5D%2C%22showOptimizer%22%3Atrue%2C%22delayedStatement%22%3A%22show+tables%3B%22%2C%22wasBatchExecuted%22%3Afalse%2C%22isReady%22%3Atrue%2C%22lastExecuted%22%3A1528820101947%2C%22lastAceSelectionRowOffset%22%3A0%2C%22executingBlockingOperation%22%3Anull%2C%22showLongOperationWarning%22%3Afalse%2C%22formatEnabled%22%3Atrue%2C%22isFetchingData%22%3Afalse%2C%22isCanceling%22%3Afalse%2C%22aceAutoExpand%22%3Afalse%7D%5D%2C%22selectedSnippet%22%3A%22impala%22%2C%22creatingSessionLocks%22%3A%5B%5D%2C%22sessions%22%3A%5B%7B%22type%22%3A%22impala%22%2C%22properties%22%3A%5B%7B%22multiple%22%3Atrue%2C%22defaultValue%22%3A%5B%5D%2C%22value%22%3A%5B%5D%2C%22nice_name%22%3A%22Files%22%2C%22key%22%3A%22files%22%2C%22help_text%22%3A%22Add+one+or+more+files%2C+jars%2C+or+arcimpalas+to+the+list+of+resources.%22%2C%22type%22%3A%22hdfs-files%22%7D%2C%7B%22multiple%22%3Atrue%2C%22defaultValue%22%3A%5B%5D%2C%22value%22%3A%5B%5D%2C%22nice_name%22%3A%22Functions%22%2C%22key%22%3A%22functions%22%2C%22help_text%22%3A%22Add+one+or+more+registered+UDFs+(requires+function+name+and+fully-qualified+class+name).%22%2C%22type%22%3A%22functions%22%7D%2C%7B%22nice_name%22%3A%22Settings%22%2C%22multiple%22%3Atrue%2C%22key%22%3A%22settings%22%2C%22help_text%22%3A%22impala+and+Hadoop+configuration+properties.%22%2C%22defaultValue%22%3A%5B%5D%2C%22type%22%3A%22settings%22%2C%22options%22%3A%5B%22impala.map.aggr%22%2C%22impala.exec.compress.output%22%2C%22impala.exec.parallel%22%2C%22impala.execution.engine%22%2C%22mapreduce.job.queuename%22%5D%2C%22value%22%3A%5B%5D%7D%5D%2C%22reuse_session%22%3Atrue%2C%22id%22%3A6865%2C%22session_id%22%3A%22714fb09b96ba3368%3A4d02ec93d7ffbfb6%22%7D%5D%2C%22directoryUuid%22%3A%22%22%2C%22dependentsCoordinator%22%3A%5B%5D%2C%22historyFilter%22%3A%22%22%2C%22historyFilterVisible%22%3Afalse%2C%22loadingHistory%22%3Afalse%2C%22historyInitialHeight%22%3A1679%2C%22forceHistoryInitialHeight%22%3Atrue%2C%22historyCurrentPage%22%3A1%2C%22historyTotalPages%22%3A3%2C%22schedulerViewModel%22%3Anull%2C%22schedulerViewModelIsLoaded%22%3Afalse%2C%22isBatchable%22%3Atrue%2C%22isExecutingAll%22%3Afalse%2C%22executingAllIndex%22%3A0%2C%22retryModalConfirm%22%3Anull%2C%22retryModalCancel%22%3Anull%2C%22unloaded%22%3Afalse%2C%22updateHistoryFailed%22%3Afalse%2C%22viewSchedulerId%22%3A%22%22%2C%22loadingScheduler%22%3Afalse%7D&snippet=%7B%22id%22%3A%22dd5755a3-e8db-82d9-4f98-9f4fb5a99a06%22%2C%22type%22%3A%22impala%22%2C%22status%22%3A%22running%22%2C%22statementType%22%3A%22text%22%2C%22statement%22%3A%22show+tables%3B%22%2C%22aceCursorPosition%22%3A%7B%22column%22%3A33%2C%22row%22%3A0%7D%2C%22statementPath%22%3A%22%22%2C%22associatedDocumentUuid%22%3Anull%2C%22properties%22%3A%7B%22files%22%3A%5B%5D%2C%22functions%22%3A%5B%5D%2C%22arguments%22%3A%5B%5D%2C%22settings%22%3A%5B%5D%7D%2C%22result%22%3A%7B%22id%22%3A%2206840534-9434-33b5-5eca-2cd08432ceb3%22%2C%22type%22%3A%22table%22%2C%22handle%22%3A%7B%22has_more_statements%22%3Afalse%2C%22statement_id%22%3A0%2C%22statements_count%22%3A1%2C%22previous_statement_hash%22%3A%22acb6478fcf28c31b5e76d49de7d77bbe46fe5e4f9436c16c0ca8ed5f%22%7D%7D%2C%22database%22%3A%22default%22%2C%22compute%22%3A%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22default-romain%22%2C%22id%22%3A%22default-romain%22%2C%22name%22%3A%22default-romain%22%7D%2C%22wasBatchExecuted%22%3Afalse%7D",
                "params": [
                  {
                    "name": "notebook",
                    "value": "%7B%22uuid%22%3A%22f2b8a233-c34c-44b8-a8a1-0e6123996216%22%2C%22name%22%3A%22%22%2C%22description%22%3A%22%22%2C%22type%22%3A%22query-impala%22%2C%22initialType%22%3A%22impala%22%2C%22coordinatorUuid%22%3Anull%2C%22isHistory%22%3Atrue%2C%22isManaged%22%3Afalse%2C%22parentSavedQueryUuid%22%3Anull%2C%22isSaved%22%3Afalse%2C%22onSuccessUrl%22%3Anull%2C%22pubSubUrl%22%3Anull%2C%22isPresentationModeDefault%22%3Afalse%2C%22isPresentationMode%22%3Afalse%2C%22isPresentationModeInitialized%22%3Atrue%2C%22presentationSnippets%22%3A%7B%7D%2C%22isHidingCode%22%3Afalse%2C%22snippets%22%3A%5B%7B%22id%22%3A%22dd5755a3-e8db-82d9-4f98-9f4fb5a99a06%22%2C%22name%22%3A%22%22%2C%22type%22%3A%22impala%22%2C%22isBatchable%22%3Atrue%2C%22aceCursorPosition%22%3A%7B%22column%22%3A33%2C%22row%22%3A0%7D%2C%22errors%22%3A%5B%5D%2C%22aceErrorsHolder%22%3A%5B%5D%2C%22aceWarningsHolder%22%3A%5B%5D%2C%22aceErrors%22%3A%5B%5D%2C%22aceWarnings%22%3A%5B%5D%2C%22editorMode%22%3Atrue%2C%22dbSelectionVisible%22%3Afalse%2C%22isSqlDialect%22%3Atrue%2C%22namespaceRefreshEnabled%22%3Afalse%2C%22availableNamespaces%22%3A%5B%5D%2C%22availableComputes%22%3A%5B%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22default-romain%22%2C%22id%22%3A%22default-romain%22%2C%22name%22%3A%22default-romain%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22compute1%22%2C%22id%22%3A%22compute1%22%2C%22name%22%3A%22compute1%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22compute2%22%2C%22id%22%3A%22compute2%22%2C%22name%22%3A%22compute2%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22altus%22%2C%22namespace%22%3A%22Altus%22%2C%22id%22%3A%22Altus%22%2C%22name%22%3A%22Altus%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22storage1%22%2C%22id%22%3A%22storage1%22%2C%22name%22%3A%22storage1%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22storage2%22%2C%22id%22%3A%22storage2%22%2C%22name%22%3A%22storage2%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22Default%22%2C%22id%22%3A%22Default%22%2C%22name%22%3A%22default%22%7D%5D%2C%22compute%22%3A%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22default-romain%22%2C%22id%22%3A%22default-romain%22%2C%22name%22%3A%22default-romain%22%7D%2C%22database%22%3A%22default%22%2C%22currentQueryTab%22%3A%22queryHistory%22%2C%22pinnedContextTabs%22%3A%5B%5D%2C%22loadingQueries%22%3Afalse%2C%22queriesHasErrors%22%3Afalse%2C%22queriesCurrentPage%22%3A1%2C%22queriesTotalPages%22%3A1%2C%22queriesFilter%22%3A%22%22%2C%22queriesFilterVisible%22%3Afalse%2C%22statementType%22%3A%22text%22%2C%22statementTypes%22%3A%5B%22text%22%2C%22file%22%5D%2C%22statementPath%22%3A%22%22%2C%22externalStatementLoaded%22%3Afalse%2C%22associatedDocumentLoading%22%3Atrue%2C%22associatedDocumentUuid%22%3Anull%2C%22statement_raw%22%3A%22show+tables%3B%22%2C%22statementsList%22%3A%5B%22show+tables%3B%22%5D%2C%22aceSize%22%3A100%2C%22status%22%3A%22running%22%2C%22statusForButtons%22%3A%22executing%22%2C%22properties%22%3A%7B%22files%22%3A%5B%5D%2C%22functions%22%3A%5B%5D%2C%22arguments%22%3A%5B%5D%2C%22settings%22%3A%5B%5D%7D%2C%22viewSettings%22%3A%7B%22placeHolder%22%3A%22Example%3A+SELECT+*+FROM+tablename%2C+or+press+CTRL+%2B+space%22%2C%22sqlDialect%22%3Atrue%7D%2C%22variables%22%3A%5B%5D%2C%22hasCurlyBracketParameters%22%3Atrue%2C%22variableNames%22%3A%5B%5D%2C%22variableValues%22%3A%7B%7D%2C%22statement%22%3A%22show+tables%3B%22%2C%22result%22%3A%7B%22id%22%3A%2206840534-9434-33b5-5eca-2cd08432ceb3%22%2C%22type%22%3A%22table%22%2C%22hasResultset%22%3Atrue%2C%22handle%22%3A%7B%22has_more_statements%22%3Afalse%2C%22statement_id%22%3A0%2C%22statements_count%22%3A1%2C%22previous_statement_hash%22%3A%22acb6478fcf28c31b5e76d49de7d77bbe46fe5e4f9436c16c0ca8ed5f%22%7D%2C%22meta%22%3A%5B%5D%2C%22rows%22%3Anull%2C%22hasMore%22%3Afalse%2C%22statement_id%22%3A0%2C%22statement_range%22%3A%7B%22start%22%3A%7B%22row%22%3A0%2C%22column%22%3A0%7D%2C%22end%22%3A%7B%22row%22%3A0%2C%22column%22%3A0%7D%7D%2C%22statements_count%22%3A1%2C%22previous_statement_hash%22%3Anull%2C%22metaFilter%22%3A%7B%22query%22%3A%22%22%2C%22facets%22%3A%7B%7D%2C%22text%22%3A%5B%5D%7D%2C%22isMetaFilterVisible%22%3Afalse%2C%22filteredMetaChecked%22%3Atrue%2C%22filteredMeta%22%3A%5B%5D%2C%22fetchedOnce%22%3Afalse%2C%22startTime%22%3A%222018-06-12T16%3A15%3A01.951Z%22%2C%22endTime%22%3A%222018-06-12T16%3A15%3A01.951Z%22%2C%22executionTime%22%3A0%2C%22data%22%3A%5B%5D%2C%22explanation%22%3A%22%22%2C%22logs%22%3A%22%22%2C%22logLines%22%3A0%2C%22hasSomeResults%22%3Afalse%7D%2C%22showGrid%22%3Atrue%2C%22showChart%22%3Afalse%2C%22showLogs%22%3Atrue%2C%22progress%22%3A0%2C%22jobs%22%3A%5B%5D%2C%22isLoading%22%3Afalse%2C%22resultsKlass%22%3A%22results+impala%22%2C%22errorsKlass%22%3A%22results+impala+alert+alert-error%22%2C%22is_redacted%22%3Afalse%2C%22chartType%22%3A%22bars%22%2C%22chartSorting%22%3A%22none%22%2C%22chartScatterGroup%22%3Anull%2C%22chartScatterSize%22%3Anull%2C%22chartScope%22%3A%22world%22%2C%22chartTimelineType%22%3A%22bar%22%2C%22chartLimits%22%3A%5B5%2C10%2C25%2C50%2C100%5D%2C%22chartLimit%22%3Anull%2C%22chartX%22%3Anull%2C%22chartXPivot%22%3Anull%2C%22chartYSingle%22%3Anull%2C%22chartYMulti%22%3A%5B%5D%2C%22chartData%22%3A%5B%5D%2C%22chartMapType%22%3A%22marker%22%2C%22chartMapLabel%22%3Anull%2C%22chartMapHeat%22%3Anull%2C%22hideStacked%22%3Atrue%2C%22hasDataForChart%22%3Afalse%2C%22previousChartOptions%22%3A%7B%22chartLimit%22%3Anull%2C%22chartX%22%3Anull%2C%22chartXPivot%22%3Anull%2C%22chartYSingle%22%3Anull%2C%22chartMapType%22%3A%22marker%22%2C%22chartMapLabel%22%3Anull%2C%22chartMapHeat%22%3Anull%2C%22chartYMulti%22%3A%5B%5D%2C%22chartScope%22%3A%22world%22%2C%22chartTimelineType%22%3A%22bar%22%2C%22chartSorting%22%3A%22none%22%2C%22chartScatterGroup%22%3Anull%2C%22chartScatterSize%22%3Anull%7D%2C%22isResultSettingsVisible%22%3Afalse%2C%22settingsVisible%22%3Afalse%2C%22checkStatusTimeout%22%3Anull%2C%22topRisk%22%3Anull%2C%22suggestion%22%3A%22%22%2C%22hasSuggestion%22%3Anull%2C%22compatibilityCheckRunning%22%3Afalse%2C%22compatibilitySourcePlatform%22%3A%22impala%22%2C%22compatibilitySourcePlatforms%22%3A%5B%7B%22name%22%3A%22Teradata%22%2C%22value%22%3A%22teradata%22%7D%2C%7B%22name%22%3A%22Oracle%22%2C%22value%22%3A%22oracle%22%7D%2C%7B%22name%22%3A%22Netezza%22%2C%22value%22%3A%22netezza%22%7D%2C%7B%22name%22%3A%22Impala%22%2C%22value%22%3A%22impala%22%7D%2C%7B%22name%22%3A%22impala%22%2C%22value%22%3A%22impala%22%7D%2C%7B%22name%22%3A%22DB2%22%2C%22value%22%3A%22db2%22%7D%2C%7B%22name%22%3A%22Greenplum%22%2C%22value%22%3A%22greenplum%22%7D%2C%7B%22name%22%3A%22MySQL%22%2C%22value%22%3A%22mysql%22%7D%2C%7B%22name%22%3A%22PostgreSQL%22%2C%22value%22%3A%22postgresql%22%7D%2C%7B%22name%22%3A%22Informix%22%2C%22value%22%3A%22informix%22%7D%2C%7B%22name%22%3A%22SQL+Server%22%2C%22value%22%3A%22sqlserver%22%7D%2C%7B%22name%22%3A%22Sybase%22%2C%22value%22%3A%22sybase%22%7D%2C%7B%22name%22%3A%22Access%22%2C%22value%22%3A%22access%22%7D%2C%7B%22name%22%3A%22Firebird%22%2C%22value%22%3A%22firebird%22%7D%2C%7B%22name%22%3A%22ANSISQL%22%2C%22value%22%3A%22ansisql%22%7D%2C%7B%22name%22%3A%22Generic%22%2C%22value%22%3A%22generic%22%7D%5D%2C%22compatibilityTargetPlatform%22%3A%22impala%22%2C%22compatibilityTargetPlatforms%22%3A%5B%7B%22name%22%3A%22Impala%22%2C%22value%22%3A%22impala%22%7D%2C%7B%22name%22%3A%22impala%22%2C%22value%22%3A%22impala%22%7D%5D%2C%22showOptimizer%22%3Atrue%2C%22delayedStatement%22%3A%22show+tables%3B%22%2C%22wasBatchExecuted%22%3Afalse%2C%22isReady%22%3Atrue%2C%22lastExecuted%22%3A1528820101947%2C%22lastAceSelectionRowOffset%22%3A0%2C%22executingBlockingOperation%22%3Anull%2C%22showLongOperationWarning%22%3Afalse%2C%22formatEnabled%22%3Atrue%2C%22isFetchingData%22%3Afalse%2C%22isCanceling%22%3Afalse%2C%22aceAutoExpand%22%3Afalse%7D%5D%2C%22selectedSnippet%22%3A%22impala%22%2C%22creatingSessionLocks%22%3A%5B%5D%2C%22sessions%22%3A%5B%7B%22type%22%3A%22impala%22%2C%22properties%22%3A%5B%7B%22multiple%22%3Atrue%2C%22defaultValue%22%3A%5B%5D%2C%22value%22%3A%5B%5D%2C%22nice_name%22%3A%22Files%22%2C%22key%22%3A%22files%22%2C%22help_text%22%3A%22Add+one+or+more+files%2C+jars%2C+or+arcimpalas+to+the+list+of+resources.%22%2C%22type%22%3A%22hdfs-files%22%7D%2C%7B%22multiple%22%3Atrue%2C%22defaultValue%22%3A%5B%5D%2C%22value%22%3A%5B%5D%2C%22nice_name%22%3A%22Functions%22%2C%22key%22%3A%22functions%22%2C%22help_text%22%3A%22Add+one+or+more+registered+UDFs+(requires+function+name+and+fully-qualified+class+name).%22%2C%22type%22%3A%22functions%22%7D%2C%7B%22nice_name%22%3A%22Settings%22%2C%22multiple%22%3Atrue%2C%22key%22%3A%22settings%22%2C%22help_text%22%3A%22impala+and+Hadoop+configuration+properties.%22%2C%22defaultValue%22%3A%5B%5D%2C%22type%22%3A%22settings%22%2C%22options%22%3A%5B%22impala.map.aggr%22%2C%22impala.exec.compress.output%22%2C%22impala.exec.parallel%22%2C%22impala.execution.engine%22%2C%22mapreduce.job.queuename%22%5D%2C%22value%22%3A%5B%5D%7D%5D%2C%22reuse_session%22%3Atrue%2C%22id%22%3A6865%2C%22session_id%22%3A%22714fb09b96ba3368%3A4d02ec93d7ffbfb6%22%7D%5D%2C%22directoryUuid%22%3A%22%22%2C%22dependentsCoordinator%22%3A%5B%5D%2C%22historyFilter%22%3A%22%22%2C%22historyFilterVisible%22%3Afalse%2C%22loadingHistory%22%3Afalse%2C%22historyInitialHeight%22%3A1679%2C%22forceHistoryInitialHeight%22%3Atrue%2C%22historyCurrentPage%22%3A1%2C%22historyTotalPages%22%3A3%2C%22schedulerViewModel%22%3Anull%2C%22schedulerViewModelIsLoaded%22%3Afalse%2C%22isBatchable%22%3Atrue%2C%22isExecutingAll%22%3Afalse%2C%22executingAllIndex%22%3A0%2C%22retryModalConfirm%22%3Anull%2C%22retryModalCancel%22%3Anull%2C%22unloaded%22%3Afalse%2C%22updateHistoryFailed%22%3Afalse%2C%22viewSchedulerId%22%3A%22%22%2C%22loadingScheduler%22%3Afalse%7D"
                  },
                  {
                    "name": "snippet",
                    "value": "%7B%22id%22%3A%22dd5755a3-e8db-82d9-4f98-9f4fb5a99a06%22%2C%22type%22%3A%22impala%22%2C%22status%22%3A%22running%22%2C%22statementType%22%3A%22text%22%2C%22statement%22%3A%22show+tables%3B%22%2C%22aceCursorPosition%22%3A%7B%22column%22%3A33%2C%22row%22%3A0%7D%2C%22statementPath%22%3A%22%22%2C%22associatedDocumentUuid%22%3Anull%2C%22properties%22%3A%7B%22files%22%3A%5B%5D%2C%22functions%22%3A%5B%5D%2C%22arguments%22%3A%5B%5D%2C%22settings%22%3A%5B%5D%7D%2C%22result%22%3A%7B%22id%22%3A%2206840534-9434-33b5-5eca-2cd08432ceb3%22%2C%22type%22%3A%22table%22%2C%22handle%22%3A%7B%22has_more_statements%22%3Afalse%2C%22statement_id%22%3A0%2C%22statements_count%22%3A1%2C%22previous_statement_hash%22%3A%22acb6478fcf28c31b5e76d49de7d77bbe46fe5e4f9436c16c0ca8ed5f%22%7D%7D%2C%22database%22%3A%22default%22%2C%22compute%22%3A%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22default-romain%22%2C%22id%22%3A%22default-romain%22%2C%22name%22%3A%22default-romain%22%7D%2C%22wasBatchExecuted%22%3Afalse%7D"
                  }
                ]
              }
            }'''
    }

def create_directories(fs, directory_list=[]):
  # If needed, create the remote home, deployment and data directories
  directories = [REMOTE_DEPLOYMENT_DIR.get()] + directory_list

  for directory in directories:
    if not fs.do_as_user(fs.DEFAULT_USER, fs.exists, directory):
      remote_home_dir = Hdfs.join('/user', fs.DEFAULT_USER)
      if directory.startswith(remote_home_dir):
        # Home is 755
        fs.do_as_user(fs.DEFAULT_USER, fs.create_home_dir, remote_home_dir)
      # Shared by all the users
      fs.do_as_user(fs.DEFAULT_USER, fs.mkdir, directory, 01777)
      fs.do_as_user(fs.DEFAULT_USER, fs.chmod, directory, 01777) # To remove after https://issues.apache.org/jira/browse/HDFS-3491

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
# limitations under the License.import logging

import logging
import os

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.conf import DISABLE_HUE_3
from hadoop.fs.hadoopfs import Hdfs
from notebook.models import make_notebook

from indexer.conf import CONFIG_JARS_LIBS_PATH


LOG = logging.getLogger(__name__)


class EnvelopeIndexer(object):

  def __init__(self, username, fs=None, jt=None, solr_client=None):
    self.fs = fs
    self.jt = jt
    self.username = username


  def _upload_workspace(self, envelope):
    from oozie.models2 import Job

    hdfs_workspace_path = Job.get_workspace(self.username)
    hdfs_envelope_path = os.path.join(hdfs_workspace_path, "envelope.conf")

    # Create workspace on hdfs
    self.fs.do_as_user(self.username, self.fs.mkdir, hdfs_workspace_path)

    self.fs.do_as_user(self.username, self.fs.create, hdfs_envelope_path, data=envelope)

    return hdfs_workspace_path


  def run(self, request, collection_name, envelope, input_path, start_time=None, lib_path=None):
    workspace_path = self._upload_workspace(envelope)
    if lib_path is None:
      lib_path = CONFIG_JARS_LIBS_PATH.get()

    task = make_notebook(
      name=_('Indexing into %s') % collection_name,
      editor_type='notebook',
      #on_success_url=reverse('search:browse', kwargs={'name': collection_name}),
      #pub_sub_url='assist.collections.refresh',
      is_task=True,
      is_notebook=True,
      last_executed=start_time
    )

    if not DISABLE_HUE_3.config.default_value or True: # CDH5
      shell_command_name = "pipeline.sh"
      shell_command = """#!/bin/bash

export SPARK_DIST_CLASSPATH=`hadoop classpath`
export SPARK_DIST_CLASSPATH=/etc/hive/conf:`hadoop classpath`
export JAVA_HOME=/usr/java/jdk1.8.0_162

SPARK_KAFKA_VERSION=0.10 spark2-submit envelope.jar envelope.conf"""
      hdfs_shell_cmd_path = os.path.join(workspace_path, shell_command_name)
      self.fs.do_as_user(self.username, self.fs.create, hdfs_shell_cmd_path, data=shell_command)
      task.add_shell_snippet(
        shell_command=shell_command_name,
        files=[
            {u'value': u'%s/envelope.conf' % workspace_path},
            {u'value': hdfs_shell_cmd_path},
            {u'value': lib_path}
        ]
      )
    else:
      task.add_spark_snippet(
        clazz='com.cloudera.labs.envelope.EnvelopeMain',
        jars=Hdfs.basename(lib_path),
        arguments=[
            u'envelope.conf'
        ],
        files=[
            {u'path': u'%s/envelope.conf' % workspace_path, u'type': u'file'},
            {u'path': lib_path, u'type': u'file'},
        ]
      )

    return task.execute(request, batch=True)


  def generate_config(self, properties):
    if properties['inputFormat'] == 'stream':
      if properties['streamSelection'] == 'kafka':
        input = """type = kafka
                brokers = "%(brokers)s"
                topics = [%(topics)s]
                encoding = string
                translator {
                    type = %(kafkaFieldType)s
                    delimiter = "%(kafkaFieldDelimiter)s"
                    field.names = [%(kafkaFieldNames)s]
                    field.types = [%(kafkaFieldTypes)s]
                }
                %(window)s
        """ % properties
      elif properties['streamSelection'] == 'sfdc':
        input = """type = sfdc
            mode = fetch-all
            sobject = %(streamObject)s
            sfdc: {
              partner: {
                username = "%(streamUsername)s"
                password = "%(streamPassword)s"
                token = "%(streamToken)s"
                auth-endpoint = "%(streamEndpointUrl)s"
              }
            }
  """ % properties
      else:
        raise PopupException(_('Stream format of %(inputFormat)s not recognized: %(streamSelection)s') % properties)
    elif properties['inputFormat'] == 'file':
      input = """type = filesystem
        path = %(input_path)s
        format = %(format)s
      """ % properties
    else:
      raise PopupException(_('Input format not recognized: %(inputFormat)s') % properties)


    if properties['ouputFormat'] == 'file':
      output = """
        planner = {
          type = overwrite
        }
        output = {
          type = filesystem
          path = %(path)s
          format = %(format)s
          header = true
        }""" % properties
    elif properties['ouputFormat'] == 'table':
      if properties['inputFormat'] == 'stream' and properties['streamSelection'] == 'kafka':
        output = """
          deriver {
              type = sql
              query.literal = \"""
                  SELECT * FROM inputdata\"""
          }
          planner {
              type = upsert
          }
          output {
              type = kudu
              connection = "%(kudu_master)s"
              table.name = "%(output_table)s"
          }""" % properties
      else:
        output = """
          planner {
              type = append
          }
          output {
              type = hive
              table.name = "%(output_table)s"
          }""" % properties
    elif properties['ouputFormat'] == 'index':
      if properties['inputFormat'] == 'stream':
        if properties['topics'] == 'NavigatorAuditEvents':
          output = ''
      else:
        output = """
          planner {
              type = upstert
          }
          output {
              type = solr
              connection = "%(connection)s"
              collection.name = "%(collectionName)s"
          }""" % properties
    elif properties['ouputFormat'] == 'stream':
      output = """
        planner {
            type = append
        }
        output {
            type = kafka
            brokers = "%(brokers)s"
            topic = %(topics)s
            serializer.type = delimited
            serializer.field.delimiter = ","
        }""" % properties
    else:
      raise PopupException(_('Output format not recognized: %(ouputFormat)s') % properties)

    return """
application {
    name = %(app_name)s
    %(batch)s
    executors = 1
    executor.cores = 1
    executor.memory = 1G
}

steps {
    inputdata {
        input {
            %(input)s
        }
    }

    outputdata {
        dependencies = [inputdata]

        deriver {
          type = sql
          query.literal = \"\"\"SELECT * from inputdata\"\"\"
        }

        %(output)s
    }
}

""" % {
    'input': input,
    'output': output,
    'app_name': properties['app_name'],
    'batch': 'batch.milliseconds = 5000' if properties['inputFormat'] == 'stream' else ''
  }

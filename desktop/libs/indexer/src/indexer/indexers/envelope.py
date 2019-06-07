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
from hadoop.fs.hadoopfs import Hdfs
from notebook.models import make_notebook

from indexer.conf import CONFIG_JARS_LIBS_PATH, config_morphline_path
from libzookeeper.conf import zkensemble


LOG = logging.getLogger(__name__)


class EnvelopeIndexer(object):

  def __init__(self, username, fs=None, jt=None, solr_client=None):
    self.fs = fs
    self.jt = jt
    self.username = username


  def _upload_workspace(self, configs):
    from oozie.models2 import Job

    hdfs_workspace_path = Job.get_workspace(self.username)

    # Create workspace on hdfs
    self.fs.do_as_user(self.username, self.fs.mkdir, hdfs_workspace_path)

    for config_name, config_content in configs.iteritems():
      hdfs_config_path = os.path.join(hdfs_workspace_path, config_name)
      self.fs.do_as_user(self.username, self.fs.create, hdfs_config_path, data=config_content)

    return hdfs_workspace_path


  def run(self, request, collection_name, configs, input_path, start_time=None, lib_path=None):
    workspace_path = self._upload_workspace(configs)

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

    return task.execute(request, batch=True)


  def generate_config(self, properties):
    configs = {
    }

    if properties['inputFormat'] == 'stream':
      if properties['streamSelection'] == 'kafka':
        if properties['topics'] == 'NavigatorAuditEvents':
          morphline_config = open(os.path.join(config_morphline_path(), 'navigator_topic.morphline.conf')).read()
          configs['navigator_topic.morphline.conf'] = morphline_config.replace(
            '${SOLR_COLLECTION}', 'empty'
          ).replace(
            '${ZOOKEEPER_ENSEMBLE}', '%s/solr' % zkensemble()
          )
          input = """
              type = kafka
              brokers = "%(brokers)s"
              topics = [%(topics)s]
              //group.id = nav-envelope
              encoding = bytearray
              parameter.auto.offset.reset = earliest

              translator {
                type = morphline
                encoding.key = UTF8
                encoding.message = UTF8
                morphline.file = "navigator_topic.morphline.conf"
                morphline.id = "nav-json-input"
                field.names = [%(kafkaFieldNames)s]
                field.types = [%(kafkaFieldTypes)s]
              }
              %(window)s
          """ % properties
        else:
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
      else:
        raise PopupException(_('Stream format of %(inputFormat)s not recognized: %(streamSelection)s') % properties)
    elif properties['inputFormat'] == 'connector':
      # sfdc
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
    elif properties['inputFormat'] == 'file':
      input = """type = filesystem
        path = %(input_path)s
        format = %(format)s
      """ % properties
    else:
      raise PopupException(_('Input format not recognized: %(inputFormat)s') % properties)


    extra_step = ''
    properties['output_deriver'] = """
        deriver {
          type = sql
          query.literal = \"\"\"SELECT * from inputdata\"\"\"
        }"""

    if properties['inputFormat'] == 'stream' and properties['topics'] == 'NavigatorAuditEvents': # Kudu does not support upper case names
      properties['output_deriver'] = """
          deriver {
            type = sql
            query.literal = \"\"\"
                SELECT concat_ws('-', time,  service, user) as id,
                -- timeDate todo
                additionalInfo as additionalinfo, allowed,
                collectionName as collectionname,
                databaseName as databasename, db,
                DELEGATION_TOKEN_ID as delegation_token_id, dst,
                entityId as entityid, time, family, impersonator, ip, name,
                objectType as objecttype,
                objType as objtype,
                objUsageType as objusagetype, op,
                operationParams as operationparams,
                operationText as operationtext,
                opText as optext, path, perms, privilege, qualifier,
                QUERY_ID as query_id,
                resourcePath as resourcepath, service,
                SESSION_ID as session_id,
                solrVersion as solrversion, src, status,
                subOperation as suboperation,
                tableName as tablename,
                `table` as `table`, type, url, user
                FROM inputdata
            \"\"\"
          }"""


    if properties['ouputFormat'] == 'file':
      output = """
        %(output_deriver)s

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
      if properties['inputFormat'] == 'stream' and properties['streamSelection'] == 'kafka': # TODO: look at table output type instead and merge
        output = """
          %(output_deriver)s

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
         %(output_deriver)s

          planner {
              type = append
          }
          output {
              type = hive
              table.name = "%(output_table)s"
          }""" % properties
    elif properties['ouputFormat'] == 'index':
      if True: # Workaround until envelope Solr output is official
        morphline_config = open(os.path.join(config_morphline_path(), 'navigator_topic.morphline.conf')).read()
        configs['navigator_topic.morphline.conf'] = morphline_config.replace(
          '${SOLR_COLLECTION}', properties['collectionName']
        ).replace(
          '${ZOOKEEPER_ENSEMBLE}', '%s/solr' % zkensemble()
        )
        output = """
            // Load events to a Solr index
            // TODO: Move this to a SolrOutput step, when this is available
            deriver {
              type = morphline
              step.name = kafkaInput
              morphline.file = ${vars.morphline.file}
              morphline.id = ${vars.morphline.solr.indexer}
              field.names = ${vars.json.field.names}
              field.types = ${vars.json.field.types}
            }
          """ % properties
        extra_step = """
          solrOutput {
            dependencies = [outputdata]

            deriver {
              type = sql
              query.literal = \"\"\"
                SELECT *
                FROM outputdata LIMIT 0
                \"\"\"
            }

            planner = {
              type = append
            }

            output = {
              type = log
              path = ${vars.hdfs.basedir}
              format = csv
            }
          }""" % properties
      else:
        output = """
          %(output_deriver)s

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
        %(output_deriver)s

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

    configs['envelope.conf'] = """
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

        %(output)s
    }

    %(extra_step)s
}

""" % {
    'input': input,
    'output': output,
    'extra_step': extra_step,
    'app_name': properties['app_name'],
    'batch': 'batch.milliseconds = 5000' if properties['inputFormat'] == 'stream' else ''
  }

    return configs

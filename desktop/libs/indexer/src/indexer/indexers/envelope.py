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

from notebook.models import make_notebook


LOG = logging.getLogger(__name__)


class EnvelopeIndexer(object):

  def __init__(self, username, fs=None, jt=None, solr_client=None):
    self.fs = fs
    self.jt = jt
    self.username = username


  def _upload_workspace(self, morphline):
    from oozie.models2 import Job

    hdfs_workspace_path = Job.get_workspace(self.username)
    hdfs_morphline_path = os.path.join(hdfs_workspace_path, "envelope.conf")

    # Create workspace on hdfs
    self.fs.do_as_user(self.username, self.fs.mkdir, hdfs_workspace_path)

    self.fs.do_as_user(self.username, self.fs.create, hdfs_morphline_path, data=morphline)

    return hdfs_workspace_path


  def run(self, request, collection_name, morphline, input_path, start_time=None, lib_path=None):
    workspace_path = self._upload_workspace(morphline)

    task = make_notebook(
      name=_('Indexing into %s') % collection_name,
      editor_type='notebook',
      #on_success_url=reverse('search:browse', kwargs={'name': collection_name}),
      #pub_sub_url='assist.collections.refresh',
      is_task=True,
      is_notebook=True,
      last_executed=start_time
    )

    task.add_spark_snippet(
      clazz=None,
      jars=lib_path,
      arguments=[
          u'envelope.conf'
      ],
      files=[
          {u'path': u'%s/envelope.conf' % workspace_path, u'type': u'file'}
      ]
    )

    return task.execute(request, batch=True)


  def generate_config(self):
    properties = {
      "brokers": "self-service-analytics-1.gce.cloudera.com:9092,self-service-analytics-2.gce.cloudera.com:9092,self-service-analytics-3.gce.cloudera.com:9092",
      "kudu_master": "self-service-analytics-1.gce.cloudera.com:7051",
      "output_table": "impala::default.traffic_conditions"
    }

    return """
application {
    name = Traffic analysis
    batch.milliseconds = 5000
    executors = 1
    executor.cores = 1
    executor.memory = 1G
}

steps {
    traffic {
        input {
            type = kafka
            brokers = "%(brokers)s"
            topics = traffic
            encoding = string
            translator {
                type = delimited
                delimiter = ","
                field.names = [measurement_time,number_of_vehicles]
                field.types = [long,int]
            }
            window {
                enabled = true
                milliseconds = 60000
            }
        }
    }

    trafficwindow {
        dependencies = [traffic]
        deriver {
            type = sql
            query.literal = \"""
                SELECT UNIX_TIMESTAMP() * 1000 as_of_time, ROUND(AVG(number_of_vehicles), 2) avg_num_veh,
                MIN(number_of_vehicles) min_num_veh, MAX(number_of_vehicles) max_num_veh,
                MIN(measurement_time) first_meas_time, MAX(measurement_time) last_meas_time FROM traffic\"""
        }
        planner {
            type = upsert
        }
        output {
            type = kudu
            connection = "%(kudu_master)s"
            table.name = "%(output_table)s"
        }
    }
}

""" % properties


"""application {
  name = Filesystem Example
  executors = 1
}
steps {
  fsInput {
    input {
      type = filesystem
      // Be sure to load this file into HDFS first!
      path = example-input.json
      format = json
    }
  }
  fsProcess {
    dependencies = [fsInput]
    deriver {
      type = sql
      query.literal = "SELECT foo FROM fsInput"
    }
    planner = {
      type = overwrite
    }
    output = {
      type = filesystem
      // The output directory
      path = example-output
      format = parquet
    }
  }
}
"""
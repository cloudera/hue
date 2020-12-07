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

from builtins import object
import logging
import os

from django.urls import reverse
from django.utils.translation import ugettext as _

from libzookeeper.conf import zkensemble
from indexer.conf import config_morphline_path
from metadata.manager_client import ManagerApi
from useradmin.models import User

from desktop.lib.exceptions_renderable import PopupException


LOG = logging.getLogger(__name__)


class FlumeIndexer(object):

  def __init__(self, user):
    self.user = user


  def start(self, destination_name, file_format, destination):
    responses = {'status': 0}

    api = ManagerApi(self.user)

    for config_name, config_value in self.generate_config(file_format, destination):
      responses[config_name] = api.update_flume_config(cluster_name=None, config_name=config_name, config_value=config_value)

    responses['refresh_flume'] = api.refresh_flume(cluster_name=None, restart=True)

    if destination['ouputFormat'] == 'index':
      responses['pubSubUrl'] = 'assist.collections.refresh'
      responses['on_success_url'] = reverse('search:browse', kwargs={'name': destination_name})

    return responses


  def generate_config(self, source, destination):
    configs = []

    if source['channelSourceType'] == 'directory':
      agent_source = '''
  tier1.sources.source1.type = exec
  tier1.sources.source1.command = tail -F %(directory)s
  tier1.sources.source1.channels = channel1
      ''' % {
       'directory': source['channelSourcePath']
    }
    elif source['channelSourceType'] == 'kafka':
      agent_source = '''
  tier1.sources.source1.type = org.apache.flume.source.kafka.KafkaSource
  tier1.sources.source1.channels = channel1
  tier1.sources.source1.batchSize = 5000
  tier1.sources.source1.batchDurationMillis = 2000
  tier1.sources.source1.kafka.bootstrap.servers = localhost:9092
  tier1.sources.source1.kafka.topics = test1, test2
  tier1.sources.source1.kafka.consumer.group.id = custom.g.id
      ''' % {
       'directory': source['channelSourcePath']
    }
    else:
      raise PopupException(_('Input format not recognized: %(channelSourceType)s') % source)

    if destination['ouputFormat'] == 'file':
      agent_sink = '''
  a1.channels = c1
  a1.sinks = k1
  a1.sinks.k1.type = hdfs
  a1.sinks.k1.channel = c1
  a1.sinks.k1.hdfs.path = /flume/events/%y-%m-%d/%H%M/%S
  a1.sinks.k1.hdfs.filePrefix = events-
  a1.sinks.k1.hdfs.round = true
  a1.sinks.k1.hdfs.roundValue = 10
  a1.sinks.k1.hdfs.roundUnit = minute'''
    elif destination['ouputFormat'] == 'table':
      agent_sink = '''
  a1.channels = c1
  a1.channels.c1.type = memory
  a1.sinks = k1
  a1.sinks.k1.type = hive
  a1.sinks.k1.channel = c1
  a1.sinks.k1.hive.metastore = thrift://127.0.0.1:9083
  a1.sinks.k1.hive.database = logsdb
  a1.sinks.k1.hive.table = weblogs
  a1.sinks.k1.hive.partition = asia,%{country},%y-%m-%d-%H-%M
  a1.sinks.k1.useLocalTimeStamp = false
  a1.sinks.k1.round = true
  a1.sinks.k1.roundValue = 10
  a1.sinks.k1.roundUnit = minute
  a1.sinks.k1.serializer = DELIMITED
  a1.sinks.k1.serializer.delimiter = "\t"
  a1.sinks.k1.serializer.serdeSeparator = '\t'
  a1.sinks.k1.serializer.fieldnames =id,,msg'''
    elif destination['ouputFormat'] == 'kafka':
      manager = ManagerApi()
      agent_sink = '''
      tier1.sinks.sink1.type = org.apache.flume.sink.kafka.KafkaSink
tier1.sinks.sink1.topic = hueAccessLogs
tier1.sinks.sink1.brokerList = %(brokers)s
tier1.sinks.sink1.channel = channel1
tier1.sinks.sink1.batchSize = 20''' % {
      'brokers': manager.get_kafka_brokers()
    }

    elif destination['ouputFormat'] == 'index':
      # Morphline file
      configs.append(self.generate_morphline_config(destination))
      # Flume config
      agent_sink = '''
  tier1.sinks.sink1.type          = org.apache.flume.sink.solr.morphline.MorphlineSolrSink
  tier1.sinks.sink1.morphlineFile = morphlines.conf
  tier1.sinks.sink1.morphlineId = hue_accesslogs_no_geo
  tier1.sinks.sink1.channel       = channel1'''
    else:
      raise PopupException(_('Output format not recognized: %(ouputFormat)s') % destination)

    # TODO: use agent id: input + output and do not overide all the configs
    # TODO: use Kafka channel if possible
    flume_config = '''tier1.sources = source1
  tier1.channels = channel1
  tier1.sinks = sink1

  %(sources)s

  tier1.channels.channel1.type = memory
  tier1.channels.channel1.capacity = 10000
  tier1.channels.channel1.transactionCapacity = 1000

  %(sinks)s''' % {
    'sources': agent_source,
    'sinks': agent_sink,
  }

    configs.append(('agent_config_file', flume_config))

    return configs


  def generate_morphline_config(self, destination):
    # TODO manage generic config, cf. MorphlineIndexer
    morphline_config = open(os.path.join(config_morphline_path(), 'hue_accesslogs_no_geo.morphline.conf')).read()
    morphline_config = morphline_config.replace(
      '${SOLR_COLLECTION}', destination['name']
    ).replace(
      '${ZOOKEEPER_ENSEMBLE}', '%s/solr' % zkensemble()
    )
    return ('agent_morphlines_conf_file', morphline_config)

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

from django.contrib.auth.models import User

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_true

from indexer.indexers.flume import FlumeIndexer


def test_generate_from_directory_to_solr_index():
  raise SkipTest

  source = {
    'channelSourceType': 'directory',
  }
  destination = {
    'ouputFormat': 'index',
  }

  configs = FlumeIndexer(user=None).generate_config(source=source, destination=destination)

  assert_equal(
    '''SOLR_LOCATOR : {
    # Name of solr collection
    collection : log_analytics_demo
    # ZooKeeper ensemble
    zkHost : "spark2-envelope515-1.gce.cloudera.com:2181/solr"
}


morphlines : [
{
    id : hue_accesslogs_no_geo

    importCommands : ["org.kitesdk.**", "org.apache.solr.**"]
    commands : [
    {
        ## Read the email stream and break it up into individual messages.
        ## The beginning of a message is marked by regex clause below
        ## The reason we use this command is that one event can have multiple
        ## messages
        readCSV {

        ## Hue HTTPD load balancer
        ## 172.18.18.3 - - [27/Aug/2018:05:47:12 -0700] "GET /static/desktop/js/jquery.rowselector.a04240f7cc48.js HTTP/1.1" 200 2321

      separator:  " "
            columns:  [client_ip,C1,C2,time,dummy1,request,code,bytes]
      ignoreFirstLine : false
            quoteChar : "\""
            commentPrefix : ""
            trim : true
            charset : UTF-8
        }
    }
    {
  split {
    inputField : request
    outputFields : [method, url, protocol]
    separator : " "
    isRegex : false
    #separator : """\s*,\s*"""
    #  #isRegex : true
    addEmptyStrings : false
    trim : true
          }
    }
     {
  split {
    inputField : url
    outputFields : ["", app, subapp]
    separator : "\/"
    isRegex : false
    #separator : """\s*,\s*"""
    #  #isRegex : true
    addEmptyStrings : false
    trim : true
          }
    }
    {
  userAgent {
    inputField : user_agent
    outputFields : {
      user_agent_family : "@{ua_family}"
      user_agent_major  : "@{ua_major}"
      device_family     : "@{device_family}"
      os_family         : "@{os_family}"
      os_major    : "@{os_major}"
    }
  }
    }

      #{logInfo { format : "BODY : {}", args : ["@{}"] } }
    # add Unique ID, in case our message_id field from above is not present
    {
        generateUUID {
            field:id
        }
    }

    # convert the timestamp field to "yyyy-MM-dd'T'HH:mm:ss.SSSZ" format
    {
       #  21/Nov/2014:22:08:27
        convertTimestamp {
            field : time
            inputFormats : ["[dd/MMM/yyyy:HH:mm:ss", "EEE, d MMM yyyy HH:mm:ss Z", "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", "yyyy-MM-dd'T'HH:mm:ss", "yyyy-MM-dd"]
            #inputTimezone : America/Los_Angeles
            inputTimezone : UTC
            outputFormat : "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"
            outputTimezone : UTC
        }
    }

    # Consume the output record of the previous command and pipe another
    # record downstream.
    #
    # This command sanitizes record fields that are unknown to Solr schema.xml
    # by deleting them. Recall that Solr throws an exception on any attempt to
    # load a document that contains a field that isn't specified in schema.xml
    {
        sanitizeUnknownSolrFields {
            # Location from which to fetch Solr schema
            solrLocator : ${SOLR_LOCATOR}
        }
    }

    # load the record into a SolrServer or MapReduce SolrOutputFormat.
    {
        loadSolr {
            solrLocator : ${SOLR_LOCATOR}
        }
    }
    ]
}
]
'''.strip()
    ,
    configs[0][1].strip() # 'agent_morphlines_conf_file'
  )
  
  assert_equal(
    ('agent_config_file', 'tier1.sources = source1\n  tier1.channels = channel1\n  tier1.sinks = sink1\n\n\n  tier1.channels.channel1.type = memory\n  tier1.channels.channel1.capacity = 10000\n  tier1.channels.channel1.transactionCapacity = 1000\n\n  \n  tier1.sinks.sink1.type          = org.apache.flume.sink.solr.morphline.MorphlineSolrSink\n  tier1.sinks.sink1.morphlineFile = morphlines.conf\n  tier1.sinks.sink1.morphlineId = hue_accesslogs_no_geo\n  tier1.sinks.sink1.channel       = channel1')
    ,
    configs['agent_config_file']
  )

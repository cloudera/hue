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
import sys
sys.path.append("../if/gen-py")
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

host = "localhost"
port = 9290

from hadoop.api import Jobtracker
from hadoop.api.ttypes import  *

#print dir(ThriftTaskPhase)
#exit()

socket = TSocket.TSocket(host,port)
transport = TTransport.TBufferedTransport(socket)
protocol = TBinaryProtocol.TBinaryProtocol(transport)

client = Jobtracker.Client(protocol)
transport.open()

#print client.trackerName(None,)
#print client.getClusterStatus(None,)
#print dir(client)
#print client.getQueues(None,)
jobs =  client.getCompletedJobs(None,)
print jobs 
if jobs and len(jobs) > 0:
    counters =  client.getJobCounters(None, jobs[0].job_id)

    for c in counters:
        print "--------------------------------------------"
        print "CounterGroup:: ", c.displayName
        for name in c.counters:
            print "Counter '%s':: %s" % (name,c.counters[name].value)        

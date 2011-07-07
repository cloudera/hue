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
A file to store all the constants in one place. Most constants
are the members of JSON objects, which are stored here for
easy reference.
"""

SHELL_ID = "shellId"
NOT_LOGGED_IN = "notLoggedIn"
SHELL_KILLED = "shellKilled"
SUCCESS = "success"


# Parameter/JSON object member names
ALIVE = "alive"
EXITED = "exited"
OUTPUT = "output"
COMMAND = "lineToSend"
COMMANDS = "commands"
KEY_NAME = "keyName"
NICE_NAME = "niceName"
OFFSET = "offset"
NEXT_OFFSET = "nextOffset"
NO_SHELL_EXISTS = "noShellExists"
BUFFER_EXCEEDED = "bufferExceeded"
PERIODIC_RESPONSE = "periodicResponse"
SHELL_CREATE_FAILED = "shellCreateFailed"
MORE_OUTPUT_AVAILABLE = "moreOutputAvailable"
NUM_PAIRS = "numPairs"
CANCELLED = "cancelled"
NOT_RUNNING_SPAWNING = "notRunningSpawning"
IS_TAB = "isTab"
NO_SUCH_USER = "noSuchUser"
SHELL_NOT_ALLOWED = "shellNotAllowed"
HOME = "HOME"
HADOOP_HOME = "HADOOP_HOME"
HADOOP_TOKEN_FILE_LOCATION = 'HADOOP_TOKEN_FILE_LOCATION'
EXISTS = "exists"

# HTTP Headers used
HUE_INSTANCE_ID = "HTTP_HUE_INSTANCE_ID"

BROWSER_REQUEST_TIMEOUT = 55    # seconds

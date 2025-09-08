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

from __future__ import absolute_import

# Multipart upload settings
DEFAULT_CHUNK_SIZE = 1024 * 1024 * 8  # 8MiB
MULTIPART_THRESHOLD = DEFAULT_CHUNK_SIZE  # Start multipart upload if file size > threshold
MAX_POOL_CONNECTIONS = 10
MAX_RETRIES = 3

# Timeouts (in seconds)
CONNECT_TIMEOUT = 120
READ_TIMEOUT = 120

# S3 specific constants
S3_DELIMITER = "/"
DEFAULT_REGION = "us-east-1"

# Error retry settings
RETRY_EXCEPTIONS = ("RequestTimeout", "ConnectionError", "HTTPClientError")

# Client config defaults
CLIENT_CONFIG = {
  "max_pool_connections": MAX_POOL_CONNECTIONS,
  "connect_timeout": CONNECT_TIMEOUT,
  "read_timeout": READ_TIMEOUT,
  "retries": {
    "max_attempts": MAX_RETRIES,
    "mode": "standard",  # standard/adaptive
  },
}

# Transfer config defaults
TRANSFER_CONFIG = {
  "multipart_threshold": MULTIPART_THRESHOLD,
  "multipart_chunksize": DEFAULT_CHUNK_SIZE,
  "max_concurrency": MAX_POOL_CONNECTIONS,
  "use_threads": True,
}

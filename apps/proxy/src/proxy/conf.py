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
"""
Configuration options for the reverse proxy application.
"""
from desktop.lib.conf import Config, list_of_compiled_res
    
WHITELIST = Config(
  key="whitelist",
  default="(localhost|127\.0\.0\.1):(50030|50070|50060|50075)",
  help="Comma-separated list of regular expressions, which match 'host:port' of requested proxy target.",
  type=list_of_compiled_res(skip_empty=True))

BLACKLIST = Config(
  key="blacklist",
  default=(),
  help="Comma-separated list of regular expressions, which match any prefix of 'host:port/path' of requested proxy target. This does not support matching GET parameters.",
  type=list_of_compiled_res(skip_empty=True))

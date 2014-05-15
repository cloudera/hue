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


from desktop.lib.conf import Config, validate_thrift_transport

HBASE_CLUSTERS = Config(
  key="hbase_clusters",
  default="(Cluster|localhost:9090)",
  help="Comma-separated list of HBase Thrift servers for clusters in the format of '(name|host:port)'.",
  type=str)

TRUNCATE_LIMIT = Config(
  key="truncate_limit",
  default="500",
  help="Hard limit of rows or columns per row fetched before truncating.",
  type=int)

THRIFT_TRANSPORT = Config(
  key="thrift_transport",
  default="buffered",
  help="'buffered' is the default of the HBase Thrift Server. " +
       "'framed' can be used to chunk up responses, " +
       "which is useful when used in conjunction with the nonblocking server in Thrift.",
  type=str
)


def config_validator(user):
  res = []

  res.extend(validate_thrift_transport(THRIFT_TRANSPORT))

  return res

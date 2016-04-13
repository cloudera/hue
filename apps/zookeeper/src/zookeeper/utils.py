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

from django.http import Http404

from zookeeper.conf import CLUSTERS


def get_cluster_or_404(id):
  try:
    name = id
    cluster = CLUSTERS.get()[name]
  except (TypeError, ValueError):
    raise Http404()

  cluster = {
    'id': id,
    'nice_name': id,
    'host_ports': cluster.HOST_PORTS.get(),
    'rest_url': cluster.REST_URL.get(),
  }

  return cluster

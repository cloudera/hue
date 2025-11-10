// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

export const metricLabelKeys: { [key: string]: string } = {
  'queries.number': 'Metrics: Number of Queries',
  'requests.active': 'Metrics: Active Requests',
  'requests.exceptions': 'Metrics: Request Exceptions',
  'requests.response-time': 'Metrics: Request Response Time',
  'threads.daemon': 'Metrics: Daemon Threads',
  'threads.total': 'Metrics: Total Threads',
  users: 'Metrics: Users',
  'users.active': 'Metrics: Active Users',
  'users.active.total': 'Metrics: Total Active Users'
};

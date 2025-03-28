// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

export const SCHEDULE_NEW_TASK_URL = '/desktop/api2/taskserver/task/submit';
export const KILL_TASK_URL = '/desktop/api2/taskserver/task/kill';
export const GET_TASKS_URL = '/desktop/api2/taskserver/tasks';
export const GET_TASK_LOG_URL = '/desktop/api2/taskserver/task/logs';

export const scheduleTasksCategory = [
  {
    value: 'document_cleanup',
    label: 'Document Cleanup',
    children: [{ value: 'keep_days', label: 'Keep days', type: 'number' }]
  },
  {
    value: 'tmp_clean_up',
    label: 'Tmp Cleanup',
    children: [
      { value: 'cleanup_threshold', label: 'Cleanup threshold', type: 'number', max: 100 },
      { value: 'disk_check_interval', label: 'Disk check interval', type: 'number', max: 100 }
    ]
  }
];

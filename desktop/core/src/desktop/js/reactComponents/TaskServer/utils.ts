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

import { TaskServerResponse, TaskStatus } from './types';

export const statusTagColor = (status: TaskServerResponse['status']): string =>
  ({
    [TaskStatus.Running]: 'processing',
    [TaskStatus.Success]: 'success',
    [TaskStatus.Failure]: 'error'
  })[status] ?? '';

export const getFilteredTasks = (
  statusFilter: Record<string, boolean>,
  searchTerm: string,
  tasks?: TaskServerResponse[]
): TaskServerResponse[] => {
  if (!tasks) {
    return [];
  }
  return tasks
    .filter(task => {
      const taskNameMatch = task.result?.taskName?.toLowerCase().includes(searchTerm);
      const userIdMatch = task.result?.username?.toLowerCase().includes(searchTerm);
      const taskIdMatch = task.taskId?.toLowerCase().includes(searchTerm);
      const statusMatch =
        statusFilter.all ||
        (statusFilter.success && task.status === TaskStatus.Success) ||
        (statusFilter.failure && task.status === TaskStatus.Failure) ||
        (statusFilter.running && task.status === TaskStatus.Running);

      return (taskNameMatch || userIdMatch || taskIdMatch) && statusMatch;
    })
    .map(task => ({
      ...task,
      children: task.children?.length ? task.children : undefined
    }));
};

export const sortTasksByDate = (tasks?: TaskServerResponse[]): TaskServerResponse[] => {
  if (!tasks) {
    return [];
  }
  return tasks?.sort((a, b) => {
    const dateA = new Date(a.dateDone).getTime();
    const dateB = new Date(b.dateDone).getTime();
    if (dateA === dateB || isNaN(dateA) || isNaN(dateB)) {
      return 0;
    }
    return dateB - dateA;
  });
};

export const getUpdatedFilters = (
  status: string,
  prevStatusFilter: Record<string, boolean>
): Record<string, boolean> => {
  const isAll = status === 'all';
  const newStatusFilter = {
    ...prevStatusFilter,
    [status]: isAll ? true : !prevStatusFilter[status]
  };

  if (isAll) {
    // If 'all' is selected, set everything else to false
    newStatusFilter.success = false;
    newStatusFilter.failure = false;
    newStatusFilter.running = false;
  } else {
    // If any specific status is toggled, set 'all' to false
    newStatusFilter.all = false;
  }

  // If no individual statuses are selected, default to 'all'
  if (!newStatusFilter.success && !newStatusFilter.failure && !newStatusFilter.running) {
    newStatusFilter.all = true;
  }

  return newStatusFilter;
};

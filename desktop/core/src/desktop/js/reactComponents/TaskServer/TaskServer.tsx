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

import React, { useState, useMemo } from 'react';
import { i18nReact } from '../../utils/i18nReact.ts';
import { AxiosError } from 'axios';
import { extractErrorMessage } from '../../api/utils.ts';
import { calculateDuration, formatTimestamp } from '../../utils/dateTimeUtils.ts';
import huePubSub from '../../utils/huePubSub.ts';
import { Input, Checkbox } from 'antd';
import { Tag } from 'antd';
import { PrimaryButton, DangerButton } from 'cuix/dist/components/Button';
import PaginatedTable from '../PaginatedTable/PaginatedTable';
import useLoadData from '../../utils/hooks/useLoadData/useLoadData.ts';
import useSaveData from '../../utils/hooks/useSaveData/useSaveData.ts';
import { KillTaskResponse, TaskServerResponse, TaskServerResult } from './types.ts';
import { statusTagColor, getFilteredTasks, sortTasksByDate, getUpdatedFilters } from './utils.ts';
import { GET_TASKS_URL, KILL_TASK_URL } from './constants.ts';
import ScheduleTaskModal from './ScheduleTaskModal/ScheduleTaskModal.tsx';
import TaskLogsModal from './TaskLogsModal/TaskLogsModal.tsx';
import { useWindowSize } from '../../utils/hooks/useWindowSize/useWindowSize';

import './TaskServer.scss';

export const TaskServer: React.FC = () => {
  const [selectedTaskId, setSelectedTaskId] = useState<TaskServerResponse['taskId'] | null>(null);
  const [showSchedulePopup, showScheduleTaskPopup] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedTasks, setSelectedTasks] = useState<TaskServerResponse[]>([]);
  const [statusFilter, setStatusFilter] = useState<Record<string, boolean>>({
    success: false,
    failure: false,
    running: false,
    all: true
  });

  const { t } = i18nReact.useTranslation();

  const { save } = useSaveData(undefined);

  const columns = [
    {
      title: t('Task ID'),
      dataIndex: 'taskId',
      key: 'taskId',
      width: '30%',
      render: (text: TaskServerResponse['taskId'], record: TaskServerResponse) => (
        <a onClick={() => setSelectedTaskId(record.taskId)}>{text}</a>
      )
    },
    {
      title: t('User'),
      dataIndex: ['result', 'username'],
      key: 'user',
      width: '10%'
    },
    {
      title: t('Progress'),
      dataIndex: ['result', 'progress'],
      key: 'progress',
      width: '10%'
    },
    {
      title: t('Task Name'),
      dataIndex: ['result', 'taskName'],
      key: 'taskName',
      width: '10%'
    },
    {
      title: t('Parameters'),
      dataIndex: 'parameters',
      key: 'parameters',
      width: '10%',
      render: (_, record: TaskServerResponse) => {
        if (record.result?.taskName) {
          const paramterText = {
            fileupload: `{file name: ${record.result?.qqfilename}}`,
            document_cleanup: `{keep days: ${record.result?.parameters}}`,
            tmp_cleanup: `{cleanup threshold: ${record.result?.parameters}}`,
            cleanup_stale_uploads: `{cleanup timedelta: ${record.result?.parameters}}`
          }[record.result?.taskName];
          if (paramterText) {
            return <span>{paramterText}</span>;
          }
        }
      }
    },
    {
      title: t('Status'),
      dataIndex: 'status',
      key: 'status',
      width: '10%',
      render: (status: TaskServerResponse['status']) => (
        <Tag color={statusTagColor(status)}>{status.toUpperCase()}</Tag>
      )
    },
    {
      title: t('Started'),
      dataIndex: ['result', 'taskStart'],
      key: 'started',
      width: '10%',
      render: (text: TaskServerResult['taskStart']) => formatTimestamp(text)
    },
    {
      title: t('Duration'),
      key: 'duration',
      width: '10%',
      render: (_, record: TaskServerResponse) => {
        if (record.result?.taskStart && record.result?.taskEnd) {
          return calculateDuration(record.result?.taskStart, record.result?.taskEnd);
        }
      }
    }
  ];

  const { data: tasks } = useLoadData<TaskServerResponse[]>(GET_TASKS_URL, {
    pollInterval: 5000,
    onError: error => {
      huePubSub.publish('hue.global.error', { message: `Error fetching tasks: ${error}` });
    },
    onSuccess: data => {
      if (!Array.isArray(data)) {
        huePubSub.publish('hue.global.error', {
          message: `Expected an array of tasks, but received: ${data}`
        });
      }
    }
  });

  const sortedTasks = useMemo(() => sortTasksByDate(tasks), [tasks]);
  const filteredTasks = useMemo(
    () => getFilteredTasks(statusFilter, searchTerm, sortedTasks),
    [statusFilter, searchTerm, sortedTasks]
  );

  const onSearchChange = e => {
    setSearchTerm(e.target.value.toLowerCase());
  };

  const onStatusFilterChange = (status: string) => () => {
    const updatedFilters = getUpdatedFilters(status, statusFilter);
    setStatusFilter(updatedFilters);
  };

  const handleKillTask = (taskId: TaskServerResponse['taskId']) => {
    save(null, {
      url: `${KILL_TASK_URL}/${taskId}`,
      onSuccess: response => {
        const { status, message } = response as KillTaskResponse;
        if (status === 'success') {
          huePubSub.publish('hue.global.error', { message: `Task: ${taskId} has been killed.` });
        } else if (status === 'info') {
          huePubSub.publish('hue.global.info', {
            message: `Task: ${taskId} has already been completed or revoked.`
          });
        } else {
          huePubSub.publish('hue.global.error', {
            message: `Task: ${taskId} could not be killed. ${message}`
          });
        }
      },
      onError: error => {
        const errorMessage = extractErrorMessage(error as AxiosError);
        huePubSub.publish('hue.global.error', {
          message: `Task not killed - Error: ${errorMessage}`
        });
      }
    });
  };

  const onSchedulePopup = () => showScheduleTaskPopup(true);

  const onKillTask = () => {
    selectedTasks.forEach(task => {
      handleKillTask(task.taskId);
    });
    setSelectedTasks([]);
  };

  const [ref, rect] = useWindowSize();
  const tableBodyHeight = Math.max(rect.height - 40, 100);

  return (
    <div className="hue-task-server">
      <div className="hue-task-server__actions">
        <PrimaryButton data-event="" onClick={onSchedulePopup}>
          {t('Schedule Task')}
        </PrimaryButton>
        <DangerButton data-event="" onClick={onKillTask}>
          {t('Kill Task')}
        </DangerButton>
        <Input
          type="text"
          placeholder={t('Search by task name, user ID, or task ID...')}
          onChange={onSearchChange}
          style={{ flexGrow: 1 }}
        />
        <Checkbox checked={statusFilter.success} onChange={onStatusFilterChange('success')} />
        <span className="success-text">{t('Succeeded')}</span>
        <Checkbox checked={statusFilter.running} onChange={onStatusFilterChange('running')} />
        <span className="running-text">{t('Running')}</span>
        <Checkbox checked={statusFilter.failure} onChange={onStatusFilterChange('failure')} />
        <span className="failed-text">{t('Failed')}</span>
        <Checkbox checked={statusFilter.all} onChange={onStatusFilterChange('all')} />
        {t('All')}
      </div>
      <div className="hue-task-server__table" ref={ref}>
        <PaginatedTable<TaskServerResponse>
          onRowSelect={setSelectedTasks}
          columns={columns}
          data={filteredTasks}
          rowKey="taskId"
          scroll={{ y: tableBodyHeight }}
        />
      </div>
      {showSchedulePopup && <ScheduleTaskModal onClose={() => showScheduleTaskPopup(false)} />}
      {!!selectedTaskId && (
        <TaskLogsModal taskId={selectedTaskId} onClose={() => setSelectedTaskId(null)} />
      )}
    </div>
  );
};

export default TaskServer;

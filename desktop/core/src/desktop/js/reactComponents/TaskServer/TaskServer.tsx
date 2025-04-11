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
import { PrimaryButton, DangerButton, LinkButton } from 'cuix/dist/components/Button';
import PaginatedTable from '../PaginatedTable/PaginatedTable';
import useLoadData from '../../utils/hooks/useLoadData/useLoadData.ts';
import useSaveData from '../../utils/hooks/useSaveData/useSaveData.ts';
import { KillTaskResponse, TaskServerResponse, TaskServerResult } from './types.ts';
import { statusTagColor, getFilteredTasks, sortTasksByDate, getUpdatedFilters } from './utils.ts';
import { GET_TASKS_URL, KILL_TASK_URL } from './constants.ts';
import ScheduleTaskModal from './ScheduleTaskModal/ScheduleTaskModal.tsx';
import TaskLogsModal from './TaskLogsModal/TaskLogsModal.tsx';
import LoadingErrorWrapper from '../LoadingErrorWrapper/LoadingErrorWrapper.tsx';

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

  const { save } = useSaveData(KILL_TASK_URL);

  const columns = [
    {
      title: t('Task ID'),
      dataIndex: 'taskId',
      key: 'taskId',
      render: (taskId: TaskServerResponse['taskId']) => (
        <LinkButton
          className="hue-task-server__task-id-column"
          onClick={() => setSelectedTaskId(taskId)}
        >
          {taskId}
        </LinkButton>
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

  const {
    data: tasks,
    loading,
    error
  } = useLoadData<TaskServerResponse[]>(GET_TASKS_URL, {
    pollInterval: 5000
  });

  const errors = [
    {
      enabled: !!error,
      message: t(`Error fetching tasks: ${error}`)
    },
    {
      enabled: !Array.isArray(tasks),
      message: t(`Expected an array of tasks, but received: ${tasks}`)
    }
  ];

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
    const payload = new FormData();
    payload.append('task_id', taskId);

    save(payload, {
      onSuccess: response => {
        const { status, message } = response as KillTaskResponse;
        if (status === 'success') {
          huePubSub.publish('hue.global.info', { message: `Task: ${taskId} has been killed.` });
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

  const onKillTasks = () => {
    selectedTasks.forEach(task => {
      handleKillTask(task.taskId);
    });
    setSelectedTasks([]);
  };

  return (
    <div className="hue-task-server">
      <div className="hue-task-server__actions">
        <PrimaryButton onClick={onSchedulePopup}>{t('Schedule Task')}</PrimaryButton>
        <DangerButton onClick={onKillTasks} disabled={selectedTasks.length === 0}>
          {t('Kill Task')}
        </DangerButton>
        <Input
          type="text"
          placeholder={t('Search by task name, user ID, or task ID...')}
          onChange={onSearchChange}
          style={{ flexGrow: 1 }}
        />
        <Checkbox checked={statusFilter.success} onChange={onStatusFilterChange('success')}>
          <span className="hue-task-server__success-text">{t('Succeeded')}</span>
        </Checkbox>
        <Checkbox
          checked={statusFilter.running}
          onChange={onStatusFilterChange('running')}
          name="running"
        >
          <span className="hue-task-server__running-text">{t('Running')}</span>
        </Checkbox>
        <Checkbox
          checked={statusFilter.failure}
          onChange={onStatusFilterChange('failure')}
          name="failure"
        >
          <span className="hue-task-server__failed-text">{t('Failed')}</span>
        </Checkbox>
        <Checkbox checked={statusFilter.all} onChange={onStatusFilterChange('all')} name="all">
          <span>{t('All')}</span>
        </Checkbox>
      </div>
      <LoadingErrorWrapper loading={false} errors={errors}>
        <PaginatedTable<TaskServerResponse>
          loading={!tasks && loading}
          onRowSelect={setSelectedTasks}
          columns={columns}
          data={filteredTasks}
          rowKey="taskId"
          isDynamicHeight
          locale={{ emptyText: t('No tasks found') }}
        />
      </LoadingErrorWrapper>
      {showSchedulePopup && <ScheduleTaskModal onClose={() => showScheduleTaskPopup(false)} />}
      {!!selectedTaskId && (
        <TaskLogsModal taskId={selectedTaskId} onClose={() => setSelectedTaskId(null)} />
      )}
    </div>
  );
};

export default TaskServer;

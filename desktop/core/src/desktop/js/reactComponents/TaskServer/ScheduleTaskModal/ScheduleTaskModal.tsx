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

import React, { useState } from 'react';
import { Form, Input, Radio } from 'antd';
import { AxiosError } from 'axios';
import Modal from 'cuix/dist/components/Modal';

import { TaskServerResult } from '../types';
import useSaveData from '../../../utils/hooks/useSaveData/useSaveData';
import { SCHEDULE_NEW_TASK_URL, scheduleTasksCategory } from '../constants';
import { extractErrorMessage } from '../../../api/utils';
import huePubSub from '../../../utils/huePubSub';
import { i18nReact } from '../../../utils/i18nReact';
import LoadingErrorWrapper from '../../LoadingErrorWrapper/LoadingErrorWrapper';

interface ScheduleTaskModalProps {
  onClose: () => void;
  open?: boolean;
}

const ScheduleTaskModal = ({ onClose, open = true }: ScheduleTaskModalProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const [selectedTask, setSelectedTask] = useState<TaskServerResult['taskName']>('');
  const [params, setParams] = useState({});

  const handleChange = e => {
    const { name, value } = e.target;
    setParams(prevParams => ({
      ...prevParams,
      [name]: value
    }));
  };

  const { save, loading, error } = useSaveData(SCHEDULE_NEW_TASK_URL, {
    onSuccess: () => {
      huePubSub.publish('hue.global.info', { message: `Task submitted successfully` });
      onClose();
    },
    onError: (error: Error) => {
      const errorMessage = extractErrorMessage(error as AxiosError);
      huePubSub.publish('hue.global.error', {
        message: `Failed to submit scheduling task ${errorMessage}`
      });
    }
  });

  const handleSubmit = () => {
    save({
      taskName: selectedTask,
      taskParams: params
    });
  };

  const dropdownOptions = scheduleTasksCategory.map(task => ({
    label: task.label,
    value: task.value
  }));

  const errors = [
    {
      enabled: !!error,
      message: error?.message ?? t('An unknown error occurred.')
    }
  ];

  const selectedTaskChildren =
    scheduleTasksCategory.find(task => task.value === selectedTask)?.children ?? [];

  const isSubmitDisabled = !(
    selectedTask && selectedTaskChildren.every(task => params[task.value] > 0)
  );

  return (
    <Modal
      title={t('Schedule Task')}
      open={open}
      className="hue-schedule-task__modal"
      data-testid="hue-schedule-task__modal"
      width={530}
      okText={t('Schedule')}
      onOk={handleSubmit}
      okButtonProps={{ disabled: isSubmitDisabled, loading }}
      cancelText={t('Cancel')}
      onCancel={onClose}
      cancelButtonProps={{ disabled: loading }}
      closable={!loading}
    >
      <LoadingErrorWrapper errors={errors}>
        <div className="hue-schedule-task-selection">
          <Form.Item label={'Task'}>
            <Radio.Group
              options={dropdownOptions}
              value={selectedTask}
              onChange={e => setSelectedTask(e.target.value)}
              disabled={loading}
            />
          </Form.Item>
        </div>
        {selectedTask && (
          <div className="hue-schedule-task__input-group">
            {selectedTaskChildren.map(param => (
              <div key={param.value}>
                <Form.Item label={param.label}>
                  <Input
                    name={param.value}
                    type={param.type}
                    placeholder={param.label}
                    onChange={handleChange}
                    value={params[param.value]}
                    disabled={loading}
                  />
                </Form.Item>
              </div>
            ))}
          </div>
        )}
      </LoadingErrorWrapper>
    </Modal>
  );
};

export default ScheduleTaskModal;

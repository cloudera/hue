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
import { Form, Input, Select } from 'antd';
import Modal from 'cuix/dist/components/Modal';
import { TaskServerResult } from '../types';
import useSaveData from '../../../utils/hooks/useSaveData/useSaveData';
import { HANDLE_SUBMIT_URL } from '../constants';
import { extractErrorMessage } from '../../../api/utils';
import huePubSub from '../../../utils/huePubSub';
import { i18nReact } from '../../../utils/i18nReact';

import './ScheduleTaskModal.scss';
import { AxiosError } from 'axios';

const { Option } = Select;

const tasks = {
  document_cleanup: {
    params: [{ name: 'keep_days', label: 'Keep days', type: 'number' }]
  },
  tmp_clean_up: {
    params: [
      { name: 'cleanup_threshold', label: 'Cleanup threshold', type: 'number', max: 100 },
      { name: 'disk_check_interval', label: 'Disk check interval', type: 'number', max: 100 }
    ]
  }
};

interface ScheduleTaskModalProps {
  onClose: () => void;
  open?: boolean;
}

const ScheduleTaskModal: React.FC<ScheduleTaskModalProps> = ({
  onClose,
  open = true
}): JSX.Element => {
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

  const { save } = useSaveData(HANDLE_SUBMIT_URL, {
    postOptions: {
      qsEncodeData: false
    },
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

  return (
    <Modal
      title={t('Schedule Task')}
      open={open}
      onOk={handleSubmit}
      onCancel={onClose}
      okText={t('Submit')}
      width={530}
      cancellable={false}
      // className="hue-schedule-task__modal"
    >
      <div className="task-selection">
        <Select
          value={selectedTask}
          onChange={setSelectedTask}
          placeholder={t('Select Task')}
          className="hue-schedule-task__select"
          style={{ width: '100%' }}
        >
          {Object.keys(tasks).map(taskName => (
            <Option key={taskName} value={taskName}>
              {taskName}
            </Option>
          ))}
        </Select>
      </div>
      {selectedTask && (
        <div className="hue-schedule-task__modal__input-params">
          {tasks[selectedTask].params.map(param => (
            <div key={param.name}>
              <Form.Item label={param.label}>
                <Input
                  name={param.name}
                  type={param.type}
                  placeholder={param.label}
                  onChange={handleChange}
                  value={params[param.name] || 0}
                />
              </Form.Item>
            </div>
          ))}
        </div>
      )}
    </Modal>
  );
};

export default ScheduleTaskModal;

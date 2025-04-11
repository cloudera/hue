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

import React from 'react';
import Modal from 'cuix/dist/components/Modal';
import { TaskServerResponse } from '../types';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';
import { GET_TASK_LOG_URL } from '../constants';
import { i18nReact } from '../../../utils/i18nReact';
import LoadingErrorWrapper from '../../LoadingErrorWrapper/LoadingErrorWrapper';

import './TaskLogsModal.scss';

interface TaskLogsModalProps {
  taskId: TaskServerResponse['taskId'];
  onClose: () => void;
}

const TaskLogsModal: React.FC<TaskLogsModalProps> = ({ taskId, onClose }): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const { data, loading, error } = useLoadData<string>(GET_TASK_LOG_URL, {
    params: { task_id: taskId },
    skip: !taskId
  });

  const errors = [
    {
      enabled: !!error,
      message: error?.message ?? t('An error occurred while fetching task logs.')
    }
  ];

  return (
    <Modal open={!!taskId} title={t('Task Logs')} width={830} onCancel={onClose} footer={false}>
      <LoadingErrorWrapper loading={loading} errors={errors}>
        <div className="hue-task-server-logs">
          <pre>{data}</pre>
        </div>
      </LoadingErrorWrapper>
    </Modal>
  );
};

export default TaskLogsModal;

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
import { StorageDirectoryTableData } from '../../../../../reactComponents/FileChooser/types';
import { i18nReact } from '../../../../../utils/i18nReact';
import useSaveData from '../../../../../utils/hooks/useSaveData';
import { SET_REPLICATION_API_URL } from '../../../../../reactComponents/FileChooser/api';
import InputModal from '../../../InputModal/InputModal';

interface ReplicationActionProps {
  isOpen?: boolean;
  file: StorageDirectoryTableData;
  onSuccess: () => void;
  onError: (error: Error) => void;
  onClose: () => void;
}

const ReplicationAction = ({
  isOpen = true,
  file,
  onSuccess,
  onError,
  onClose
}: ReplicationActionProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const { save, loading } = useSaveData(undefined, {
    skip: !file.path,
    onSuccess,
    onError
  });

  const handleReplication = (replicationFactor: number) => {
    const payload = { path: file.path, replication_factor: replicationFactor };
    save(payload, { url: SET_REPLICATION_API_URL });
  };

  return (
    <InputModal
      title={t('Setting Replication factor for: ') + file.path}
      inputLabel={t('Replication factor:')}
      submitText={t('Submit')}
      showModal={isOpen}
      onSubmit={handleReplication}
      onClose={onClose}
      inputType="number"
      initialValue={file.replication}
      buttonDisabled={loading}
    />
  );
};

export default ReplicationAction;

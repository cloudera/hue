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
import { i18nReact } from '../../../../../utils/i18nReact';
import useSaveData from '../../../../../utils/hooks/useSaveData/useSaveData';
import { StorageDirectoryTableData } from '../../../../../reactComponents/FileChooser/types';
import {
  BULK_DELETION_API_URL,
  DELETION_API_URL
} from '../../../../../reactComponents/FileChooser/api';

interface DeletionModalProps {
  isOpen?: boolean;
  isTrashEnabled?: boolean;
  files: StorageDirectoryTableData[];
  setLoading: (value: boolean) => void;
  onSuccess: () => void;
  onError: (error: Error) => void;
  onClose: () => void;
}

const DeletionModal = ({
  isOpen = true,
  isTrashEnabled = false,
  files,
  setLoading,
  onSuccess,
  onError,
  onClose
}: DeletionModalProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const { save, loading } = useSaveData(undefined, {
    postOptions: {
      qsEncodeData: false
    },
    skip: !files.length,
    onSuccess,
    onError
  });

  const handleDeletion = (isForedSkipTrash: boolean = false) => {
    setLoading(true);
    const isSkipTrash = !isTrashEnabled || isForedSkipTrash;

    const formData = new FormData();
    files.forEach(selectedFile => {
      formData.append('path', selectedFile.path);
    });
    if (isSkipTrash) {
      formData.append('skip_trash', String(isSkipTrash));
    }

    if (files.length > 1) {
      save(formData, { url: BULK_DELETION_API_URL });
    } else {
      save(formData, { url: DELETION_API_URL });
    }
  };

  return (
    <Modal
      cancelText={t('Cancel')}
      className="hue-input-modal cuix antd"
      okText={isTrashEnabled ? t('Move to Trash') : t('Delete Permanently')}
      onCancel={onClose}
      onOk={() => handleDeletion()}
      open={isOpen}
      title={t('Delete file')}
      secondaryButtonText={isTrashEnabled ? t('Delete Permanently') : undefined}
      onSecondary={() => handleDeletion(true)}
      secondaryButtonProps={{ disabled: loading }}
      okButtonProps={{ disabled: loading }}
      cancelButtonProps={{ disabled: loading }}
    >
      {isTrashEnabled
        ? files.length > 1
          ? t('Do you want to move {{count}} items to trash?', { count: files.length })
          : t('Do you want to move "{{name}}" to trash?', { name: files[0]?.name })
        : files.length > 1
          ? t('Do you want to delete {{count}} items permanently?', { count: files.length })
          : t('Do you want to delete "{{name}}" permanently?', { name: files[0]?.name })}
    </Modal>
  );
};

export default DeletionModal;

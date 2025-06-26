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
import Modal from 'cuix/dist/components/Modal';
import { i18nReact } from '../../../../../../utils/i18nReact';
import useSaveData from '../../../../../../utils/hooks/useSaveData/useSaveData';
import { StorageDirectoryTableData } from '../../../../types';
import { BULK_DELETION_API_URL, DELETION_API_URL } from '../../../../api';

interface DeletionModalProps {
  isOpen?: boolean;
  isTrashEnabled?: boolean;
  files: StorageDirectoryTableData[];
  onSuccess: () => void;
  onError: (error: Error) => void;
  onClose: () => void;
}

const DeletionModal = ({
  isOpen = true,
  isTrashEnabled = false,
  files,
  onSuccess,
  onError,
  onClose
}: DeletionModalProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const [isMoveTrashClicked, setIsMoveTrashClicked] = useState<boolean>(false);

  const { save, loading } = useSaveData(undefined, {
    skip: !files.length,
    onSuccess,
    onError
  });

  const isMoveTrashButtonDisabled = loading && !isMoveTrashClicked;
  const isMoveTrashButtonLoading = loading && isMoveTrashClicked;
  const isDeletePermanentlyButtonDisabled = loading && isMoveTrashClicked;
  const isDeletePermanentlyButtonLoading = loading && !isMoveTrashClicked;
  const hasMultipleFiles = files.length > 1;

  const handleDeletion = (isSkipTrash: boolean) => {
    setIsMoveTrashClicked(!isSkipTrash);

    const formData = new FormData();
    files.forEach(selectedFile => {
      formData.append('path', selectedFile.path);
    });
    if (isSkipTrash) {
      formData.append('skip_trash', String(isSkipTrash));
    }

    if (hasMultipleFiles) {
      save(formData, { url: BULK_DELETION_API_URL });
    } else {
      save(formData, { url: DELETION_API_URL });
    }
  };

  return (
    <Modal
      open={isOpen}
      title={t('Confirm Delete')}
      className="hue-input-modal cuix antd"
      cancelText={t('Cancel')}
      okText={t('Move to Trash')}
      onOk={() => handleDeletion(false)}
      okButtonProps={{
        disabled: isMoveTrashButtonDisabled,
        loading: isMoveTrashButtonLoading,
        hidden: !isTrashEnabled
      }}
      secondaryButtonText={t('Delete Permanently')}
      onSecondary={() => handleDeletion(true)}
      secondaryButtonProps={{
        disabled: isDeletePermanentlyButtonDisabled,
        loading: isDeletePermanentlyButtonLoading,
        danger: true
      }}
      onCancel={onClose}
      cancelButtonProps={{ disabled: loading }}
      closable={!loading}
    >
      {isTrashEnabled
        ? hasMultipleFiles
          ? t('Do you want to move {{count}} items to trash?', { count: files.length })
          : t('Do you want to move "{{name}}" to trash?', { name: files[0]?.name })
        : hasMultipleFiles
          ? t('Do you want to delete {{count}} items permanently?', { count: files.length })
          : t('Do you want to delete "{{name}}" permanently?', { name: files[0]?.name })}
    </Modal>
  );
};

export default DeletionModal;

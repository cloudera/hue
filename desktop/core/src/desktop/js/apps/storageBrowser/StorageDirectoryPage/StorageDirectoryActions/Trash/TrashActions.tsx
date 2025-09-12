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
import { BorderlessButton } from 'cuix/dist/components/Button';
import Modal from 'cuix/dist/components/Modal';

import { i18nReact } from '../../../../../utils/i18nReact';
import { FileStats, StorageDirectoryTableData } from '../../../types';
import useSaveData from '../../../../../utils/hooks/useSaveData/useSaveData';
import { TRASH_PURGE, TRASH_RESTORE_BULK } from '../../../api';
import { inRestorableTrash } from '../../../utils/utils';

interface TrashActionsProps {
  selectedFiles: StorageDirectoryTableData[];
  currentPath: FileStats['path'];
  onActionSuccess: () => void;
  onActionError: (error: Error) => void;
  onTrashEmptySuccess: () => void;
}

enum Actions {
  restore = 'restore',
  trashEmpty = 'trashEmpty'
}

const TrashActions = ({
  selectedFiles,
  currentPath,
  onActionSuccess,
  onActionError,
  onTrashEmptySuccess
}: TrashActionsProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [selectedAction, setSelectedAction] = useState<Actions | undefined>();

  const { save, loading } = useSaveData(undefined, {
    onSuccess: () => setIsModalOpen(false),
    onError: onActionError
  });

  const onRestoreFiles = () => {
    const formData = new FormData();
    selectedFiles.forEach(selectedFile => {
      formData.append('path', selectedFile.path);
    });

    save(formData, { url: TRASH_RESTORE_BULK, onSuccess: onActionSuccess });
  };

  const onTrashEmpty = () => {
    save(undefined, {
      url: TRASH_PURGE,
      onSuccess: onTrashEmptySuccess
    });
  };

  const handleActionClick = (clickedAction: Actions) => {
    setIsModalOpen(true);
    setSelectedAction(clickedAction);
  };

  const handleModalConfirm = () => {
    if (selectedAction === Actions.restore) {
      return onRestoreFiles();
    }
    if (selectedAction === Actions.trashEmpty) {
      return onTrashEmpty();
    }
  };

  const handleModalCancel = () => {
    setIsModalOpen(false);
    setSelectedAction(undefined);
  };

  return (
    <>
      <BorderlessButton
        disabled={!selectedFiles.length || !inRestorableTrash(currentPath)}
        onClick={() => handleActionClick(Actions.restore)}
      >
        {t('Restore')}
      </BorderlessButton>
      <BorderlessButton onClick={() => handleActionClick(Actions.trashEmpty)}>
        {t('Empty trash')}
      </BorderlessButton>
      <Modal
        open={isModalOpen}
        title={selectedAction === Actions.restore ? t('Restore') : t('Empty trash')}
        className="cuix antd"
        okText={t('Yes')}
        onOk={handleModalConfirm}
        okButtonProps={{ loading }}
        cancelText={t('No')}
        onCancel={handleModalCancel}
        cancelButtonProps={{ disabled: loading }}
        closable={!loading}
      >
        {selectedAction === Actions.restore
          ? t('Are you sure you want to restore these files?')
          : t('Are you sure you want to permanently delete all your trash?')}
      </Modal>
    </>
  );
};

export default TrashActions;

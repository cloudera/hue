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

import { i18nReact } from '../../../../../utils/i18nReact';

import { BorderlessButton } from 'cuix/dist/components/Button';
import { FileStats, StorageDirectoryTableData } from '../../../types';
import useSaveData from '../../../../../utils/hooks/useSaveData/useSaveData';
import { TRASH_PURGE, TRASH_RESTORE_BULK } from '../../../api';
import { inRestorableTrash } from '../../../../../utils/storageBrowserUtils';

interface TrashActionsProps {
  selectedFiles: StorageDirectoryTableData[];
  currentPath: FileStats['path'];
  isTrashEmpty: boolean;
  onActionSuccess: () => void;
  onActionError: (error: Error) => void;
  setLoadingFiles: (value: boolean) => void;
  onTrashEmptySuccess: () => void;
}

const TrashActions = ({
  selectedFiles,
  currentPath,
  isTrashEmpty,
  onActionSuccess,
  onActionError,
  setLoadingFiles,
  onTrashEmptySuccess
}: TrashActionsProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const { save } = useSaveData(undefined, {
    postOptions: {
      qsEncodeData: false
    },
    onSuccess: onActionSuccess,
    onError: onActionError
  });

  const onRestoreFiles = () => {
    const formData = new FormData();
    selectedFiles.forEach(selectedFile => {
      formData.append('path', selectedFile.path);
    });
    setLoadingFiles(true);

    save(formData, { url: TRASH_RESTORE_BULK });
  };

  const onTrashEmpty = () => {
    setLoadingFiles(true);

    save(undefined, {
      url: TRASH_PURGE,
      onSuccess: onTrashEmptySuccess
    });
  };

  return (
    <>
      <BorderlessButton
        data-event=""
        disabled={!selectedFiles.length || !inRestorableTrash(currentPath)}
        onClick={onRestoreFiles}
      >
        {t('Restore')}
      </BorderlessButton>
      <BorderlessButton data-event="" disabled={isTrashEmpty} onClick={onTrashEmpty}>
        {t('Empty trash')}
      </BorderlessButton>
    </>
  );
};

export default TrashActions;

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

import React, { useState, useRef } from 'react';
import { Dropdown } from 'antd';
import { MenuItemGroupType } from 'antd/lib/menu/hooks/useItems';

import FolderIcon from '@cloudera/cuix-core/icons/react/ProjectIcon';
import FileIcon from '@cloudera/cuix-core/icons/react/DocumentationIcon';
import DropDownIcon from '@cloudera/cuix-core/icons/react/DropdownIcon';
import ImportIcon from '@cloudera/cuix-core/icons/react/ImportIcon';
import { PrimaryButton } from 'cuix/dist/components/Button';

import { i18nReact } from '../../../../../utils/i18nReact';
import { CREATE_DIRECTORY_API_URL, CREATE_FILE_API_URL } from '../../../api';
import { FileStats } from '../../../types';
import useSaveData from '../../../../../utils/hooks/useSaveData/useSaveData';
import InputModal from '../../../../../reactComponents/InputModal/InputModal';

import './CreateAndUploadAction.scss';

interface CreateAndUploadActionProps {
  currentPath: FileStats['path'];
  onActionSuccess: () => void;
  onFilesUpload: (files: File[]) => void;
  onActionError: (error: Error) => void;
}

enum ActionType {
  createFile = 'createFile',
  createFolder = 'createFolder',
  uploadFile = 'uploadFile'
}

const CreateAndUploadAction = ({
  currentPath,
  onActionSuccess,
  onFilesUpload,
  onActionError
}: CreateAndUploadActionProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedAction, setSelectedAction] = useState<ActionType>();

  const onModalClose = () => {
    setSelectedAction(undefined);
  };

  const onApiSuccess = () => {
    onModalClose();
    onActionSuccess();
  };

  const { save, loading, error } = useSaveData(undefined, {
    postOptions: { qsEncodeData: true }, // TODO: Remove once API supports RAW JSON payload
    onSuccess: onApiSuccess,
    onError: onActionError
  });

  const onActionClick = (action: ActionType) => () => {
    setSelectedAction(action);
  };

  const onFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const filesArray = Array.from(e.target.files);
      onFilesUpload(filesArray);
    }
    // Reset the input value so the same file can be selected again
    e.target.value = '';
  };

  const newActionsMenuItems: MenuItemGroupType[] = [
    {
      key: 'create',
      type: 'group',
      label: t('CREATE'),
      children: [
        {
          icon: <FileIcon />,
          key: ActionType.createFile,
          label: t('New File'),
          onClick: onActionClick(ActionType.createFile)
        },
        {
          icon: <FolderIcon />,
          key: ActionType.createFolder,
          label: t('New Folder'),
          onClick: onActionClick(ActionType.createFolder)
        }
      ]
    },
    {
      key: 'upload',
      type: 'group',
      label: t('UPLOAD'),
      children: [
        {
          icon: <ImportIcon />,
          key: ActionType.uploadFile,
          label: t('Upload File'),
          onClick: () => fileInputRef.current?.click()
        }
      ]
    }
  ];

  const handleCreate = (name: string | number) => {
    const url = {
      [ActionType.createFile]: CREATE_FILE_API_URL,
      [ActionType.createFolder]: CREATE_DIRECTORY_API_URL
    }[selectedAction ?? ''];

    if (!url) {
      return;
    }
    save({ path: currentPath, name }, { url });
  };

  return (
    <>
      <Dropdown
        overlayClassName="hue-storage-browser__actions-dropdown"
        menu={{
          items: newActionsMenuItems,
          className: 'hue-storage-browser__action-menu'
        }}
        trigger={['click']}
      >
        <PrimaryButton data-testid="hue-storage-browser-directory__actions-bar__new-btn">
          {t('New')}
          <DropDownIcon />
        </PrimaryButton>
      </Dropdown>

      {(selectedAction === ActionType.createFolder || selectedAction === ActionType.createFile) && (
        <InputModal
          showModal={true}
          title={selectedAction === ActionType.createFolder ? t('Create Folder') : t('Create File')}
          inputLabel={
            selectedAction === ActionType.createFolder ? t('Folder name') : t('File name')
          }
          submitText={t('Create')}
          onSubmit={handleCreate}
          onClose={onModalClose}
          loading={loading}
          error={error}
        />
      )}

      <input
        ref={fileInputRef}
        type="file"
        id="file-upload-input"
        hidden
        multiple
        onChange={onFileUpload}
      />
    </>
  );
};

export default CreateAndUploadAction;

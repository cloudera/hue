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
import { Dropdown } from 'antd';
import { MenuItemGroupType } from 'antd/lib/menu/hooks/useItems';
import Modal from 'cuix/dist/components/Modal';
import FolderIcon from '@cloudera/cuix-core/icons/react/ProjectIcon';
import FileIcon from '@cloudera/cuix-core/icons/react/DocumentationIcon';
import DropDownIcon from '@cloudera/cuix-core/icons/react/DropdownIcon';
import ImportIcon from '@cloudera/cuix-core/icons/react/ImportIcon';
import { PrimaryButton } from 'cuix/dist/components/Button';

import { i18nReact } from '../../../../utils/i18nReact';
import huePubSub from '../../../../utils/huePubSub';
import {
  CREATE_DIRECTORY_API_URL,
  CREATE_FILE_API_URL
} from '../../../../reactComponents/FileChooser/api';
import { FileStats } from '../../../../reactComponents/FileChooser/types';
import useSaveData from '../../../../utils/hooks/useSaveData';
import InputModal from '../../InputModal/InputModal';
import './CreateAndUploadAction.scss';
import DragAndDrop from '../../../../reactComponents/DragAndDrop/DragAndDrop';

interface CreateAndUploadActionProps {
  currentPath: FileStats['path'];
  onSuccessfulAction: () => void;
  setLoadingFiles: (value: boolean) => void;
  onFilesUpload: (files: File[]) => void;
}

enum ActionType {
  createFile = 'createFile',
  createFolder = 'createFolder',
  uploadFile = 'uploadFile'
}

const CreateAndUploadAction = ({
  currentPath,
  onSuccessfulAction,
  setLoadingFiles,
  onFilesUpload
}: CreateAndUploadActionProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const [selectedAction, setSelectedAction] = useState<ActionType>();

  const onApiSuccess = () => {
    setLoadingFiles(false);
    onSuccessfulAction();
  };

  const onApiError = (error: Error) => {
    setLoadingFiles(false);
    huePubSub.publish('hue.error', error);
  };

  const { save } = useSaveData(undefined, {
    onSuccess: onApiSuccess,
    onError: onApiError
  });

  const onActionClick = (action: ActionType) => () => {
    setSelectedAction(action);
  };

  const onModalClose = () => {
    setSelectedAction(undefined);
  };

  const onUpload = (files: File[]) => {
    onModalClose();
    onFilesUpload(files);
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
          label: t('New Upload'),
          onClick: onActionClick(ActionType.uploadFile)
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
    setLoadingFiles(true);
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
        <PrimaryButton data-event="">
          {t('New')}
          <DropDownIcon />
        </PrimaryButton>
      </Dropdown>
      <InputModal
        title={t('Create New Folder')}
        inputLabel={t('Enter New Folder Name')}
        submitText={t('Create')}
        showModal={selectedAction === ActionType.createFolder}
        onSubmit={handleCreate}
        onClose={onModalClose}
      />
      <InputModal
        title={t('Create New File')}
        inputLabel={t('Enter New File Name')}
        submitText={t('Create')}
        showModal={selectedAction === ActionType.createFile}
        onSubmit={handleCreate}
        onClose={onModalClose}
      />
      <Modal
        onCancel={onModalClose}
        className="cuix antd"
        open={selectedAction === ActionType.uploadFile}
        title={t('Upload A File')}
      >
        <div className="hue-file-upload-modal">
          <DragAndDrop onDrop={onUpload} />
        </div>
      </Modal>
    </>
  );
};

export default CreateAndUploadAction;

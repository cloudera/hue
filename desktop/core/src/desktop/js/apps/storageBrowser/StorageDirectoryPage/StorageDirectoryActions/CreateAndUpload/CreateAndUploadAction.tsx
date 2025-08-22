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
import { ItemType, MenuItemGroupType } from 'antd/lib/menu/hooks/useItems';
import Modal from 'cuix/dist/components/Modal';
import FolderIcon from '@cloudera/cuix-core/icons/react/ProjectIcon';
import FileIcon from '@cloudera/cuix-core/icons/react/DocumentationIcon';
import DropDownIcon from '@cloudera/cuix-core/icons/react/DropdownIcon';
import ImportIcon from '@cloudera/cuix-core/icons/react/ImportIcon';
import BucketIcon from '@cloudera/cuix-core/icons/react/BucketIcon';
import DatabaseIcon from '@cloudera/cuix-core/icons/react/DatabaseIcon';
import DataBrowserIcon from '@cloudera/cuix-core/icons/react/DataBrowserIcon';
import { PrimaryButton } from 'cuix/dist/components/Button';

import { i18nReact } from '../../../../../utils/i18nReact';
import { CREATE_DIRECTORY_API_URL, CREATE_FILE_API_URL } from '../../../api';
import {
  isOFS,
  isABFSRoot,
  isGSRoot,
  isOFSServiceID,
  isOFSVol,
  isS3Root,
  isABFS,
  isGS,
  isS3
} from '../../../../../utils/storageBrowserUtils';
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
  uploadFile = 'uploadFile',
  createBucket = 'createBucket',
  createVolume = 'createVolume',
  createFileSystem = 'createFileSystem'
}

type ActionItem = {
  icon: React.ReactElement;
  label: string;
  modal?: {
    title: string;
    label: string;
  };
  api?: string;
};

const actionConfig: Record<ActionType, ActionItem> = {
  [ActionType.createFile]: {
    icon: <FileIcon />,
    label: 'New File',
    modal: { title: 'Create File', label: 'File name' },
    api: CREATE_FILE_API_URL
  },
  [ActionType.createFolder]: {
    icon: <FolderIcon />,
    label: 'New Folder',
    modal: { title: 'Create Folder', label: 'Folder name' },
    api: CREATE_DIRECTORY_API_URL
  },
  [ActionType.createBucket]: {
    icon: <BucketIcon />,
    label: 'New Bucket',
    modal: { title: 'Create Bucket', label: 'Bucket name' },
    api: CREATE_DIRECTORY_API_URL
  },
  [ActionType.createVolume]: {
    icon: <DatabaseIcon />,
    label: 'New Volume',
    modal: { title: 'Create Volume', label: 'Volume name' },
    api: CREATE_DIRECTORY_API_URL
  },
  [ActionType.createFileSystem]: {
    icon: <DataBrowserIcon />,
    label: 'New File System',
    modal: { title: 'Create File System', label: 'File system name' },
    api: CREATE_DIRECTORY_API_URL
  },
  [ActionType.uploadFile]: {
    icon: <ImportIcon />,
    label: 'Upload File'
  }
};

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
    options: { qsEncodeData: true }, // TODO: Remove once API supports RAW JSON payload
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
  }
  
  const getCreateActionChildren = (): ItemType[] => {
    const fileActions = [ActionType.createFile, ActionType.createFolder].map(a => ({
      icon: actionConfig[a].icon,
      key: a,
      label: t(actionConfig[a].label),
      onClick: onActionClick(a)
    }));

    if (isS3(currentPath)) {
      return isS3Root(currentPath)
        ? [
            {
              icon: actionConfig[ActionType.createBucket].icon,
              key: ActionType.createBucket,
              label: t(actionConfig[ActionType.createBucket].label),
              onClick: onActionClick(ActionType.createBucket)
            }
          ]
        : fileActions;
    }

    if (isGS(currentPath)) {
      return isGSRoot(currentPath)
        ? [
            {
              icon: actionConfig[ActionType.createBucket].icon,
              key: ActionType.createBucket,
              label: t(actionConfig[ActionType.createBucket].label),
              onClick: onActionClick(ActionType.createBucket)
            }
          ]
        : fileActions;
    }

    if (isABFS(currentPath)) {
      return isABFSRoot(currentPath)
        ? [
            {
              icon: actionConfig[ActionType.createFileSystem].icon,
              key: ActionType.createFileSystem,
              label: t(actionConfig[ActionType.createFileSystem].label),
              onClick: onActionClick(ActionType.createFileSystem)
            }
          ]
        : fileActions;
    }

    if (isOFS(currentPath)) {
      if (isOFSServiceID(currentPath)) {
        return [
          {
            icon: actionConfig[ActionType.createVolume].icon,
            key: ActionType.createVolume,
            label: t(actionConfig[ActionType.createVolume].label),
            onClick: onActionClick(ActionType.createVolume)
          }
        ];
      }
      if (isOFSVol(currentPath)) {
        return [
          {
            icon: actionConfig[ActionType.createBucket].icon,
            key: ActionType.createBucket,
            label: t(actionConfig[ActionType.createBucket].label),
            onClick: onActionClick(ActionType.createBucket)
          }
        ];
      }
      return fileActions;
    }

    return fileActions;
  };

  const newActionsMenuItems: MenuItemGroupType[] = [
    {
      key: 'create',
      type: 'group',
      label: t('CREATE'),
      children: getCreateActionChildren()
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
    const url = selectedAction ? actionConfig[selectedAction]?.api : undefined;

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
      {selectedAction !== undefined && selectedAction !== ActionType.uploadFile && (
        <InputModal
          showModal={true}
          title={
            actionConfig[selectedAction].modal
              ? t(actionConfig[selectedAction].modal.title)
              : t('Create')
          }
          inputLabel={
            actionConfig[selectedAction].modal
              ? t(actionConfig[selectedAction].modal.label)
              : t('Name')
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

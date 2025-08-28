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
  isABFSRoot,
  isGSRoot,
  isOFSServiceID,
  isOFSVol,
  isS3Root,
  isFileSystemNonRoot
} from '../../../utils/utils';
import { FileStats } from '../../../types';
import useSaveData from '../../../../../utils/hooks/useSaveData/useSaveData';
import InputModal from '../../../../../reactComponents/InputModal/InputModal';

import './CreateAndUploadAction.scss';
import { TFunction } from 'i18next';

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
  visible: (path: string) => boolean;
  group: string;
};

const getActionConfig = (t: TFunction): Record<ActionType, ActionItem> => ({
  [ActionType.createFile]: {
    icon: <FileIcon />,
    label: t('New File'),
    modal: { title: t('Create File'), label: t('File name') },
    api: CREATE_FILE_API_URL,
    group: 'create',
    visible: path => isFileSystemNonRoot(path)
  },
  [ActionType.createFolder]: {
    icon: <FolderIcon />,
    label: t('New Folder'),
    modal: { title: t('Create Folder'), label: t('Folder name') },
    api: CREATE_DIRECTORY_API_URL,
    group: 'create',
    visible: path => isFileSystemNonRoot(path)
  },
  [ActionType.createBucket]: {
    icon: <BucketIcon />,
    label: t('New Bucket'),
    modal: { title: t('Create Bucket'), label: t('Bucket name') },
    api: CREATE_DIRECTORY_API_URL,
    group: 'create',
    visible: path => isS3Root(path) || isGSRoot(path) || isOFSVol(path)
  },
  [ActionType.createVolume]: {
    icon: <DatabaseIcon />,
    label: t('New Volume'),
    modal: { title: t('Create Volume'), label: t('Volume name') },
    api: CREATE_DIRECTORY_API_URL,
    group: 'create',
    visible: path => isOFSServiceID(path)
  },
  [ActionType.createFileSystem]: {
    icon: <DataBrowserIcon />,
    label: t('New File System'),
    modal: { title: t('Create File System'), label: t(')File system name') },
    api: CREATE_DIRECTORY_API_URL,
    group: 'create',
    visible: path => isABFSRoot(path)
  },
  [ActionType.uploadFile]: {
    icon: <ImportIcon />,
    label: t('Upload File'),
    group: 'upload',
    visible: path => isFileSystemNonRoot(path)
  }
});

const CreateAndUploadAction = ({
  currentPath,
  onActionSuccess,
  onFilesUpload,
  onActionError
}: CreateAndUploadActionProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedAction, setSelectedAction] = useState<ActionType>();
  const actionConfig = getActionConfig(t);

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
  };

  const getCreateActionChildren = (): ItemType[] => {
    return (Object.entries(actionConfig) as [ActionType, (typeof actionConfig)[ActionType]][])
      .filter(([, cfg]) => cfg.group !== 'upload' && cfg.visible(currentPath))
      .map(([action, cfg]) => ({
        icon: cfg.icon,
        key: action,
        label: cfg.label,
        onClick: onActionClick(action)
      }));
  };

  const newActionsMenuItems: MenuItemGroupType[] = [
    {
      key: 'create',
      type: 'group' as const,
      label: t('CREATE'),
      children: getCreateActionChildren()
    },
    {
      key: 'upload',
      type: 'group' as const,
      label: t('UPLOAD'),
      children: actionConfig[ActionType.uploadFile].visible(currentPath)
        ? [
            {
              icon: actionConfig[ActionType.uploadFile].icon,
              key: ActionType.uploadFile,
              label: actionConfig[ActionType.uploadFile].label,
              onClick: () => fileInputRef.current?.click()
            }
          ]
        : []
    }
  ].filter(group => group.children && group.children.length > 0);

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
              ? actionConfig[selectedAction].modal.title
              : t('Create')
          }
          inputLabel={
            actionConfig[selectedAction].modal
              ? actionConfig[selectedAction].modal.label
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

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

import React, { useMemo, useState } from 'react';
import { Dropdown } from 'antd';
import { MenuItemType } from 'antd/lib/menu/hooks/useItems';

import Button from 'cuix/dist/components/Button';
import DropDownIcon from '@cloudera/cuix-core/icons/react/DropdownIcon';
import InfoIcon from '@cloudera/cuix-core/icons/react/InfoIcon';
import DuplicateIcon from '@cloudera/cuix-core/icons/react/DuplicateIcon';
import CopyClipboardIcon from '@cloudera/cuix-core/icons/react/CopyClipboardIcon';

import { i18nReact } from '../../../../utils/i18nReact';
import { inTrash } from '../../../../utils/storageBrowserUtils';
import {
  RENAME_API_URL,
  SET_REPLICATION_API_URL,
  BULK_COPY_API_URL,
  BULK_MOVE_API_URL
} from '../../../../reactComponents/FileChooser/api';
import huePubSub from '../../../../utils/huePubSub';
import useSaveData from '../../../../utils/hooks/useSaveData';

import SummaryModal from '../SummaryModal/SummaryModal';
import InputModal from '../../InputModal/InputModal';
import FileChooserModal from '../../FileChooserModal/FileChooserModal';

import './StorageBrowserActions.scss';
import {
  FileStats,
  StorageDirectoryTableData
} from '../../../../reactComponents/FileChooser/types';
import { ActionType, getActionsConfig } from './StorageBrowserActions.util';

interface StorageBrowserRowActionsProps {
  currentPath: FileStats['path'];
  selectedFiles: StorageDirectoryTableData[];
  onSuccessfulAction: () => void;
  setLoadingFiles: (value: boolean) => void;
}

const StorageBrowserActions = ({
  currentPath,
  selectedFiles,
  onSuccessfulAction,
  setLoadingFiles
}: StorageBrowserRowActionsProps): JSX.Element => {
  const [selectedFilePath, setSelectedFilePath] = useState<string>('');
  const [selectedAction, setSelectedAction] = useState<ActionType>();

  const { t } = i18nReact.useTranslation();

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

  const { save: saveForm } = useSaveData(undefined, {
    postOptions: {
      qsEncodeData: false,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    },
    onSuccess: onApiSuccess,
    onError: onApiError
  });

  const handleRename = (value: string) => {
    setLoadingFiles(true);
    const payload = { source_path: selectedFilePath, destination_path: value };
    save(payload, { url: RENAME_API_URL });
  };

  const handleReplication = (replicationFactor: number) => {
    const payload = { path: selectedFilePath, replication_factor: replicationFactor };
    save(payload, { url: SET_REPLICATION_API_URL });
  };

  const handleCopyOrMove = (destination_path: string) => {
    const url = {
      [ActionType.Copy]: BULK_COPY_API_URL,
      [ActionType.Move]: BULK_MOVE_API_URL
    }[selectedAction ?? ''];

    if (!url) {
      return;
    }

    const formData = new FormData();
    selectedFiles.map(selectedFile => {
      formData.append('source_path', selectedFile.path);
    });
    formData.append('destination_path', destination_path);

    setLoadingFiles(true);
    saveForm(formData, { url });
  };

  const actionConfig = getActionsConfig(selectedFiles);

  const onActionClick = (action: ActionType, path: string) => () => {
    setSelectedFilePath(path);
    setSelectedAction(action);
  };

  const onModalClose = () => {
    setSelectedFilePath('');
    setSelectedAction(undefined);
  };

  const actionItems: MenuItemType[] = useMemo(() => {
    const isActionEnabled =
      selectedFiles && selectedFiles.length > 0 && !inTrash(selectedFiles[0].path);
    if (!isActionEnabled) {
      return [];
    }

    const actions: MenuItemType[] = [
      {
        disabled: !actionConfig.isCopyEnabled,
        key: ActionType.Copy,
        icon: <CopyClipboardIcon />,
        label: t('Copy'),
        onClick: onActionClick(ActionType.Copy, selectedFiles[0].path)
      },
      {
        disabled: !actionConfig.isMoveEnabled,
        key: ActionType.Move,
        icon: <CopyClipboardIcon />,
        label: t('Move'),
        onClick: onActionClick(ActionType.Move, selectedFiles[0].path)
      },
      {
        disabled: !actionConfig.isSummaryEnabled,
        key: ActionType.Summary,
        icon: <InfoIcon />,
        label: t('View Summary'),
        onClick: onActionClick(ActionType.Summary, selectedFiles[0].path)
      },
      {
        disabled: !actionConfig.isRenameEnabled,
        key: ActionType.Rename,
        icon: <InfoIcon />,
        label: t('Rename'),
        onClick: onActionClick(ActionType.Rename, selectedFiles[0].path)
      },
      {
        disabled: !actionConfig.isReplicationEnabled,
        key: ActionType.Repilcation,
        icon: <DuplicateIcon />,
        label: t('Set Replication'),
        onClick: onActionClick(ActionType.Repilcation, selectedFiles[0].path)
      }
    ].filter(e => !e.disabled);
    return actions;
  }, [selectedFiles, actionConfig]);

  return (
    <>
      <Dropdown
        overlayClassName="hue-storage-browser__table-actions-dropdown"
        menu={{
          items: actionItems,
          className: 'hue-storage-browser__table-actions-menu'
        }}
        trigger={['click']}
        disabled={actionItems.length === 0 ? true : false}
      >
        <Button data-event="">
          {t('Actions')}
          <DropDownIcon />
        </Button>
      </Dropdown>
      <SummaryModal
        showModal={selectedAction === ActionType.Summary}
        path={selectedFilePath}
        onClose={onModalClose}
      />
      <InputModal
        title={t('Rename')}
        inputLabel={t('Enter new name')}
        submitText={t('Rename')}
        showModal={selectedAction === ActionType.Rename}
        onSubmit={handleRename}
        onClose={onModalClose}
        inputType="text"
        initialValue={selectedFiles[0]?.name}
      />
      <InputModal
        title={t('Setting Replication factor for: ') + selectedFilePath}
        inputLabel={t('Replication factor:')}
        submitText={t('Submit')}
        showModal={selectedAction === ActionType.Repilcation}
        onSubmit={handleReplication}
        onClose={onModalClose}
        inputType="number"
        initialValue={selectedFiles[0]?.replication}
      />
      <FileChooserModal
        onClose={onModalClose}
        onSubmit={handleCopyOrMove}
        showModal={selectedAction === ActionType.Move || selectedAction === ActionType.Copy}
        title={selectedAction === ActionType.Move ? t('Move to') : t('Copy to')}
        sourcePath={currentPath}
        submitText={selectedAction === ActionType.Move ? t('Move') : t('Copy')}
      />
    </>
  );
};

export default StorageBrowserActions;

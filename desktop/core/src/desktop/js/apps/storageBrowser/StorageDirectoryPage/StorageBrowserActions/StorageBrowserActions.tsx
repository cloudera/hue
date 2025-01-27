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
import SummaryIcon from '@cloudera/cuix-core/icons/react/SummaryIcon';
import EditIcon from '@cloudera/cuix-core/icons/react/EditIcon';
import DuplicateIcon from '@cloudera/cuix-core/icons/react/DuplicateIcon';
import CopyClipboardIcon from '@cloudera/cuix-core/icons/react/CopyClipboardIcon';
import DataMovementIcon from '@cloudera/cuix-core/icons/react/DataMovementIcon';
import DeleteIcon from '@cloudera/cuix-core/icons/react/DeleteIcon';
import CollapseIcon from '@cloudera/cuix-core/icons/react/CollapseViewIcon';
import ExpandIcon from '@cloudera/cuix-core/icons/react/ExpandViewIcon';
import DownloadIcon from '@cloudera/cuix-core/icons/react/DownloadIcon';
import GroupsIcon from '@cloudera/cuix-core/icons/react/GroupsIcon';

import { i18nReact } from '../../../../utils/i18nReact';
import huePubSub from '../../../../utils/huePubSub';
import './StorageBrowserActions.scss';
import {
  FileStats,
  ListDirectory,
  StorageDirectoryTableData
} from '../../../../reactComponents/FileChooser/types';
import { ActionType, getEnabledActions } from './StorageBrowserActions.util';
import MoveCopyModal from './MoveCopyModal/MoveCopyModal';
import RenameModal from './RenameModal/RenameModal';
import ReplicationModal from './ReplicationModal/ReplicationModal';
import SummaryModal from './SummaryModal/SummaryModal';
import DeletionModal from './DeletionModal/DeletionModal';
import CompressionModal from './CompressionModal/CompressionModal';
import ExtractionModal from './ExtractionModal/ExtractionModal';
import { DOWNLOAD_API_URL } from '../../../../reactComponents/FileChooser/api';
import ChangeOwnerAndGroupModal from './ChangeOwnerAndGroupModal/ChangeOwnerAndGroupModal';

interface StorageBrowserRowActionsProps {
  // TODO: move relevant keys to hue_config
  superUser?: ListDirectory['superuser'];
  superGroup?: ListDirectory['supergroup'];
  users?: ListDirectory['users'];
  groups?: ListDirectory['groups'];
  isFsSuperUser?: ListDirectory['is_fs_superuser'];
  isTrashEnabled?: boolean;
  currentPath: FileStats['path'];
  selectedFiles: StorageDirectoryTableData[];
  onSuccessfulAction: () => void;
  setLoadingFiles: (value: boolean) => void;
}

const iconsMap: Record<ActionType, JSX.Element> = {
  [ActionType.Copy]: <CopyClipboardIcon />,
  [ActionType.Move]: <DataMovementIcon />,
  [ActionType.Rename]: <EditIcon />,
  [ActionType.Replication]: <DuplicateIcon />,
  [ActionType.Delete]: <DeleteIcon />,
  [ActionType.Summary]: <SummaryIcon />,
  [ActionType.Compress]: <CollapseIcon />,
  [ActionType.Extract]: <ExpandIcon />,
  [ActionType.Download]: <DownloadIcon />,
  [ActionType.ChangeOwnerAndGroup]: <GroupsIcon />
};

const StorageBrowserActions = ({
  superUser,
  superGroup,
  users,
  groups,
  isFsSuperUser,
  isTrashEnabled,
  currentPath,
  selectedFiles,
  onSuccessfulAction,
  setLoadingFiles
}: StorageBrowserRowActionsProps): JSX.Element => {
  const [selectedAction, setSelectedAction] = useState<ActionType>();

  const { t } = i18nReact.useTranslation();

  const closeModal = () => {
    setSelectedAction(undefined);
  };

  const downloadFile = () => {
    huePubSub.publish('hue.global.info', { message: t('Downloading your file, Please wait...') });
    location.href = `${DOWNLOAD_API_URL}?path=${selectedFiles[0]?.path}`;
  };

  const onActionClick = (actionType: ActionType) => () => {
    if (actionType === ActionType.Download) {
      return downloadFile();
    }
    setSelectedAction(actionType);
  };

  const onApiSuccess = () => {
    setLoadingFiles(false);
    closeModal();
    onSuccessfulAction();
  };

  const onApiError = (error: Error) => {
    setLoadingFiles(false);
    huePubSub.publish('hue.error', error);
  };

  const actionItems: MenuItemType[] = useMemo(() => {
    const enabledActions = getEnabledActions(selectedFiles, isFsSuperUser);
    return enabledActions.map(action => ({
      key: String(action.type),
      label: t(action.label),
      icon: iconsMap[action.type],
      onClick: onActionClick(action.type)
    }));
  }, [selectedFiles]);

  return (
    <>
      <Dropdown
        overlayClassName="hue-storage-browser__table-actions-dropdown"
        menu={{
          items: actionItems,
          className: 'hue-storage-browser__table-actions-menu'
        }}
        trigger={['click']}
        disabled={!actionItems.length}
      >
        <Button data-event="">
          {t('Actions')}
          <DropDownIcon />
        </Button>
      </Dropdown>
      {selectedAction === ActionType.Summary && (
        <SummaryModal path={selectedFiles[0].path} onClose={closeModal} />
      )}
      {selectedAction === ActionType.Rename && (
        <RenameModal
          file={selectedFiles[0]}
          onSuccess={onApiSuccess}
          onError={onApiError}
          onClose={closeModal}
        />
      )}
      {selectedAction === ActionType.Replication && (
        <ReplicationModal
          file={selectedFiles[0]}
          onSuccess={onApiSuccess}
          onError={onApiError}
          onClose={closeModal}
        />
      )}
      {(selectedAction === ActionType.Move || selectedAction === ActionType.Copy) && (
        <MoveCopyModal
          action={selectedAction}
          files={selectedFiles}
          currentPath={currentPath}
          onSuccess={onApiSuccess}
          onError={onApiError}
          onClose={closeModal}
          setLoadingFiles={setLoadingFiles}
        />
      )}
      {selectedAction === ActionType.Delete && (
        <DeletionModal
          isTrashEnabled={isTrashEnabled}
          files={selectedFiles}
          onSuccess={onApiSuccess}
          onError={onApiError}
          onClose={closeModal}
          setLoading={setLoadingFiles}
        />
      )}
      {selectedAction === ActionType.Compress && (
        <CompressionModal
          currentPath={currentPath}
          files={selectedFiles}
          onSuccess={onApiSuccess}
          onError={onApiError}
          onClose={closeModal}
          setLoading={setLoadingFiles}
        />
      )}
      {selectedAction === ActionType.Extract && (
        <ExtractionModal
          currentPath={currentPath}
          file={selectedFiles[0]}
          onSuccess={onApiSuccess}
          onError={onApiError}
          onClose={closeModal}
          setLoading={setLoadingFiles}
        />
      )}
      {selectedAction === ActionType.ChangeOwnerAndGroup && (
        <ChangeOwnerAndGroupModal
          files={selectedFiles}
          superUser={superUser}
          superGroup={superGroup}
          users={users}
          groups={groups}
          onSuccess={onApiSuccess}
          onError={onApiError}
          onClose={closeModal}
          setLoading={setLoadingFiles}
        />
      )}
    </>
  );
};

export default StorageBrowserActions;

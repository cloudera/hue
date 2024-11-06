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

import React, { useCallback, useMemo, useState } from 'react';
import { Dropdown } from 'antd';
import { MenuItemType } from 'antd/lib/menu/hooks/useItems';

import Button from 'cuix/dist/components/Button';
import DropDownIcon from '@cloudera/cuix-core/icons/react/DropdownIcon';
import InfoIcon from '@cloudera/cuix-core/icons/react/InfoIcon';
import DuplicateIcon from '@cloudera/cuix-core/icons/react/DuplicateIcon';

import { i18nReact } from '../../../../utils/i18nReact';
import { StorageBrowserTableData } from '../../../../reactComponents/FileChooser/types';
import {
  isHDFS,
  isOFS,
  isABFSRoot,
  isGSRoot,
  isOFSServiceID,
  isOFSVol,
  isS3Root,
  inTrash,
  isABFS,
  isGS,
  isS3,
  isOFSRoot
} from '../../../../utils/storageBrowserUtils';
import {
  RENAME_API_URL,
  SET_REPLICATION_API_URL
} from '../../../../reactComponents/FileChooser/api';
import huePubSub from '../../../../utils/huePubSub';
import useSaveData from '../../../../utils/hooks/useSaveData';

import SummaryModal from '../../SummaryModal/SummaryModal';
import InputModal from '../../InputModal/InputModal';

import './StorageBrowserActions.scss';

interface StorageBrowserRowActionsProps {
  selectedFiles: StorageBrowserTableData[];
  onSuccessfulAction: () => void;
  setLoadingFiles: (value: boolean) => void;
}

const StorageBrowserActions = ({
  selectedFiles,
  onSuccessfulAction
}: StorageBrowserRowActionsProps): JSX.Element => {
  const [showSummaryModal, setShowSummaryModal] = useState<boolean>(false);
  const [showRenameModal, setShowRenameModal] = useState<boolean>(false);
  const [selectedFile, setSelectedFile] = useState<string>('');
  const [showReplicationModal, setShowReplicationModal] = useState<boolean>(false);

  const { t } = i18nReact.useTranslation();

  const { error: renameError, save: saveRename } = useSaveData(RENAME_API_URL);

  const handleRename = (value: string) => {
    saveRename(
      { source_path: selectedFile, destination_path: value },
      {
        onSuccess: () => onSuccessfulAction(),
        onError: () => {
          huePubSub.publish('hue.error', renameError);
        }
      }
    );
  };

  const { error: replicationError, save: saveReplication } = useSaveData(SET_REPLICATION_API_URL);
  const handleReplication = (replicationFactor: number) => {
    saveReplication(
      { path: selectedFile, replication_factor: replicationFactor },
      {
        onSuccess: () => onSuccessfulAction(),
        onError: () => {
          huePubSub.publish('hue.error', replicationError);
        }
      }
    );
  };

  const isSummaryEnabled = useMemo(() => {
    if (selectedFiles.length !== 1) {
      return false;
    }
    const selectedFile = selectedFiles[0];
    return (isHDFS(selectedFile.path) || isOFS(selectedFile.path)) && selectedFile.type === 'file';
  }, [selectedFiles]);

  const isRenameEnabled = useMemo(() => {
    if (selectedFiles.length !== 1) {
      return false;
    }
    const selectedFilePath = selectedFiles[0].path;
    return (
      isHDFS(selectedFilePath) ||
      (isS3(selectedFilePath) && !isS3Root(selectedFilePath)) ||
      (isGS(selectedFilePath) && !isGSRoot(selectedFilePath)) ||
      (isABFS(selectedFilePath) && !isABFSRoot(selectedFilePath)) ||
      (isOFS(selectedFilePath) &&
        !isOFSRoot(selectedFilePath) &&
        !isOFSServiceID(selectedFilePath) &&
        !isOFSVol(selectedFilePath))
    );
  }, [selectedFiles]);

  const isReplicationEnabled = useMemo(() => {
    if (selectedFiles.length !== 1) {
      return false;
    }
    const selectedFile = selectedFiles[0];
    return isHDFS(selectedFile.path) && selectedFile.type === 'file';
  }, [selectedFiles]);

  const getActions = useCallback(() => {
    const actions: MenuItemType[] = [];
    if (selectedFiles && selectedFiles.length > 0 && !inTrash(selectedFiles[0].path)) {
      if (isSummaryEnabled) {
        actions.push({
          key: 'content_summary',
          icon: <InfoIcon />,
          label: t('View Summary'),
          onClick: () => {
            setSelectedFile(selectedFiles[0].path);
            setShowSummaryModal(true);
          }
        });
      }
      if (isRenameEnabled) {
        actions.push({
          key: 'rename',
          icon: <InfoIcon />,
          label: t('Rename'),
          onClick: () => {
            setSelectedFile(selectedFiles[0].path);
            setShowRenameModal(true);
          }
        });
      }
      if (isReplicationEnabled) {
        actions.push({
          key: 'setReplication',
          icon: <DuplicateIcon />,
          label: t('Set Replication'),
          onClick: () => {
            setSelectedFile(selectedFiles[0].path);
            setShowReplicationModal(true);
          }
        });
      }
    }
    return actions;
  }, [selectedFiles, isSummaryEnabled, isRenameEnabled, isReplicationEnabled]);

  return (
    <>
      <Dropdown
        overlayClassName="hue-storage-browser__table-actions-dropdown"
        menu={{
          items: getActions(),
          className: 'hue-storage-browser__table-actions-menu'
        }}
        trigger={['click', 'hover']}
      >
        <Button data-event="">
          {t('Actions')}
          <DropDownIcon />
        </Button>
      </Dropdown>
      <SummaryModal
        showModal={showSummaryModal}
        path={selectedFile}
        onClose={() => setShowSummaryModal(false)}
      />
      <InputModal
        title={t('Rename')}
        inputLabel={t('Enter new name here')}
        submitText={t('Rename')}
        showModal={showRenameModal}
        onSubmit={handleRename}
        onClose={() => setShowRenameModal(false)}
        inputType="text"
        initialValue={selectedFiles[0]?.name}
      />
      <InputModal
        title={'Setting Replication factor for: ' + selectedFile}
        inputLabel={t('Replication factor:')}
        submitText={t('Submit')}
        showModal={showReplicationModal}
        onSubmit={handleReplication}
        onClose={() => setShowReplicationModal(false)}
        inputType="number"
        initialValue={selectedFiles[0]?.replication}
      />
    </>
  );
};

export default StorageBrowserActions;

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
import { MenuItemType } from 'antd/lib/menu/hooks/useItems';

import Button from 'cuix/dist/components/Button';
import DropDownIcon from '@cloudera/cuix-core/icons/react/DropdownIcon';
import InfoIcon from '@cloudera/cuix-core/icons/react/InfoIcon';

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
  isS3
} from '../../../../utils/storageBrowserUtils';
import { rename } from '../../../../reactComponents/FileChooser/api';
import huePubSub from '../../../../utils/huePubSub';

import SummaryModal from '../../SummaryModal/SummaryModal';
import InputModal from '../../InputModal/InputModal';

import './StorageBrowserActions.scss';

interface StorageBrowserRowActionsProps {
  selectedFiles: StorageBrowserTableData[];
  setRefreshKey: (value: number) => void;
  setLoadingFiles: (value: boolean) => void;
}

const StorageBrowserActions = ({
  selectedFiles,
  setLoadingFiles,
  setRefreshKey
}: StorageBrowserRowActionsProps): JSX.Element => {
  const [showSummaryModal, setShowSummaryModal] = useState<boolean>(false);
  const [showRenameModal, setShowRenameModal] = useState<boolean>(false);
  const [selectedFile, setSelectedFile] = useState<string>('');

  const { t } = i18nReact.useTranslation();

  const handleRename = (newName: string) => {
    setLoadingFiles(true);
    rename(selectedFile, newName)
      .then(() => {
        setRefreshKey((oldKey: number) => oldKey + 1);
      })
      .catch(error => {
        huePubSub.publish('hue.error', error);
        setShowRenameModal(false);
      })
      .finally(() => {
        setLoadingFiles(false);
      });
  };

  const isSummaryEnabled = () => {
    const selectedFile = selectedFiles[0];
    return (
      selectedFiles.length == 1 &&
      (isHDFS(selectedFile.path) || isOFS(selectedFile.path)) &&
      selectedFile.type === 'file'
    );
  };

  const isRenameEnabled = () => {
    const selectedFile = selectedFiles[0];
    return (
      selectedFiles.length == 1 &&
      (isHDFS(selectedFile.path) ||
        (isS3(selectedFile.path) && !isS3Root(selectedFile.path)) ||
        (isGS(selectedFile.path) && !isGSRoot(selectedFile.path)) ||
        (isABFS(selectedFile.path) && !isABFSRoot(selectedFile.path)) ||
        (isOFS(selectedFile.path) &&
          !isOFSServiceID(selectedFile.path) &&
          !isOFSVol(selectedFile.path)))
    );
  };

  const getActions = () => {
    const actions: MenuItemType[] = [];
    if (selectedFiles && selectedFiles.length > 0 && !inTrash(selectedFiles[0].path)) {
      if (isSummaryEnabled()) {
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
      if (isRenameEnabled()) {
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
    }
    return actions;
  };

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
      />
    </>
  );
};

export default StorageBrowserActions;

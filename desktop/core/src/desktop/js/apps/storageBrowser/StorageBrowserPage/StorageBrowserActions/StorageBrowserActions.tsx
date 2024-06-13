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
import { isHDFS, isOFS } from '../../../../utils/storageBrowserUtils';

import SummaryModal from '../../SummaryModal/SummaryModal';

import './StorageBrowserActions.scss';

interface StorageBrowserRowActionsProps {
  selectedFiles: StorageBrowserTableData[];
}

const StorageBrowserActions = ({ selectedFiles }: StorageBrowserRowActionsProps): JSX.Element => {
  const [showSummaryModal, setShowSummaryModal] = useState<boolean>(false);
  const [selectedFile, setSelectedFile] = useState<string>('');

  const { t } = i18nReact.useTranslation();

  const isSummaryEnabled = () => {
    return (
      selectedFiles.length == 1 &&
      (isHDFS(selectedFiles[0].path) || isOFS(selectedFiles[0].path)) &&
      selectedFiles[0].type === 'file'
    );
  };

  const getActions = () => {
    const actions: MenuItemType[] = [];
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
        <Button onClick={e => e.stopPropagation()} data-event="">
          Actions
          <DropDownIcon />
        </Button>
      </Dropdown>
      <SummaryModal
        showModal={showSummaryModal}
        path={selectedFile}
        onClose={() => setShowSummaryModal(false)}
      />
    </>
  );
};

export default StorageBrowserActions;

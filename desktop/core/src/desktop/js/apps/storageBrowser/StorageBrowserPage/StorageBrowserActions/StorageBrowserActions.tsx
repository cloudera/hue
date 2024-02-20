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
import { Dropdown, Button } from 'antd';
import type { MenuProps } from 'antd';

import MoreVerticalIcon from '@cloudera/cuix-core/icons/react/MoreVerticalIcon';
import InfoIcon from '@cloudera/cuix-core/icons/react/InfoIcon';
import { i18nReact } from '../../../../utils/i18nReact';
import { StorageBrowserTableData } from '../../../../reactComponents/FileChooser/types';

import './StorageBrowserActions.scss';

interface StorageBrowserActionsProps {
  rowData: StorageBrowserTableData;
  onSelectFile: (path: string) => void;
  onSelectSummary: (showModal: boolean) => void;
}

const StorageBrowserActions: React.FC<StorageBrowserActionsProps> = ({
  rowData,
  onSelectFile,
  onSelectSummary
}): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const isHDFS = () => {
    const currentPath = rowData.path.toLowerCase();
    return currentPath.indexOf('/') === 0 || currentPath.indexOf('hdfs') === 0;
  };

  const isOFS = () => {
    return rowData.path.toLowerCase().indexOf('ofs://') === 0;
  };

  //TODO: handle multiple file selection scenarios
  const isSummaryEnabled = () => {
    if (isHDFS() || isOFS()) {
      if (rowData.type === 'file') {
        return true;
      }
    }
    return false;
  };

  const getActions = () => {
    const actions: MenuProps['items'] = [];
    if (isSummaryEnabled()) {
      actions.push({
        key: 'content_summary',
        icon: <InfoIcon />,
        label: t('View Summary'),
        onClick: () => {
          onSelectFile(rowData.path);
          onSelectSummary(true);
        }
      });
    }
    return actions;
  };

  return (
    <Dropdown
      overlayClassName="hue-storage-browser__table-actions-dropdown"
      menu={{
        items: getActions(),
        className: 'hue-storage-browser__table-actions-menu'
      }}
      trigger={['click', 'hover']}
    >
      <Button onClick={e => e.stopPropagation()} className="hue-storage-browser__table-actions-btn">
        <MoreVerticalIcon />
      </Button>
    </Dropdown>
  );
};

export default StorageBrowserActions;

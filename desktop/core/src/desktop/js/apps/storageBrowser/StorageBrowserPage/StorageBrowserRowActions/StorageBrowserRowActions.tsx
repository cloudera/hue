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
import { Dropdown } from 'antd';
import { MenuItemType } from 'antd/lib/menu/hooks/useItems';

import { BorderlessButton } from 'cuix/dist/components/Button';
import MoreVerticalIcon from '@cloudera/cuix-core/icons/react/MoreVerticalIcon';
import InfoIcon from '@cloudera/cuix-core/icons/react/InfoIcon';

import { i18nReact } from '../../../../utils/i18nReact';
import { StorageBrowserTableData } from '../../../../reactComponents/FileChooser/types';
import { isHDFS, isOFS } from '../../../../../js/utils/storageBrowserUtils';

import './StorageBrowserRowActions.scss';

interface StorageBrowserRowActionsProps {
  rowData: StorageBrowserTableData;
  onViewSummary: (selectedFilePath: string) => void;
}

const StorageBrowserRowActions = ({
  rowData,
  onViewSummary
}: StorageBrowserRowActionsProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  //TODO: handle multiple file selection scenarios
  const isSummaryEnabled = () =>
    (isHDFS(rowData.path) || isOFS(rowData.path)) && rowData.type === 'file';

  const getActions = () => {
    const actions: MenuItemType[] = [];
    if (isSummaryEnabled()) {
      actions.push({
        key: 'content_summary',
        icon: <InfoIcon />,
        label: t('View Summary'),
        onClick: () => {
          onViewSummary(rowData.path);
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
      trigger={['click']}
    >
      <BorderlessButton
        onClick={e => e.stopPropagation()}
        className="hue-storage-browser__table-actions-btn"
        data-event=""
        icon={<MoreVerticalIcon />}
      />
    </Dropdown>
  );
};

export default StorageBrowserRowActions;

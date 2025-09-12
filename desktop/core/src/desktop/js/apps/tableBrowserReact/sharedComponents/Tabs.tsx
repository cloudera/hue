// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// See the NOTICE file distributed with this work for additional information
// regarding copyright ownership. Cloudera, Inc. licenses this file to you under
// the Apache License, Version 2.0 (the "License"); you may not use this file
// except in compliance with the License. You may obtain a copy of the License at
// http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations under
// the License.

import React from 'react';
import { Tabs as AntdTabs } from 'antd';
import type { TabsProps as AntdTabsProps } from 'antd';
import { i18nReact } from '../../../utils/i18nReact';

export type TabKey =
  | 'overview'
  | 'partitions'
  | 'sample'
  | 'queries'
  | 'viewSql'
  | 'details'
  | 'privileges'
  | 'erd';

export interface TabsProps {
  activeKey: TabKey;
  onChange: (nextKey: TabKey) => void;
  sampleCount?: number;
  partitionsCount?: number;
  showQueries?: boolean;
  showViewSql?: boolean;
  showErd?: boolean;
  showPartitions?: boolean;
}

const Tabs = ({
  activeKey,
  onChange,
  sampleCount,
  partitionsCount,
  showQueries,
  showViewSql,
  showErd,
  showPartitions = true
}: TabsProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const items: NonNullable<AntdTabsProps['items']> = [
    { key: 'overview', label: t('Overview') },
    ...(showPartitions
      ? [
          {
            key: 'partitions',
            label: `${t('Partitions')}${partitionsCount ? ` (${partitionsCount})` : ''}`
          }
        ]
      : []),
    { key: 'sample', label: `${t('Sample')}${sampleCount ? ` (${sampleCount})` : ''}` },
    ...(showQueries ? [{ key: 'queries', label: t('Queries') }] : []),
    ...(showViewSql ? [{ key: 'viewSql', label: t('View SQL') }] : []),
    { key: 'details', label: t('Details') },
    { key: 'privileges', label: t('Privileges') },
    ...(showErd ? [{ key: 'erd', label: t('ERD') }] : [])
  ];

  return <AntdTabs activeKey={activeKey} onChange={key => onChange(key as TabKey)} items={items} />;
};

export default Tabs;

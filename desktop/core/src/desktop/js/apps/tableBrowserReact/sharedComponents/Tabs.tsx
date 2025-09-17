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

import React, { useEffect, useMemo, useState } from 'react';
import { Tabs as AntdTabs } from 'antd';
import type { TabsProps as AntdTabsProps } from 'antd';
import { i18nReact } from '../../../utils/i18nReact';
import './Tabs.scss';

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

const TableBrowserTabs = ({
  activeKey,
  onChange,
  sampleCount,
  partitionsCount,
  showQueries,
  showViewSql,
  showErd,
  showPartitions = true
}: TabsProps): React.ReactElement | null => {
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

  // Debounced remount key to coalesce multiple label updates into a single recalculation
  const rawKey = useMemo(
    () =>
      JSON.stringify({
        sampleCount: sampleCount ?? 0,
        partitionsCount: partitionsCount ?? 0,
        showQueries: !!showQueries,
        showViewSql: !!showViewSql,
        showErd: !!showErd,
        showPartitions: !!showPartitions
      }),
    [sampleCount, partitionsCount, showQueries, showViewSql, showErd, showPartitions]
  );
  const [tabsKey, setTabsKey] = useState<string>(rawKey);
  useEffect(() => {
    const timeout = window.setTimeout(() => setTabsKey(rawKey), 120);
    return () => window.clearTimeout(timeout);
  }, [rawKey]);

  // Suppress ink bar animation until labels stabilize after initial load
  const [suppressInkAnim, setSuppressInkAnim] = useState<boolean>(true);
  useEffect(() => {
    setSuppressInkAnim(true);
    const timeout = window.setTimeout(() => setSuppressInkAnim(false), 220);
    return () => window.clearTimeout(timeout);
  }, [rawKey]);

  return (
    <AntdTabs
      key={tabsKey}
      className={suppressInkAnim ? 'hue-tabs hue-tabs--no-ink-anim' : 'hue-tabs'}
      activeKey={activeKey}
      onChange={(key: string) => onChange(key as TabKey)}
      items={items}
    />
  );
};

export default TableBrowserTabs;

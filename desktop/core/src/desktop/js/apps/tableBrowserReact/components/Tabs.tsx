// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React from 'react';
import { Tabs as AntdTabs } from 'antd';
import { i18nReact } from '../../../utils/i18nReact';

export type TabKey = 'overview' | 'partitions' | 'sample' | 'queries' | 'viewSql' | 'details' | 'privileges' | 'erd';

export interface TabsProps {
  activeKey: TabKey;
  onChange: (nextKey: TabKey) => void;
  sampleCount?: number;
  showQueries?: boolean;
  showViewSql?: boolean;
  showErd?: boolean;
}

const Tabs = ({ activeKey, onChange, sampleCount, showQueries, showViewSql, showErd }: TabsProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const items = [
    { key: 'overview', label: t('Overview') },
    { key: 'partitions', label: t('Partitions') },
    { key: 'sample', label: `${t('Sample')}${sampleCount ? ` (${sampleCount})` : ''}` },
    ...(showQueries ? [{ key: 'queries', label: t('Queries') }] : []),
    ...(showViewSql ? [{ key: 'viewSql', label: t('View SQL') }] : []),
    { key: 'details', label: t('Details') },
    { key: 'privileges', label: t('Privileges') },
    ...(showErd ? [{ key: 'erd', label: 'ERD' }] : [])
  ];

  return <AntdTabs activeKey={activeKey} onChange={key => onChange(key as TabKey)} items={items as any} />;
};

export default Tabs;



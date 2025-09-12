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

import React, { useState } from 'react';
import { LinkButton } from 'cuix/dist/components/Button/';
import Loading from 'cuix/dist/components/Loading';
import EmptyState from 'cuix/dist/components/EmptyState';
import Filter from 'cuix/dist/components/Filter';
import HomeIcon from '@cloudera/cuix-core/icons/react/HomeIcon';
import PageHeader from './PageHeader';
import PaginatedTable, {
  type ColumnProps as PaginatedColumnProps
} from '../../../reactComponents/PaginatedTable/PaginatedTable';
import type { FilterOutput } from 'cuix/dist/components/Filter/types';
import type { SortOrder } from 'antd/lib/table/interface';
import { i18nReact } from '../../../utils/i18nReact';

export interface SourcesListProps {
  sources: string[];
  loading: boolean;
  isRefreshing: boolean;
  onRefresh?: () => void;
  sourceFilter: string;
  setSourceFilter: (value: string) => void;
  sourcePageNumber: number;
  setSourcePageNumber: (num: number) => void;
  sourcePageSize: number;
  setSourcePageSize: (size: number) => void;
  onOpenSource: (sourceType: string) => void;
  // Breadcrumbs props
  sourceType?: string;
  database?: string;
  table?: string;
  sourceOptions?: string[];
  onSelectSource?: (sourceType: string) => void;
  onClickDataSources?: () => void;
  onClickDatabases?: () => void;
  onClickDatabase?: (database: string) => void;
}

const SourcesList = ({
  sources,
  loading,
  isRefreshing,
  onRefresh,
  sourceFilter,
  setSourceFilter,
  sourcePageNumber,
  setSourcePageNumber,
  sourcePageSize,
  setSourcePageSize,
  onOpenSource,
  sourceType,
  database,
  table,
  sourceOptions,
  onSelectSource,
  onClickDataSources,
  onClickDatabases,
  onClickDatabase
}: SourcesListProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [sortByColumn, setSortByColumn] = useState<string | undefined>(undefined);
  const [sortOrder, setSortOrder] = useState<SortOrder>(null);

  const filtered = sources.filter(src =>
    sourceFilter ? src.toLowerCase().includes(sourceFilter.toLowerCase()) : true
  );

  const columns: PaginatedColumnProps<{ name: string }>[] = [
    {
      title: t('Source'),
      dataIndex: 'name',
      key: 'name',
      sorter: true,
      render: (text: string, record: { name: string }) => (
        <LinkButton aria-label={t('Open source')} onClick={() => onOpenSource(record.name)}>
          {text}
        </LinkButton>
      )
    }
  ];

  // Apply sorting
  const sorted = [...filtered].sort((a, b) => {
    if (!sortOrder || !sortByColumn) {
      return 0;
    }

    const aValue = a.toLowerCase();
    const bValue = b.toLowerCase();

    const comparison = aValue.localeCompare(bValue);
    return sortOrder === 'ascend' ? comparison : -comparison;
  });

  const data = sorted.map(name => ({ key: name, name }));
  const totalSize = data.length;
  const totalPages = Math.max(Math.ceil(totalSize / sourcePageSize), 1);
  const start = (sourcePageNumber - 1) * sourcePageSize;
  const pageData = data.slice(start, start + sourcePageSize);

  return (
    <div>
      <PageHeader
        title={t('Home')}
        icon={<HomeIcon />}
        onRefresh={onRefresh}
        loading={loading}
        isRefreshing={isRefreshing}
        sourceType={sourceType}
        database={database}
        table={table}
        sourceOptions={sourceOptions}
        onSelectSource={onSelectSource}
        onClickDataSources={onClickDataSources}
        onClickDatabases={onClickDatabases}
        onClickDatabase={onClickDatabase}
      />

      <div className="hue-table-browser__header-with-actions">
        <h3 className="hue-h3">
          {t('{{label}} ({{count}})', {
            label: t('Data sources'),
            count: totalSize
          })}
        </h3>
      </div>

      <Loading spinning={!!loading || isRefreshing}>
        <div className="hue-table-browser__filter">
          <Filter
            search={{ placeholder: t('Filter sources') }}
            onChange={(output: FilterOutput) => {
              const searchValue = String(
                (output as unknown as { search?: unknown[] }).search?.[0] ?? ''
              );
              if (searchValue !== sourceFilter) {
                setSourceFilter(searchValue);
              }
            }}
          />
        </div>
        {!loading && filtered.length === 0 ? (
          <EmptyState className="hue-table-browser__empty-state" title={t('No sources')} />
        ) : (
          <PaginatedTable<{ name: string }>
            data={pageData}
            columns={columns}
            rowKey="key"
            sortByColumn={sortByColumn}
            sortOrder={sortOrder}
            setSortByColumn={column => setSortByColumn(String(column))}
            setSortOrder={setSortOrder}
            pagination={{
              pageStats: {
                pageNumber: sourcePageNumber,
                totalPages,
                pageSize: sourcePageSize,
                totalSize
              },
              setPageNumber: setSourcePageNumber,
              setPageSize: setSourcePageSize
            }}
          />
        )}
      </Loading>
    </div>
  );
};

export default SourcesList;

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
import { LinkButton } from 'cuix/dist/components/Button/';
import Loading from 'cuix/dist/components/Loading';
import EmptyState from 'cuix/dist/components/EmptyState';
import Filter from 'cuix/dist/components/Filter';
import PaginatedTable, {
  type ColumnProps as PaginatedColumnProps
} from '../../../reactComponents/PaginatedTable/PaginatedTable';
import type { FilterOutput } from 'cuix/dist/components/Filter/types';
import { i18nReact } from '../../../utils/i18nReact';

export interface SourcesListProps {
  sources: string[];
  loading: boolean;
  isRefreshing: boolean;
  sourceFilter: string;
  setSourceFilter: (value: string) => void;
  sourcePageNumber: number;
  setSourcePageNumber: (num: number) => void;
  sourcePageSize: number;
  setSourcePageSize: (size: number) => void;
  onOpenSource: (sourceType: string) => void;
}

const SourcesList = ({
  sources,
  loading,
  isRefreshing,
  sourceFilter,
  setSourceFilter,
  sourcePageNumber,
  setSourcePageNumber,
  sourcePageSize,
  setSourcePageSize,
  onOpenSource
}: SourcesListProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const filtered = sources.filter(src =>
    sourceFilter ? src.toLowerCase().includes(sourceFilter.toLowerCase()) : true
  );

  const columns: PaginatedColumnProps<{ name: string }>[] = [
    {
      title: t('Source'),
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: { name: string }) => (
        <LinkButton aria-label={t('Open source')} onClick={() => onOpenSource(record.name)}>
          {text.toUpperCase()}
        </LinkButton>
      )
    }
  ];

  const data = filtered.map(name => ({ key: name, name }));
  const totalSize = data.length;
  const totalPages = Math.max(Math.ceil(totalSize / sourcePageSize), 1);
  const start = (sourcePageNumber - 1) * sourcePageSize;
  const pageData = data.slice(start, start + sourcePageSize);

  return (
    <div>
      <h2 className="hue-table-browser__heading">
        {t('{{label}} ({{count}})', {
          label: t('Data sources'),
          count: totalSize
        })}
      </h2>
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

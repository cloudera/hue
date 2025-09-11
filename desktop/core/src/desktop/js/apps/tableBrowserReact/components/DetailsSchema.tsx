// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React, { useMemo, useState } from 'react';
import Filter from 'cuix/dist/components/Filter';
import PaginatedTable, {
  type ColumnProps as PaginatedColumnProps
} from '../../../reactComponents/PaginatedTable/PaginatedTable';
import type { FilterOutput } from 'cuix/dist/components/Filter/types';
import { i18nReact } from '../../../utils/i18nReact';

export interface ColumnDef {
  name: string;
  type: string;
  comment?: string;
  sample?: string;
}

export interface DetailsSchemaProps {
  columns: ColumnDef[];
}

const DetailsSchema = ({ columns }: DetailsSchemaProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [filter, setFilter] = useState('');
  const [pageNumber, setPageNumber] = useState(1);
  const [pageSize, setPageSize] = useState(25);

  const filtered = useMemo(() => {
    if (!filter) {
      return columns;
    }
    const q = filter.toLowerCase();
    return columns.filter(
      c => c.name.toLowerCase().includes(q) || (c.comment || '').toLowerCase().includes(q)
    );
  }, [columns, filter]);

  const data = filtered.map(col => ({ key: col.name, ...col }));
  const totalSize = data.length;
  const totalPages = Math.max(Math.ceil(totalSize / pageSize), 1);
  const start = (pageNumber - 1) * pageSize;
  const pageData = data.slice(start, start + pageSize);

  const columnsDef: PaginatedColumnProps<ColumnDef & { key: string }>[] = [
    { title: t('Column'), dataIndex: 'name', key: 'name' },
    { title: t('Type'), dataIndex: 'type', key: 'type' },
    { title: t('Description'), dataIndex: 'comment', key: 'comment' },
    { title: t('Sample'), dataIndex: 'sample', key: 'sample' }
  ];

  return (
    <div>
      <div className="hue-table-browser__filter">
        <Filter
          search={{ placeholder: t('Filter columns') }}
          onChange={(output: FilterOutput) => {
            const searchValue = String(
              (output as unknown as { search?: unknown[] }).search?.[0] ?? ''
            );
            if (searchValue !== filter) {
              setFilter(searchValue);
              setPageNumber(1);
            }
          }}
        />
      </div>
      <PaginatedTable<ColumnDef & { key: string }>
        data={pageData}
        columns={columnsDef}
        rowKey="key"
        pagination={{
          pageStats: {
            pageNumber,
            totalPages,
            pageSize,
            totalSize
          },
          setPageNumber,
          setPageSize
        }}
      />
    </div>
  );
};

export default DetailsSchema;

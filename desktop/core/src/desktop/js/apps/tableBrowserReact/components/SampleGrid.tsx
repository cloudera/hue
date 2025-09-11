// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React, { useMemo, useState, useEffect } from 'react';
import EmptyState from 'cuix/dist/components/EmptyState';
import { i18nReact } from '../../../utils/i18nReact';
import PaginatedTable, {
  type ColumnProps as PaginatedColumnProps
} from '../../../reactComponents/PaginatedTable/PaginatedTable';

export interface SampleData {
  headers: string[];
  rows: (string | number | null)[][];
}

export interface SampleGridProps {
  data?: SampleData;
  loading?: boolean;
}

const SampleGrid = ({ data, loading }: SampleGridProps): JSX.Element => {
  const [pageSize, setPageSize] = useState(100);
  const [pageNumber, setPageNumber] = useState(1);

  const totalSize = data?.rows?.length || 0;
  const totalPages = Math.max(Math.ceil(totalSize / pageSize), 1);

  useEffect(() => {
    setPageNumber(1);
  }, [pageSize, totalSize]);

  const columns: PaginatedColumnProps<Record<string, unknown>>[] = useMemo(
    () => (data?.headers || []).map(h => ({ title: h, dataIndex: h, key: h })),
    [data?.headers]
  );

  const datasource: Record<string, unknown>[] = useMemo(() => {
    const all = (data?.rows || []).map((row, idx) => {
      const obj: Record<string, unknown> = { key: String(idx) };
      (data?.headers || []).forEach((h, i) => {
        obj[h] = row[i];
      });
      return obj;
    });
    const startIdx = (pageNumber - 1) * pageSize;
    return all.slice(startIdx, startIdx + pageSize);
  }, [data?.rows, data?.headers, pageNumber, pageSize]);

  const { t } = i18nReact.useTranslation();

  if (!loading && (!data || !data.headers || data.headers.length === 0)) {
    return <EmptyState title={t('No data')} />;
  }

  return (
    <PaginatedTable<Record<string, unknown>>
      loading={!!loading}
      data={datasource}
      columns={columns}
      rowKey="key"
      isDynamicHeight
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
  );
};

export default SampleGrid;

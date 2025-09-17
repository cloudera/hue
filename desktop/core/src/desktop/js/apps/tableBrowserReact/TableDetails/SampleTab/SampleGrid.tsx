// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React, { useMemo, useState, useEffect } from 'react';
import decodeHtmlEntities from '../../../../utils/strings/decodeHtmlEntities';
import EmptyState from 'cuix/dist/components/EmptyState';
import { i18nReact } from '../../../../utils/i18nReact';
import PaginatedTable, {
  type ColumnProps as PaginatedColumnProps
} from '../../../../reactComponents/PaginatedTable/PaginatedTable';

export interface SampleData {
  headers: string[];
  rows: (string | number | null)[][];
}

export interface SampleGridProps {
  data?: SampleData;
  isRefreshing?: boolean;
  database?: string;
  table?: string;
}

const SampleGrid = ({ data, isRefreshing, database, table }: SampleGridProps): JSX.Element => {
  const [pageSize, setPageSize] = useState(100);
  const [pageNumber, setPageNumber] = useState(1);

  const totalSize = data?.rows?.length || 0;
  const totalPages = Math.max(Math.ceil(totalSize / pageSize), 1);

  useEffect(() => {
    setPageNumber(1);
  }, [pageSize, totalSize]);

  const columns: PaginatedColumnProps<Record<string, unknown>>[] = useMemo(
    () =>
      (data?.headers || []).map(h => {
        let title = h;
        // Prefer removing the longer "database.table." prefix if present
        if (database && table) {
          const dbTablePrefix = `${database}.${table}.`;
          if (title.startsWith(dbTablePrefix)) {
            title = title.substring(dbTablePrefix.length);
          }
        }
        // Fallback: remove just "table." prefix if present
        if (table) {
          const tablePrefix = `${table}.`;
          if (title.startsWith(tablePrefix)) {
            title = title.substring(tablePrefix.length);
          }
        }
        return { title, dataIndex: h, key: h };
      }),
    [data?.headers, database, table]
  );

  const datasource: Record<string, unknown>[] = useMemo(() => {
    const all = (data?.rows || []).map((row, idx) => {
      const obj: Record<string, unknown> = { key: String(idx) };
      (data?.headers || []).forEach((h, i) => {
        // Backend is encoding HTML entities in the sample data, so we need to decode them
        obj[h] = decodeHtmlEntities(row[i]);
      });
      return obj;
    });
    const startIdx = (pageNumber - 1) * pageSize;
    return all.slice(startIdx, startIdx + pageSize);
  }, [data?.rows, data?.headers, pageNumber, pageSize]);

  const { t } = i18nReact.useTranslation();

  if (!isRefreshing && (!data || !data.headers || data.headers.length === 0)) {
    return (
      <EmptyState
        title={t('No sample data')}
        subtitle={t('The table may be empty or sampling is unavailable. Try refreshing.')}
      />
    );
  }

  return (
    <PaginatedTable<Record<string, unknown>>
      enableHorizontalScroll
      loading={!!isRefreshing}
      data={datasource}
      columns={columns}
      locale={{ emptyText: t('No sample data') }}
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
  );
};

export default SampleGrid;

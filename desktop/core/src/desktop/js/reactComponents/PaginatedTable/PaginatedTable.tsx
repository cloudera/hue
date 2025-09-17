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

import React, { HTMLAttributes, useEffect, useRef, useState } from 'react';
import Table, { type ColumnProps } from 'cuix/dist/components/Table';
import { TablePaginationConfig } from 'antd/es/table';
import {
  TableLocale,
  RowSelectionType,
  FilterValue,
  SorterResult,
  SortOrder
} from 'antd/lib/table/interface';
import { PanelRender } from 'rc-table/lib/interface';
import Pagination, { PaginationProps } from '../Pagination/Pagination';
import useResizeObserver from '../../utils/hooks/useResizeObserver/useResizeObserver';

import './PaginatedTable.scss';

export interface PaginatedTableProps<T> {
  title?: PanelRender<T>;
  data: T[];
  columns: ColumnProps<T>[];
  onRowClick?: (record: T) => HTMLAttributes<HTMLElement>;
  locale?: TableLocale;
  onRowSelect?: (selectedRows: T[]) => void;
  showHeader?: boolean;
  isDynamicHeight?: boolean;
  // When true, enables horizontal scrolling and prevents cell text from wrapping
  enableHorizontalScroll?: boolean;
  sortByColumn?: ColumnProps<T>['dataIndex'];
  sortOrder?: SortOrder;
  setSortByColumn?: (column: ColumnProps<T>['dataIndex']) => void;
  setSortOrder?: (order: SortOrder) => void;
  testId?: string;
  rowKey: ((record: T) => string) | string;
  pagination?: Partial<PaginationProps>;
  rowClassName?: ((record: T) => string) | string;
  loading?: boolean;
}

const TABLE_HEADER_HEIGHT = 47;
const PAGINATION_HEIGHT = 50;

const PaginatedTable = <T extends object>({
  loading = false,
  title,
  data,
  columns,
  onRowClick,
  onRowSelect,
  isDynamicHeight = false,
  enableHorizontalScroll = false,
  sortByColumn,
  sortOrder,
  setSortByColumn,
  setSortOrder,
  pagination,
  testId,
  locale,
  rowKey,
  rowClassName,
  showHeader = true
}: PaginatedTableProps<T>): JSX.Element => {
  const [headerWidths, setHeaderWidths] = useState<Record<string, number>>({});
  const headerRefs = useRef<Record<string, HTMLTableCellElement | null>>({});
  const canvasCtxRef = useRef<CanvasRenderingContext2D | null>(null);

  const measureTextWidth = (text: string): number => {
    if (!canvasCtxRef.current) {
      const canvas = document.createElement('canvas');
      canvasCtxRef.current = canvas.getContext('2d');
      if (canvasCtxRef.current) {
        try {
          const bodyStyles = window.getComputedStyle(document.body);
          const fontSize = bodyStyles.fontSize || '14px';
          const fontFamily = bodyStyles.fontFamily || 'Arial, sans-serif';
          canvasCtxRef.current.font = `${fontSize} ${fontFamily}`;
        } catch {
          // Fallback font
          canvasCtxRef.current.font = '14px Arial, sans-serif';
        }
      }
    }
    const ctx = canvasCtxRef.current;
    if (!ctx) {
      return Math.max(40, text.length * 8);
    }
    return Math.max(40, ctx.measureText(text).width);
  };
  const rowSelection = onRowSelect
    ? {
        hideSelectAll: !data.length,
        columnWidth: 36,
        type: 'checkbox' as RowSelectionType,
        onChange: (_: React.Key[], selectedRows: T[]) => {
          onRowSelect(selectedRows);
        }
      }
    : undefined;

  const onColumnClick = (
    _: TablePaginationConfig,
    __: Record<string, FilterValue | null>,
    sorter: SorterResult<T> | SorterResult<T>[]
  ) => {
    if (setSortOrder && setSortByColumn) {
      const sorterObj = sorter && Array.isArray(sorter) ? sorter[0] : sorter;
      if (sorterObj?.order) {
        setSortOrder(sorterObj.order);
        setSortByColumn(sorterObj.columnKey);
      } else {
        setSortOrder(null);
        setSortByColumn(undefined);
      }
    }
  };

  const getColumnsFromConfig = (columnsConfig: ColumnProps<T>[]) => {
    return columnsConfig.map(col => {
      const key = String(
        (col as unknown as { key?: React.Key }).key ?? (col.dataIndex as React.Key)
      );
      const enhanced: Record<string, unknown> = {
        ...col,
        defaultSortOrder: sortByColumn === col.dataIndex ? sortOrder : undefined,
        showSorterTooltip: false
      };

      if (enableHorizontalScroll) {
        // Attach a ref to measure header title width
        type HeaderCellAttr = React.HTMLAttributes<HTMLTableCellElement> & {
          ref?: (el: HTMLTableCellElement | null) => void;
        };
        (enhanced as ColumnProps<T>).onHeaderCell = () =>
          ({
            ref: (el: HTMLTableCellElement | null) => {
              if (el) {
                headerRefs.current[key] = el;
              }
            },
            style: {
              whiteSpace: 'nowrap',
              minWidth: headerWidths[key] ? Math.ceil(headerWidths[key]) : undefined,
              width: headerWidths[key] ? Math.ceil(headerWidths[key]) : undefined,
              maxWidth: headerWidths[key] ? Math.ceil(headerWidths[key]) : undefined
            }
          }) as unknown as HeaderCellAttr;

        // Enforce shared min width via column width when known (keeps header/body in sync)
        const measured = headerWidths[key];
        const titleText =
          typeof (col as unknown as { title?: unknown }).title === 'string'
            ? ((col as unknown as { title?: string }).title as string)
            : typeof col.dataIndex === 'string'
              ? (col.dataIndex as string)
              : '';
        const approxHeaderWidth = Math.ceil(measureTextWidth(titleText)) + 32; // padding safety

        // Also consider max value width so long values don't overflow
        let maxValueWidth = 0;
        const di = col.dataIndex as unknown;
        const canRead = typeof di === 'string' || typeof di === 'number';
        if (canRead) {
          const maxRowsToMeasure = Math.min(data.length, 200);
          for (let i = 0; i < maxRowsToMeasure; i++) {
            const record = data[i] as unknown as Record<string | number, unknown>;
            const raw = record?.[di as string | number];
            const txt = raw == null ? '' : String(raw);
            if (txt) {
              const w = Math.ceil(measureTextWidth(txt)) + 24; // padding safety
              if (w > maxValueWidth) {
                maxValueWidth = w;
              }
            }
          }
        }

        const target = Math.max(
          typeof measured === 'number' && !Number.isNaN(measured) ? Math.ceil(measured) : 0,
          approxHeaderWidth,
          maxValueWidth
        );
        const existingWidth = (col as unknown as { width?: number | string }).width;
        const existingAsNum = typeof existingWidth === 'number' ? existingWidth : 0;
        const finalWidth = Math.max(existingAsNum, target);
        (enhanced as ColumnProps<T>).width = finalWidth;
        // Also enforce min/explicit width on body cells to keep in sync with header
        (enhanced as ColumnProps<T>).onCell = () => ({
          style: {
            minWidth: finalWidth,
            width: finalWidth,
            maxWidth: finalWidth
          }
        });
      }

      return enhanced as ColumnProps<T>;
    });
  };

  // Show pagination if there are multiple pages OR if the user selected a page size
  // larger than the smallest available option (so they can change it back), as requested.
  const smallestPageSizeOption = pagination?.pageSizeOptions?.[0] ?? 25;
  const isNonMinimumSelected =
    typeof pagination?.pageStats?.pageSize === 'number' &&
    pagination?.pageStats?.pageSize > smallestPageSizeOption;

  const isPaginationEnabled =
    !!pagination?.pageStats &&
    !!pagination.setPageNumber &&
    (pagination?.pageStats?.totalPages > 1 || isNonMinimumSelected);

  const [tableRef, rect] = useResizeObserver();

  const headerHeight = showHeader ? TABLE_HEADER_HEIGHT : 0;
  const paginationHeight = isPaginationEnabled ? PAGINATION_HEIGHT : 0;
  const tableOffset = headerHeight + paginationHeight;
  const tableBodyHeight = Math.max(rect.height - tableOffset, 100);

  // Compose scroll options based on props
  let tableScroll: { x?: string | number | true; y?: number } | undefined;
  if (enableHorizontalScroll || isDynamicHeight) {
    tableScroll = {};
    if (enableHorizontalScroll) {
      tableScroll.x = 'max-content';
    }
    if (isDynamicHeight) {
      tableScroll.y = tableBodyHeight;
    }
  }

  // Measure header title widths when horizontal scroll is enabled
  useEffect(() => {
    if (!enableHorizontalScroll) {
      return;
    }

    const next: Record<string, number> = {};
    Object.keys(headerRefs.current).forEach(key => {
      const el = headerRefs.current[key];
      if (!el) {
        return;
      }
      const titleEl = (el.querySelector('.ant-table-column-title') || el) as HTMLElement;
      const rect = titleEl.getBoundingClientRect();
      const styles = window.getComputedStyle(el);
      const paddingLeft = parseFloat(styles.paddingLeft || '0');
      const paddingRight = parseFloat(styles.paddingRight || '0');
      const extra = Math.ceil(paddingLeft + paddingRight) + 16; // safety padding
      const width = Math.ceil(rect.width + extra);
      if (width > 0) {
        next[key] = width;
      }
    });

    // Only update when something actually changed to avoid loops
    const changed = Object.keys(next).some(k => headerWidths[k] !== next[k]);
    if (changed) {
      setHeaderWidths(prev => ({ ...prev, ...next }));
    }
  }, [enableHorizontalScroll, rect.width, rect.height, columns]);

  const mergedOnRow = onRowClick
    ? (record: T) => {
        const attrs = onRowClick(record) || {};
        const originalOnKeyDown = (attrs as HTMLAttributes<HTMLElement>).onKeyDown;
        const originalOnClick = (attrs as HTMLAttributes<HTMLElement>).onClick;
        return {
          tabIndex: 0,
          ...attrs,
          onKeyDown: (e: React.KeyboardEvent<HTMLElement>) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              originalOnClick && originalOnClick(e as unknown as React.MouseEvent<HTMLElement>);
            }
            originalOnKeyDown && originalOnKeyDown(e);
          }
        } as HTMLAttributes<HTMLElement>;
      }
    : undefined;

  return (
    <div
      ref={tableRef}
      className={`hue-paginated-table-container ${enableHorizontalScroll ? 'hue-paginated-table-container--hscroll' : ''} ${loading ? 'hue-paginated-table-container__placeholder--hidden' : ''}`}
    >
      <Table
        title={title}
        className={`hue-paginated-table ${enableHorizontalScroll ? 'hue-paginated-table--nowrap' : ''}`}
        onChange={onColumnClick}
        columns={getColumnsFromConfig(columns)}
        dataSource={data}
        onRow={mergedOnRow as unknown as (record: T, index?: number) => HTMLAttributes<HTMLElement>}
        pagination={false}
        tableLayout={enableHorizontalScroll ? 'auto' : undefined}
        rowClassName={rowClassName}
        rowKey={rowKey}
        rowSelection={rowSelection}
        scroll={tableScroll}
        data-testid={testId}
        locale={loading ? { ...(locale || {}), emptyText: '' } : locale}
        loading={loading}
        sticky
        showHeader={showHeader}
      />
      {isPaginationEnabled && (
        <Pagination
          setPageSize={pagination.setPageSize}
          pageSize={pagination.pageSize}
          setPageNumber={pagination.setPageNumber!}
          pageStats={pagination.pageStats!}
        />
      )}
    </div>
  );
};

export default PaginatedTable;
export { ColumnProps, TableLocale, RowSelectionType, SortOrder };

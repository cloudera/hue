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

import React, { HTMLAttributes } from 'react';
import Table, { type ColumnProps } from 'cuix/dist/components/Table';
import {
  TableLocale,
  RowSelectionType,
  FilterValue,
  SorterResult,
  SortOrder
} from 'antd/lib/table/interface';
import { PanelRender } from 'rc-table/lib/interface';
import type { TableProps } from 'rc-table/lib/Table';
import Pagination, { PaginationProps } from '../Pagination/Pagination';

import './PaginatedTable.scss';
import { TablePaginationConfig } from 'antd/es/table';

export interface PaginatedTableProps<T> {
  title?: PanelRender<T>;
  data: T[];
  columns: ColumnProps<T>[];
  onRowClick?: (record: T) => HTMLAttributes<HTMLElement>;
  locale?: TableLocale;
  onRowSelect?: (selectedRows: T[]) => void;
  scroll?: TableProps<T>['scroll'];
  sortByColumn?: ColumnProps<T>['dataIndex'];
  sortOrder?: SortOrder;
  setSortByColumn?: (column: ColumnProps<T>['dataIndex']) => void;
  setSortOrder?: (order: SortOrder) => void;
  testId?: string;
  rowKey: ((record: T) => string) | string;
  pagination?: Partial<PaginationProps>;
  rowClassName?: ((record: T) => string) | string;
}

const PaginatedTable = <T extends object>({
  title,
  data,
  columns,
  onRowClick,
  onRowSelect,
  scroll,
  sortByColumn,
  sortOrder,
  setSortByColumn,
  setSortOrder,
  pagination,
  testId,
  locale,
  rowKey,
  rowClassName
}: PaginatedTableProps<T>): JSX.Element => {
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
    return columnsConfig.map(col => ({
      ...col,
      defaultSortOrder: sortByColumn === col.dataIndex ? sortOrder : undefined
    }));
  };

  return (
    <>
      <Table
        title={title}
        className="hue-table"
        onChange={onColumnClick}
        columns={getColumnsFromConfig(columns)}
        dataSource={data}
        onRow={onRowClick}
        pagination={false}
        rowClassName={rowClassName}
        rowKey={rowKey}
        rowSelection={rowSelection}
        scroll={scroll}
        data-testid={testId}
        locale={locale}
        sticky
      />
      {pagination?.pageStats &&
        pagination?.pageStats?.totalPages > 0 &&
        pagination.setPageNumber && (
          <Pagination
            setPageSize={pagination.setPageSize}
            pageSize={pagination.pageSize}
            setPageNumber={pagination.setPageNumber}
            pageStats={pagination?.pageStats}
          />
        )}
    </>
  );
};

export default PaginatedTable;
export { ColumnProps, TableLocale, RowSelectionType, SortOrder };

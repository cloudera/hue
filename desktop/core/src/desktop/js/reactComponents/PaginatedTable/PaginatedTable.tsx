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
import { TableLocale, RowSelectionType } from 'antd/lib/table/interface';
import { PanelRender } from 'rc-table/lib/interface';
import type { TableProps as RcTableProps } from 'rc-table/lib/Table';
import SortDescendingIcon from '@cloudera/cuix-core/icons/react/SortDescendingIcon';
import SortAscendingIcon from '@cloudera/cuix-core/icons/react/SortAscendingIcon';
import Pagination, { PaginationProps } from '../Pagination/Pagination';

import './Table.scss';

enum SortOrder {
  ASC = 'ascending',
  DSC = 'descending',
  NONE = 'none'
}

export interface TableProps<T> {
  title?: PanelRender<T>;
  data: T[];
  columns: ColumnProps<T>[];
  onRowClick?: (record: T) => HTMLAttributes<HTMLElement>;
  locale?: TableLocale;
  onRowSelect?: (selectedRows: T[]) => void;
  scroll?: RcTableProps<T>['scroll'];
  sortByColumn?: ColumnProps<T>['dataIndex'];
  sortOrder?: SortOrder;
  setSortByColumn?: (column: ColumnProps<T>['dataIndex']) => void;
  setSortOrder?: (order: SortOrder) => void;
  testId?: string;
  rowKey: ((record: T) => string) | string;
  pagination?: PaginationProps;
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
}: TableProps<T>): JSX.Element => {
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

  const onColumnClick = (columnClicked: ColumnProps<T>['dataIndex']) => {
    const isSortable = columns.find(col => col.dataIndex === columnClicked)?.sorter;
    if (!isSortable || !setSortByColumn || !setSortOrder) {
      return;
    }

    if (columnClicked === sortByColumn) {
      const nextOrder = {
        [SortOrder.NONE]: SortOrder.ASC,
        [SortOrder.ASC]: SortOrder.DSC,
        [SortOrder.DSC]: SortOrder.NONE
      }[sortOrder as SortOrder];
      setSortOrder(nextOrder);
      if (nextOrder === SortOrder.NONE) {
        setSortByColumn(undefined);
      }
    } else {
      setSortByColumn(columnClicked);
      setSortOrder(SortOrder.ASC);
    }
  };

  const getColumnsFromConfig = (columnsConfig: ColumnProps<T>[]) => {
    return columnsConfig.map(col => ({
      ...col,
      sorter: false, // we have custom sorter
      title: (
        <div
          className={`hue-table__header ${col.sorter ? 'hue-table__header--cursor-pointer' : ''}`}
          onClick={() => {
            if (col.sorter) {
              onColumnClick(col.dataIndex);
            }
          }}
        >
          {typeof col.title === 'function' ? col.title({}) : col.title}
          {col.dataIndex === sortByColumn && (
            <>
              {sortOrder === SortOrder.DSC && <SortDescendingIcon />}
              {sortOrder === SortOrder.ASC && <SortAscendingIcon />}
            </>
          )}
        </div>
      )
    }));
  };

  return (
    <>
      <Table
        title={title}
        className="hue-table"
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
      {pagination?.pageStats && pagination?.pageStats?.totalPages > 0 && (
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

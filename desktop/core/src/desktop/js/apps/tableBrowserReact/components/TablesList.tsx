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

import React, { useMemo, useState } from 'react';
import { Input, Skeleton } from 'antd';
import { LinkButton } from 'cuix/dist/components/Button';
import PrimaryButton from 'cuix/dist/components/Button/PrimaryButton';
import Button from 'cuix/dist/components/Button/Button';
import Loading from 'cuix/dist/components/Loading';
import Modal from 'cuix/dist/components/Modal';
import EmptyState from 'cuix/dist/components/EmptyState';
import Filter from 'cuix/dist/components/Filter';
import PaginatedTable, {
  type ColumnProps as PaginatedColumnProps
} from '../../../reactComponents/PaginatedTable/PaginatedTable';
import type { FilterOutput } from 'cuix/dist/components/Filter/types';
import { i18nReact } from '../../../utils/i18nReact';

export interface TableRowItem {
  name: string;
  type: string;
  comment: string;
}

export interface TablesListProps {
  tables: TableRowItem[];
  loading: boolean;
  isRefreshing: boolean;
  onRefresh?: () => void;
  tableFilter: string;
  setTableFilter: (value: string) => void;
  tablePageNumber: number;
  setTablePageNumber: (n: number) => void;
  tablePageSize: number;
  setTablePageSize: (s: number) => void;
  tableDescriptions: Record<string, string>;
  editingTableName: string | null;
  editingTableValue: string;
  setEditingTableName: (name: string | null) => void;
  setEditingTableValue: (v: string) => void;
  onOpenTable: (name: string) => void;
  onSaveDescription: (name: string, value: string) => void;
  onViewSelection?: (name: string) => void;
  onQuerySelection?: (name: string) => void;
  onDropSelection?: (names: string[]) => Promise<void> | void;
}

const TablesList = ({
  tables,
  loading,
  isRefreshing,
  onRefresh,
  tableFilter,
  setTableFilter,
  tablePageNumber,
  setTablePageNumber,
  tablePageSize,
  setTablePageSize,
  tableDescriptions,
  editingTableName,
  editingTableValue,
  setEditingTableName,
  setEditingTableValue,
  onOpenTable,
  onSaveDescription,
  onViewSelection,
  onQuerySelection,
  onDropSelection
}: TablesListProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [selected, setSelected] = useState<string[]>([]);
  const [confirmOpen, setConfirmOpen] = useState(false);

  const filtered = (tables || []).filter(item =>
    tableFilter ? item.name.toLowerCase().includes(tableFilter.toLowerCase()) : true
  );

  // Compute memoized data BEFORE any early return to keep hook order stable
  const data = useMemo(
    () =>
      filtered.map(item => ({
        key: item.name,
        name: item.name,
        type: item.type,
        comment: item.comment
      })),
    [filtered]
  );

  if (!loading && filtered.length === 0) {
    return (
      <div>
        <div style={{ marginBottom: 8 }}>{t('Tables')}</div>
        <EmptyState className="hue-table-browser__empty-state" title={t('No tables')} />
      </div>
    );
  }

  const columns: PaginatedColumnProps<TableRowItem>[] = [
    {
      title: t('Table'),
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: { name: string }) => (
        <LinkButton aria-label={t('Open table')} onClick={() => onOpenTable(record.name)}>
          {text}
        </LinkButton>
      )
    },
    { title: t('Type'), dataIndex: 'type', key: 'type' },
    {
      title: t('Description'),
      dataIndex: 'comment',
      key: 'description',
      render: (_: string, record: { name: string }) => {
        const hasValue = Object.prototype.hasOwnProperty.call(tableDescriptions, record.name);
        const current = tableDescriptions[record.name] || '';
        if (editingTableName === record.name) {
          return (
            <div>
              <Input.TextArea
                autoSize={{ minRows: 1, maxRows: 4 }}
                value={editingTableValue}
                onChange={e => setEditingTableValue(e.target.value)}
                onPressEnter={e => {
                  e.preventDefault();
                  onSaveDescription(record.name, editingTableValue);
                }}
              />
              <div style={{ marginTop: 4 }}>
                <PrimaryButton
                  size="small"
                  onClick={() => onSaveDescription(record.name, editingTableValue)}
                >
                  {t('Save')}
                </PrimaryButton>
                <Button
                  size="small"
                  onClick={() => setEditingTableName(null)}
                  style={{ marginLeft: 8 }}
                >
                  {t('Cancel')}
                </Button>
              </div>
            </div>
          );
        }
        if (!hasValue) {
          return <Skeleton.Input active size="small" style={{ width: '60%' }} />;
        }
        return (
          <div>
            <span style={{ whiteSpace: 'pre-wrap' }}>{current || ''}</span>
            <LinkButton
              size="small"
              onClick={() => {
                setEditingTableName(record.name);
                setEditingTableValue(current);
              }}
              style={{ marginLeft: current ? 8 : 0 }}
            >
              {current ? t('Edit') : t('Add')}
            </LinkButton>
          </div>
        );
      }
    }
  ];

  const totalSize = data.length;
  const totalPages = Math.max(Math.ceil(totalSize / tablePageSize), 1);
  const start = (tablePageNumber - 1) * tablePageSize;
  const pageData = data.slice(start, start + tablePageSize);

  return (
    <div>
      <h2 className="hue-table-browser__heading">
        {t('{{label}} ({{count}})', {
          label: t('Tables'),
          count: totalSize
        })}
      </h2>
      <Loading spinning={!!loading || isRefreshing}>
        {(onViewSelection || onQuerySelection || onDropSelection || onRefresh) && (
          <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end', marginBottom: 8 }}>
            {onRefresh && (
              <PrimaryButton onClick={onRefresh} disabled={!!loading || isRefreshing}>
                {t('Refresh')}
              </PrimaryButton>
            )}
            {onViewSelection && (
              <Button
                disabled={selected.length !== 1}
                onClick={() => selected[0] && onViewSelection?.(selected[0])}
              >
                {t('View')}
              </Button>
            )}
            {onQuerySelection && (
              <Button
                disabled={selected.length !== 1}
                onClick={() => selected[0] && onQuerySelection?.(selected[0])}
              >
                {t('Query')}
              </Button>
            )}
            {onDropSelection && (
              <Button disabled={!selected.length} onClick={() => setConfirmOpen(true)}>
                {t('Drop')}
              </Button>
            )}
          </div>
        )}
        <div className="hue-table-browser__filter">
          <Filter
            search={{ placeholder: t('Filter tables') }}
            onChange={(output: FilterOutput) => {
              const searchValue = String(
                (output as unknown as { search?: unknown[] }).search?.[0] ?? ''
              );
              if (searchValue !== tableFilter) {
                setTableFilter(searchValue);
              }
            }}
          />
        </div>
        <PaginatedTable<TableRowItem>
          data={pageData}
          columns={columns}
          rowKey="key"
          onRowSelect={selectedRows =>
            setSelected((selectedRows as unknown as { name: string }[]).map(r => r.name))
          }
          onRowClick={record => ({
            onClick: () => onOpenTable((record as unknown as { name: string }).name)
          })}
          pagination={{
            pageStats: {
              pageNumber: tablePageNumber,
              totalPages,
              pageSize: tablePageSize,
              totalSize
            },
            setPageNumber: setTablePageNumber,
            setPageSize: setTablePageSize
          }}
        />
      </Loading>

      <Modal
        open={confirmOpen}
        title={t('Drop table(s)')}
        okText={t('Drop')}
        okButtonProps={{ danger: true }}
        cancelText={t('Cancel')}
        onCancel={() => setConfirmOpen(false)}
        onOk={async () => {
          try {
            if (onDropSelection) {
              await onDropSelection(selected);
            }
            setSelected([]);
          } finally {
            setConfirmOpen(false);
          }
        }}
      >
        <div style={{ marginBottom: 8 }}>
          {t('Do you really want to drop the selected table(s)?')}
        </div>
        <ul>
          {selected.slice(0, 10).map(name => (
            <li key={name}>{name}</li>
          ))}
        </ul>
        {selected.length > 10 && (
          <div>
            {t('and')} {selected.length - 10} {t('others')}.
          </div>
        )}
      </Modal>
    </div>
  );
};

export default TablesList;

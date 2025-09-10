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

export interface DatabasesListProps {
  databases: string[];
  loading: boolean;
  isRefreshing: boolean;
  onRefresh?: () => void;
  dbFilter: string;
  setDbFilter: (value: string) => void;
  dbPageNumber: number;
  setDbPageNumber: (n: number) => void;
  dbPageSize: number;
  setDbPageSize: (s: number) => void;
  dbDescriptions: Record<string, string>;
  editingDb: string | null;
  editingValue: string;
  setEditingDb: (name: string | null) => void;
  setEditingValue: (v: string) => void;
  onOpenDatabase: (name: string) => void;
  onSaveDescription: (name: string, value: string) => void;
  onDropDatabases?: (names: string[]) => Promise<void> | void;
}

const DatabasesList = ({
  databases,
  loading,
  isRefreshing,
  onRefresh,
  dbFilter,
  setDbFilter,
  dbPageNumber,
  setDbPageNumber,
  dbPageSize,
  setDbPageSize,
  dbDescriptions,
  editingDb,
  editingValue,
  setEditingDb,
  setEditingValue,
  onOpenDatabase,
  onSaveDescription,
  onDropDatabases
}: DatabasesListProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [selected, setSelected] = useState<string[]>([]);
  const [confirmOpen, setConfirmOpen] = useState(false);

  const filtered = (databases || []).filter(db =>
    dbFilter ? db.toLowerCase().includes(dbFilter.toLowerCase()) : true
  );

  // Hooks must not be conditionally skipped: compute memoized data before any early return
  const data = useMemo(() => filtered.map(name => ({ key: name, name })), [filtered]);

  if (!loading && filtered.length === 0) {
    return (
      <div>
        <div style={{ marginBottom: 8 }}>{t('Databases')}</div>
        <EmptyState className="hue-table-browser__empty-state" title={t('No databases')} />
      </div>
    );
  }

  const columns: PaginatedColumnProps<{ name: string; description?: string }>[] = [
    {
      title: t('Database'),
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: { name: string }) => (
        <LinkButton aria-label={t('Open database')} onClick={() => onOpenDatabase(record.name)}>
          {text}
        </LinkButton>
      )
    },
    {
      title: t('Description'),
      dataIndex: 'description',
      key: 'description',
      render: (_: string | undefined, record: { name: string }) => {
        const hasValue = Object.prototype.hasOwnProperty.call(dbDescriptions, record.name);
        const current = dbDescriptions[record.name] || '';
        if (editingDb === record.name) {
          return (
            <div>
              <Input.TextArea
                autoSize={{ minRows: 1, maxRows: 4 }}
                value={editingValue}
                onChange={e => setEditingValue(e.target.value)}
                onPressEnter={e => {
                  e.preventDefault();
                  onSaveDescription(record.name, editingValue);
                }}
              />
              <div style={{ marginTop: 4 }}>
                <PrimaryButton
                  size="small"
                  onClick={() => onSaveDescription(record.name, editingValue)}
                >
                  {t('Save')}
                </PrimaryButton>
                <Button size="small" onClick={() => setEditingDb(null)} style={{ marginLeft: 8 }}>
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
                setEditingDb(record.name);
                setEditingValue(current);
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
  const totalPages = Math.max(Math.ceil(totalSize / dbPageSize), 1);
  const start = (dbPageNumber - 1) * dbPageSize;
  const pageData = data.slice(start, start + dbPageSize);

  return (
    <div>
      <h2 className="hue-table-browser__heading">
        {t('{{label}} ({{count}})', {
          label: t('Databases'),
          count: totalSize
        })}
      </h2>
      <Loading spinning={!!loading || isRefreshing}>
        {(onDropDatabases || onRefresh) && (
          <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end', marginBottom: 8 }}>
            {onRefresh && (
              <Button onClick={onRefresh} disabled={!!loading || isRefreshing}>
                {t('Refresh')}
              </Button>
            )}
            {onDropDatabases && (
              <Button
                onClick={() => {
                  if (!selected.length) {
                    return;
                  }
                  setConfirmOpen(true);
                }}
                disabled={!selected.length}
              >
                {t('Drop')}
              </Button>
            )}
          </div>
        )}
        <div className="hue-table-browser__filter">
          <Filter
            search={{ placeholder: t('Filter databases') }}
            onChange={(output: FilterOutput) => {
              const searchValue = String(
                (output as unknown as { search?: unknown[] }).search?.[0] ?? ''
              );
              if (searchValue !== dbFilter) {
                setDbFilter(searchValue);
              }
            }}
          />
        </div>
        <PaginatedTable<{ name: string; description?: string }>
          data={pageData}
          columns={columns}
          rowKey="key"
          onRowSelect={selectedRows =>
            setSelected((selectedRows as unknown as { name: string }[]).map(r => r.name))
          }
          pagination={{
            pageStats: {
              pageNumber: dbPageNumber,
              totalPages,
              pageSize: dbPageSize,
              totalSize
            },
            setPageNumber: setDbPageNumber,
            setPageSize: setDbPageSize
          }}
        />
      </Loading>

      <Modal
        open={confirmOpen}
        title={t('Drop database(s)')}
        okText={t('Drop')}
        okButtonProps={{ danger: true }}
        cancelText={t('Cancel')}
        onCancel={() => setConfirmOpen(false)}
        onOk={async () => {
          try {
            if (onDropDatabases) {
              await onDropDatabases(selected);
            }
            setSelected([]);
          } finally {
            setConfirmOpen(false);
          }
        }}
      >
        <div style={{ marginBottom: 8 }}>
          {t('Do you really want to delete the following database(s)?')}
        </div>
        <ul>
          {selected.map(name => (
            <li key={name}>{name}</li>
          ))}
        </ul>
        <div className="label label-important" style={{ display: 'inline-block', marginTop: 5 }}>
          {t('Warning: This will drop all tables and objects within the database.')}
        </div>
      </Modal>
    </div>
  );
};

export default DatabasesList;

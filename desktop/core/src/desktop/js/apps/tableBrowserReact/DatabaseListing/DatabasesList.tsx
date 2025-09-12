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
import { Checkbox, Input } from 'antd';
import { LinkButton } from 'cuix/dist/components/Button';
import Loading from 'cuix/dist/components/Loading';
import Modal from 'cuix/dist/components/Modal';
import EmptyState from 'cuix/dist/components/EmptyState';
import Filter from 'cuix/dist/components/Filter';
import DataLakeIcon from '@cloudera/cuix-core/icons/react/DataLakeIcon';
import InlineDescriptionEditor from '../sharedComponents/InlineDescriptionEditor';

import Toolbar, { type ToolbarAction } from '../sharedComponents/Toolbar';
import PageHeader from '../sharedComponents/PageHeader';
import PaginatedTable, {
  type ColumnProps as PaginatedColumnProps
} from '../../../reactComponents/PaginatedTable/PaginatedTable';
import type { FilterOutput } from 'cuix/dist/components/Filter/types';
import type { SortOrder } from 'antd/lib/table/interface';
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
  onCreateDatabase?: (name: string, comment?: string, location?: string) => Promise<void> | void;
  sourceType?: string;
  // Breadcrumbs props
  database?: string;
  table?: string;
  sourceOptions?: string[];
  onSelectSource?: (sourceType: string) => void;
  onClickDataSources?: () => void;
  onClickDatabases?: () => void;
  onClickDatabase?: (database: string) => void;
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
  onDropDatabases,
  onCreateDatabase,
  sourceType,
  database,
  table,
  sourceOptions,
  onSelectSource,
  onClickDataSources,
  onClickDatabases,
  onClickDatabase
}: DatabasesListProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [selected, setSelected] = useState<string[]>([]);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [sortByColumn, setSortByColumn] = useState<string | undefined>(undefined);
  const [sortOrder, setSortOrder] = useState<SortOrder>(null);
  const [createForm, setCreateForm] = useState({
    name: '',
    comment: '',
    location: '',
    useDefaultLocation: true
  });

  const filtered = (databases || []).filter(db =>
    dbFilter ? db.toLowerCase().includes(dbFilter.toLowerCase()) : true
  );

  // Apply sorting
  const sorted = useMemo(() => {
    const sortedData = [...filtered];
    if (sortOrder && sortByColumn) {
      sortedData.sort((a, b) => {
        const comparison = a.toLowerCase().localeCompare(b.toLowerCase());
        return sortOrder === 'ascend' ? comparison : -comparison;
      });
    }
    return sortedData;
  }, [filtered, sortOrder, sortByColumn]);

  // Hooks must not be conditionally skipped: compute memoized data before any early return
  const data = useMemo(() => sorted.map(name => ({ key: name, name })), [sorted]);

  // Prepare toolbar actions (excluding refresh which is now separate)
  const toolbarActions = useMemo(() => {
    const actions: ToolbarAction[] = [];

    if (onCreateDatabase) {
      actions.push({
        key: 'new',
        label: t('New'),
        onClick: () => setCreateModalOpen(true),
        variant: 'primary'
      });
    }

    if (onDropDatabases) {
      actions.push({
        key: 'drop',
        label: t('Drop'),
        onClick: () => {
          if (!selected.length) {
            return;
          }
          setConfirmOpen(true);
        },
        disabled: !selected.length,
        variant: 'danger'
      });
    }

    return actions;
  }, [onCreateDatabase, onDropDatabases, selected.length, t]);

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
      sorter: true,
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

        return (
          <InlineDescriptionEditor
            itemId={record.name}
            currentDescription={dbDescriptions[record.name]}
            originalDescription={undefined}
            isEditing={editingDb === record.name}
            editingValue={editingValue}
            hasLoadedDescription={hasValue}
            onStartEdit={(itemId, initialValue) => {
              setEditingDb(itemId);
              setEditingValue(initialValue);
            }}
            onCancelEdit={() => setEditingDb(null)}
            onSave={onSaveDescription}
            onEditingValueChange={setEditingValue}
          />
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
      <PageHeader
        title={sourceType?.toUpperCase()}
        icon={<DataLakeIcon />}
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
            label: t('Databases'),
            count: totalSize
          })}
        </h3>
      </div>

      {/* Filter row with filter and toolbar */}
      <div
        className={`hue-table-browser__filter-and-actions ${!!loading || isRefreshing ? 'disabled' : ''}`}
      >
        <Filter
          search={{ placeholder: t('Filter databases') }}
          onChange={(output: FilterOutput) => {
            if (!!loading || isRefreshing) {
              return; // Prevent changes while loading
            }
            const searchValue = String(
              (output as unknown as { search?: unknown[] }).search?.[0] ?? ''
            );
            if (searchValue !== dbFilter) {
              setDbFilter(searchValue);
            }
          }}
        />
        {toolbarActions.length > 0 && (
          <div className="hue-table-browser__actions">
            <Toolbar
              actions={toolbarActions}
              selectedItems={selected}
              loading={loading}
              isRefreshing={isRefreshing}
            />
          </div>
        )}
      </div>
      <Loading spinning={!!loading || isRefreshing}>
        <PaginatedTable<{ name: string; description?: string }>
          data={pageData}
          columns={columns}
          rowKey="key"
          sortByColumn={sortByColumn}
          sortOrder={sortOrder}
          setSortByColumn={column => setSortByColumn(String(column))}
          setSortOrder={setSortOrder}
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
        <div
          role="alert"
          className="label label-important"
          style={{ display: 'inline-block', marginTop: 5 }}
        >
          {t('Warning: This will drop all tables and objects within the database.')}
        </div>
      </Modal>

      <Modal
        open={createModalOpen}
        title={t('Create a new database')}
        okText={t('Create')}
        cancelText={t('Cancel')}
        onCancel={() => {
          setCreateModalOpen(false);
          setCreateForm({
            name: '',
            comment: '',
            location: '',
            useDefaultLocation: true
          });
        }}
        onOk={async () => {
          if (!createForm.name.trim()) {
            return;
          }
          try {
            if (onCreateDatabase) {
              await onCreateDatabase(
                createForm.name.trim(),
                createForm.comment.trim() || undefined,
                createForm.useDefaultLocation ? undefined : createForm.location.trim() || undefined
              );
            }
            setCreateForm({
              name: '',
              comment: '',
              location: '',
              useDefaultLocation: true
            });
          } finally {
            setCreateModalOpen(false);
          }
        }}
      >
        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', marginBottom: 4, fontWeight: 'bold' }}>
            {t('Database Name')} *
          </label>
          <Input
            placeholder={t('Database name')}
            value={createForm.name}
            onChange={e => setCreateForm({ ...createForm, name: e.target.value })}
          />
          <div style={{ fontSize: '12px', color: '#666', marginTop: 4 }}>
            {t('Name of the new database. Database names must be globally unique.')}
          </div>
        </div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', marginBottom: 4, fontWeight: 'bold' }}>
            {t('Description')}
          </label>
          <Input.TextArea
            placeholder={t('Optional description')}
            value={createForm.comment}
            onChange={e => setCreateForm({ ...createForm, comment: e.target.value })}
            rows={2}
          />
        </div>

        <div style={{ marginBottom: 16 }}>
          <Checkbox
            checked={createForm.useDefaultLocation}
            onChange={e => setCreateForm({ ...createForm, useDefaultLocation: e.target.checked })}
            style={{ marginBottom: 8 }}
          >
            {t('Use default location')}
          </Checkbox>

          {!createForm.useDefaultLocation && (
            <div>
              <label style={{ display: 'block', marginBottom: 4, fontWeight: 'bold' }}>
                {t('Location')}
              </label>
              <Input
                placeholder={t('Path to HDFS directory')}
                value={createForm.location}
                onChange={e => setCreateForm({ ...createForm, location: e.target.value })}
              />
              <div style={{ fontSize: '12px', color: '#666', marginTop: 4 }}>
                {t('Path to HDFS directory or file of database data.')}
              </div>
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
};

export default DatabasesList;

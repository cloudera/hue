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

import React, { useMemo, useRef } from 'react';
import { LinkButton } from 'cuix/dist/components/Button';
import Loading from 'cuix/dist/components/Loading';
import Modal from 'cuix/dist/components/Modal';
import Filter from 'cuix/dist/components/Filter';
import DataLakeIcon from '@cloudera/cuix-core/icons/react/DataLakeIcon';
import InlineDescriptionEditor from '../sharedComponents/InlineDescriptionEditor';

import Toolbar, { type ToolbarAction } from '../sharedComponents/Toolbar';
import PageHeader from '../sharedComponents/PageHeader';
import PaginatedTable, {
  type ColumnProps as PaginatedColumnProps
} from '../../../reactComponents/PaginatedTable/PaginatedTable';
import type { FilterOutput } from 'cuix/dist/components/Filter/types';
import { i18nReact } from '../../../utils/i18nReact';
import CreateDatabaseModal from './CreateDatabaseModal';
import './DatabasesList.scss';
import type { DatabasesListState } from './useDatabasesListState';

export interface DatabasesListProps {
  databases: string[];
  isRefreshing: boolean;
  onRefresh?: () => void;
  state: DatabasesListState;
  onOpenDatabase: (name: string) => void;
  // onSaveDescription now provided inside descriptionsState
  onDropDatabases?: (names: string[]) => Promise<void> | void;
  onCreateDatabase?: (name: string, comment?: string, location?: string) => Promise<void> | void;
  sourceType?: string;
  // Breadcrumbs props
  database?: string;
  table?: string;
  sourceOptions?: string[];
  onSelectSource?: (sourceType: string) => void;
}

const DatabasesList = ({
  databases,
  isRefreshing,
  onRefresh,
  state,
  onOpenDatabase,
  onDropDatabases,
  onCreateDatabase,
  sourceType,
  database,
  table,
  sourceOptions,
  onSelectSource
}: DatabasesListProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const containerRef = useRef<HTMLDivElement>(null);

  const {
    isInitializing,
    dbFilter,
    setDbFilter,
    dbPageNumber,
    setDbPageNumber,
    dbPageSize,
    setDbPageSize,
    selected,
    setSelected,
    confirmOpen,
    setConfirmOpen,
    createModalOpen,
    setCreateModalOpen,
    sortByColumn,
    setSortByColumn,
    sortOrder,
    setSortOrder,
    editState
  } = state;

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

  const columns: PaginatedColumnProps<{ name: string; description?: string }>[] = [
    {
      title: t('Database'),
      dataIndex: 'name',
      key: 'name',
      sorter: true,
      render: (text: string, record: { name: string }) => (
        <LinkButton
          className="hue-db-list__link"
          aria-label={t('Open database')}
          onClick={() => onOpenDatabase(record.name)}
        >
          {text}
        </LinkButton>
      )
    },
    {
      title: t('Description'),
      dataIndex: 'description',
      key: 'description',
      render: (_: string | undefined, record: { name: string }) => {
        const hasValue = Object.prototype.hasOwnProperty.call(editState.values, record.name);

        return (
          <InlineDescriptionEditor
            itemId={record.name}
            currentDescription={editState.values[record.name]}
            originalDescription={undefined}
            isEditing={editState.editingId === record.name}
            editingValue={editState.editingValue}
            hasLoadedDescription={hasValue}
            onStartEdit={(itemId, initialValue) => {
              editState.setEditingId(itemId);
              editState.setEditingValue(initialValue);
            }}
            onCancelEdit={() => editState.setEditingId(null)}
            onSave={editState.save}
            onEditingValueChange={editState.setEditingValue}
          />
        );
      }
    }
  ];

  const totalSize = data.length;
  const totalPages = Math.max(Math.ceil(totalSize / dbPageSize), 1);
  const start = (dbPageNumber - 1) * dbPageSize;
  const pageData = data.slice(start, start + dbPageSize);

  // debug: rendering
  return (
    <div ref={containerRef}>
      <PageHeader
        title={sourceType?.toUpperCase()}
        icon={<DataLakeIcon />}
        onRefresh={onRefresh}
        loading={isInitializing || isRefreshing}
        isRefreshing={isRefreshing}
        sourceType={sourceType}
        database={database}
        table={table}
        sourceOptions={sourceOptions}
        onSelectSource={onSelectSource}
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
        className={`hue-table-browser__filter-and-actions ${!!isInitializing || isRefreshing ? 'disabled' : ''}`}
      >
        <Filter
          search={{ placeholder: t('Filter databases') }}
          onChange={(output: FilterOutput) => {
            if (!!isInitializing || isRefreshing) {
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
              loading={isInitializing}
              isRefreshing={isRefreshing}
            />
          </div>
        )}
      </div>
      <Loading spinning={!!isInitializing}>
        {isInitializing ? null : (
          <PaginatedTable<{ name: string; description?: string }>
            loading={isRefreshing}
            locale={{ emptyText: t('No results found') }}
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
              setPageSize: setDbPageSize,
              pageSizeOptions: [10, 50, 100, 500]
            }}
          />
        )}
      </Loading>

      <Modal
        open={confirmOpen}
        title={t('Drop database(s)')}
        okText={t('Drop')}
        okButtonProps={{ danger: true }}
        cancelText={t('Cancel')}
        onCancel={() => setConfirmOpen(false)}
        getContainer={() => containerRef.current || document.body}
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
        <div className="hue-db-list__confirm-text">
          {t('Do you really want to delete the following database(s)?')}
        </div>
        <ul>
          {selected.map(name => (
            <li key={name}>{name}</li>
          ))}
        </ul>
        <div role="alert" className="label label-important hue-db-list__warning">
          {t('Warning: This will drop all tables and objects within the database.')}
        </div>
      </Modal>

      <CreateDatabaseModal
        open={createModalOpen}
        sourceType={sourceType}
        getContainer={() => containerRef.current || document.body}
        onCancel={() => setCreateModalOpen(false)}
        onSubmit={async (name, comment, location) => {
          if (onCreateDatabase) {
            await onCreateDatabase(name, comment, location);
          }
          setCreateModalOpen(false);
        }}
      />
    </div>
  );
};

export default DatabasesList;

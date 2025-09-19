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

import React, { useMemo } from 'react';
import { ConfigProvider } from 'antd';
import { LinkButton } from 'cuix/dist/components/Button';
import Loading from 'cuix/dist/components/Loading';
import Modal from 'cuix/dist/components/Modal';
import Filter from 'cuix/dist/components/Filter';
import DatabaseIcon from '@cloudera/cuix-core/icons/react/DatabaseIcon';
import InlineDescriptionEditor from '../sharedComponents/InlineDescriptionEditor';
import Toolbar, { type ToolbarAction } from '../sharedComponents/Toolbar';
import DatabasePropertiesComponent, {
  type DatabaseProperties
} from '../DatabaseListing/DatabaseProperties';
import PageHeader from '../sharedComponents/PageHeader';
import PaginatedTable, {
  type ColumnProps as PaginatedColumnProps
} from '../../../reactComponents/PaginatedTable/PaginatedTable';
import type { FilterOutput, BasicFacet } from 'cuix/dist/components/Filter/types';
// import type { SortOrder } from 'antd/lib/table/interface';
import { i18nReact } from '../../../utils/i18nReact';
import './TablesList.scss';
import type { TablesListState } from './useTablesListState';

export interface TableRowItem {
  name: string;
  type: string;
  comment: string;
}

export interface TablesListProps {
  tables: TableRowItem[];
  isRefreshing: boolean;
  onRefresh?: () => void;
  onOpenTable: (name: string) => void;
  onViewSelection?: (name: string) => void;
  onQuerySelection?: (name: string) => void;
  onDropSelection?: (names: string[], skipTrash?: boolean) => Promise<void> | void;
  onCreateTable?: () => void;
  databaseName?: string;
  databaseProperties?: DatabaseProperties;
  loadingDatabaseProperties?: boolean;
  sourceType?: string;
  table?: string;
  sourceOptions?: string[];
  onSelectSource?: (sourceType: string) => void;
  state: TablesListState;
}

const TablesList = ({
  tables,
  isRefreshing,
  onRefresh,
  onOpenTable,
  onViewSelection,
  onQuerySelection,
  onDropSelection,
  onCreateTable,
  databaseName,
  databaseProperties,
  loadingDatabaseProperties,
  sourceType,
  table,
  sourceOptions,
  onSelectSource,
  state
  // deprecated props intentionally not destructured/used; kept in type for compatibility
}: TablesListProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const {
    isInitializing,
    tableFilter,
    setTableFilter,
    tablePageSize,
    setTablePageSize,
    tablePageNumber,
    setTablePageNumber,
    selected,
    setSelected,
    confirmOpen,
    setConfirmOpen,
    skipTrash,
    setSkipTrash,
    sortByColumn,
    setSortByColumn,
    sortOrder,
    setSortOrder,
    selectedTypes,
    setSelectedTypes,
    editState
  } = state;

  // Build a deterministic key from available types to stabilize facets identity across renders
  const typesKey = useMemo(() => {
    const set = new Set<string>();
    (tables || []).forEach(item => {
      if (item.type) {
        set.add(String(item.type));
      }
    });
    return Array.from(set).sort().join('|');
  }, [tables]);

  const allTypes = useMemo(() => (typesKey ? typesKey.split('|') : []), [typesKey]);

  const typeFacetLabel = t('Type');
  const facets = useMemo((): BasicFacet[] => {
    if (!allTypes.length) {
      return [];
    }
    return [
      {
        label: typeFacetLabel,
        items: allTypes,
        multiple: true
      }
    ];
  }, [allTypes, typeFacetLabel]);

  const filtered = useMemo(() => {
    let list = tables || [];
    if (tableFilter) {
      const lower = tableFilter.toLowerCase();
      list = list.filter(item => {
        const nameMatches = item.name.toLowerCase().includes(lower);
        const desc = (editState.values[item.name] || item.comment || '').toLowerCase();
        const descMatches = desc.includes(lower);
        return nameMatches || descMatches;
      });
    }
    if (selectedTypes.length > 0) {
      const allowed = new Set(selectedTypes.map(String));
      list = list.filter(item => allowed.has(String(item.type)));
    }
    return list;
  }, [tables, tableFilter, selectedTypes, editState.values]);

  // Apply sorting
  const sorted = useMemo(() => {
    if (!sortOrder || !sortByColumn) {
      return filtered;
    }

    return [...filtered].sort((a, b) => {
      let aValue: string, bValue: string;

      if (sortByColumn === 'name') {
        aValue = a.name.toLowerCase();
        bValue = b.name.toLowerCase();
      } else if (sortByColumn === 'type') {
        aValue = a.type.toLowerCase();
        bValue = b.type.toLowerCase();
      } else {
        return 0;
      }

      const comparison = aValue.localeCompare(bValue);
      return sortOrder === 'ascend' ? comparison : -comparison;
    });
  }, [filtered, sortOrder, sortByColumn]);

  // Compute memoized data BEFORE any early return to keep hook order stable
  const data = useMemo(
    () =>
      sorted.map(item => ({
        key: item.name,
        name: item.name,
        type: item.type,
        comment: item.comment
      })),
    [sorted]
  );

  // Prepare toolbar actions (excluding refresh which is now separate)
  const toolbarActions = useMemo(() => {
    const actions: ToolbarAction[] = [];

    if (onCreateTable) {
      actions.push({
        key: 'new',
        label: t('New'),
        onClick: onCreateTable,
        variant: 'primary'
      });
    }

    if (onViewSelection) {
      actions.push({
        key: 'view',
        label: t('View'),
        onClick: () => {
          if (selected.length === 1) {
            onViewSelection(selected[0]);
          }
        },
        disabled: selected.length !== 1,
        tooltip: selected.length !== 1 ? t('Select exactly one table to view') : undefined
      });
    }

    if (onQuerySelection) {
      actions.push({
        key: 'query',
        label: t('Query'),
        onClick: () => {
          if (selected.length === 1) {
            onQuerySelection(selected[0]);
          }
        },
        disabled: selected.length !== 1,
        tooltip: selected.length !== 1 ? t('Select exactly one table to query') : undefined
      });
    }

    if (onDropSelection) {
      actions.push({
        key: 'drop',
        label: t('Drop'),
        onClick: () => {
          if (selected.length === 0) {
            // This shouldn't happen due to disabled state, but add safety check
            return;
          }
          setConfirmOpen(true);
        },
        disabled: !selected.length,
        variant: 'danger',
        tooltip: !selected.length ? t('Select tables to drop') : undefined
      });
    }

    return actions;
  }, [onCreateTable, onViewSelection, onQuerySelection, onDropSelection, selected, t]);

  // Keep the filter visible when filtered results are empty; use table built-in empty message.

  const columns: PaginatedColumnProps<TableRowItem>[] = [
    {
      title: t('Table'),
      dataIndex: 'name',
      key: 'name',
      sorter: true,
      render: (text: string, record: { name: string }) => (
        <LinkButton aria-label={t('Open table')} onClick={() => onOpenTable(record.name)}>
          {text}
        </LinkButton>
      )
    },
    { title: t('Type'), dataIndex: 'type', key: 'type', sorter: true },
    {
      title: t('Description'),
      dataIndex: 'comment',
      key: 'description',
      render: (_: string, record: { name: string }) => {
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
  const totalPages = Math.max(Math.ceil(totalSize / tablePageSize), 1);
  const start = (tablePageNumber - 1) * tablePageSize;
  const pageData = data.slice(start, start + tablePageSize);

  return (
    <div>
      {/* Page Header */}
      <PageHeader
        title={databaseName}
        icon={<DatabaseIcon />}
        onRefresh={onRefresh}
        loading={isInitializing || isRefreshing}
        isRefreshing={isRefreshing}
        sourceType={sourceType}
        database={databaseName}
        table={table}
        sourceOptions={sourceOptions}
        onSelectSource={onSelectSource}
      />

      {/* Database Properties Section */}
      {databaseName && (
        <DatabasePropertiesComponent
          properties={databaseProperties}
          loading={loadingDatabaseProperties}
        />
      )}

      {/* Header row with title */}
      <div className="hue-table-browser__header-with-actions">
        <h3 className="hue-h3">
          {t('{{label}} ({{count}})', {
            label: t('Tables & Views'),
            count: totalSize
          })}
        </h3>
      </div>

      {/* Filter row with filter and toolbar */}
      <div
        className={`hue-table-browser__filter-and-actions ${!!isInitializing || isRefreshing ? 'disabled' : ''}`}
      >
        <div className="cuix-filter">
          <ConfigProvider getPopupContainer={trigger => trigger?.parentElement || document.body}>
            <Filter
              key={`filter-${facets.length}`}
              search={{ placeholder: t('Filter tables & views') }}
              facets={facets}
              onChange={(output: FilterOutput) => {
                if (!!isInitializing || isRefreshing) {
                  return; // Prevent changes while loading
                }
                const out = (output || {}) as Record<string, unknown[]>;
                const nextTypes = Array.isArray(out[typeFacetLabel])
                  ? (out[typeFacetLabel] as unknown[]).map(String)
                  : [];
                // Only update when the selection meaningfully changes
                const prev = selectedTypes;
                const changed =
                  prev.length !== nextTypes.length ||
                  prev.some(v => !nextTypes.includes(v)) ||
                  nextTypes.some(v => !prev.includes(v));
                if (changed) {
                  setSelectedTypes(nextTypes);
                }
                const searchValue = String(
                  (output as unknown as { search?: unknown[] }).search?.[0] ?? ''
                );
                if (searchValue !== tableFilter) {
                  setTableFilter(searchValue);
                }
              }}
            />
          </ConfigProvider>
        </div>
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
          <PaginatedTable<TableRowItem>
            data={pageData}
            columns={columns}
            rowKey="key"
            loading={isRefreshing}
            sortByColumn={sortByColumn}
            sortOrder={sortOrder}
            setSortByColumn={column => setSortByColumn(String(column))}
            setSortOrder={setSortOrder}
            onRowSelect={selectedRows =>
              setSelected((selectedRows as unknown as { name: string }[]).map(r => r.name))
            }
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
        )}
      </Loading>

      <Modal
        open={confirmOpen}
        title={t('Drop table(s)')}
        okText={t('Drop')}
        okButtonProps={{ danger: true }}
        cancelText={t('Cancel')}
        onCancel={() => {
          setConfirmOpen(false);
          setSkipTrash(false);
        }}
        onOk={async () => {
          try {
            if (onDropSelection) {
              await onDropSelection(selected, skipTrash);
            }
            setSelected([]);
          } finally {
            setConfirmOpen(false);
            setSkipTrash(false);
          }
        }}
      >
        <div className="hue-tables-list__confirm-text">
          {t('Do you really want to drop the selected table(s)?')}
        </div>
        <ul className="hue-tables-list__confirm-list">
          {selected.slice(0, 10).map(name => (
            <li key={name}>{name}</li>
          ))}
        </ul>
        {selected.length > 10 && (
          <div className="hue-tables-list__confirm-more">
            {t('and')} {selected.length - 10} {t('others')}.
          </div>
        )}
        <label className="hue-tables-list__confirm-skip">
          <input
            type="checkbox"
            checked={skipTrash}
            onChange={e => setSkipTrash(e.target.checked)}
          />
          {t('Skip the trash')}
        </label>
      </Modal>
    </div>
  );
};

export default TablesList;

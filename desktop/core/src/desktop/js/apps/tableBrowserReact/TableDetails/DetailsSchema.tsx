// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React, { useMemo, useState } from 'react';
import { Popover } from 'antd';
import Table from 'cuix/dist/components/Table';
import Filter from 'cuix/dist/components/Filter';
import BorderlessButton from 'cuix/dist/components/Button/BorderlessButton';
import KeyIcon from '@cloudera/cuix-core/icons/react/KeyIcon';
import InlineDescriptionEditor from '../sharedComponents/InlineDescriptionEditor';
import PaginatedTable, {
  type ColumnProps as PaginatedColumnProps
} from '../../../reactComponents/PaginatedTable/PaginatedTable';
import type { FilterOutput } from 'cuix/dist/components/Filter/types';
import type { SortOrder } from 'antd/lib/table/interface';
import { i18nReact } from '../../../utils/i18nReact';
import { useDescriptionManager } from '../hooks/useDescriptionManager';
import type { Connector, Compute, Namespace } from '../../../config/types';

import './DetailsSchema.scss';

interface SamplePopoverProps {
  sampleData: { key: number; value: string | number | null }[];
}

const SamplePopover = ({ sampleData }: SamplePopoverProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [sampleFilter, setSampleFilter] = useState('');

  const filteredSampleData = sampleData.filter(
    item =>
      sampleFilter === '' ||
      String(item.value || '')
        .toLowerCase()
        .includes(sampleFilter.toLowerCase())
  );

  // Limit display to first 250 items for performance with large datasets
  const MAX_DISPLAY_ITEMS = 250;
  const displayData = filteredSampleData.slice(0, MAX_DISPLAY_ITEMS);
  const hasMore = filteredSampleData.length > MAX_DISPLAY_ITEMS;

  const sampleColumns = [
    {
      title: t('Sample Values'),
      dataIndex: 'value',
      key: 'value',
      render: (value: string | number | null) => String(value || '')
    }
  ];

  return (
    <div className="sample-popover__container">
      <div className="sample-popover__search">
        <Filter
          search={{ placeholder: t('Filter sample values') }}
          onChange={(output: FilterOutput) => {
            const searchValue = String(
              (output as unknown as { search?: unknown[] }).search?.[0] ?? ''
            );
            setSampleFilter(searchValue);
          }}
        />
      </div>
      <Table
        columns={sampleColumns}
        dataSource={displayData}
        size="small"
        pagination={false}
        showHeader={false}
        className="sample-popover__table"
        scroll={{ y: 250 }}
      />
      <div className="sample-popover__footer">
        {hasMore ? (
          <>
            {t('Showing first {{count}} of {{total}} values', {
              count: MAX_DISPLAY_ITEMS,
              total: filteredSampleData.length
            })}
            {sampleFilter && (
              <div style={{ fontSize: '11px', color: '#999', marginTop: '4px' }}>
                {t('Use the filter above to narrow down results')}
              </div>
            )}
          </>
        ) : (
          filteredSampleData.length > 0 && (
            <>
              {t('Showing {{count}} values', { count: filteredSampleData.length })}
              {sampleData.length !== filteredSampleData.length && (
                <span style={{ fontSize: '11px', color: '#999' }}>
                  {' '}
                  ({t('filtered from {{total}}', { total: sampleData.length })})
                </span>
              )}
            </>
          )
        )}
      </div>
    </div>
  );
};

export interface ColumnDef {
  name: string;
  type: string;
  comment?: string;
  sample?: string;
  isPartitionKey?: boolean;
}

export interface DetailsSchemaProps {
  columns: ColumnDef[];
  sampleData?: { headers: string[]; rows: (string | number | null)[][] };
  connector?: Connector | null;
  namespace?: Namespace | null;
  compute?: Compute | null;
  database?: string;
  table?: string;
}

const DetailsSchema = ({
  columns,
  sampleData,
  connector,
  namespace,
  compute,
  database,
  table
}: DetailsSchemaProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [filter, setFilter] = useState('');
  const [pageNumber, setPageNumber] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [sortByColumn, setSortByColumn] = useState<string | undefined>(undefined);
  const [sortOrder, setSortOrder] = useState<SortOrder>(null);

  // Description management
  const {
    descriptions,
    editingItem: editingColumn,
    editingValue: editingValue,
    setEditingItem: setEditingColumn,
    setEditingValue: setEditingValue,
    saveDescription
  } = useDescriptionManager({
    connector,
    namespace,
    compute,
    items: columns.map(col => col.name),
    path: database && table ? [database, table] : [],
    currentItem: undefined // We're editing columns, not navigating to them
  });

  const filtered = useMemo(() => {
    if (!filter) {
      return columns;
    }
    const q = filter.toLowerCase();
    return columns.filter(
      c => c.name.toLowerCase().includes(q) || (c.comment || '').toLowerCase().includes(q)
    );
  }, [columns, filter]);

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

  const data = sorted.map(col => ({ key: col.name, ...col }));
  const totalSize = data.length;
  const totalPages = Math.max(Math.ceil(totalSize / pageSize), 1);
  const start = (pageNumber - 1) * pageSize;
  const pageData = data.slice(start, start + pageSize);

  // Create sample data for a specific column
  const getColumnSampleData = (columnName: string) => {
    if (!sampleData?.headers || !sampleData?.rows) {
      return null;
    }

    // Try exact match first
    let columnIndex = sampleData.headers.indexOf(columnName);

    // If not found, try case-insensitive match
    if (columnIndex === -1) {
      columnIndex = sampleData.headers.findIndex(
        header => header.toLowerCase() === columnName.toLowerCase()
      );
    }

    // If still not found, try partial match (for complex column names)
    if (columnIndex === -1) {
      columnIndex = sampleData.headers.findIndex(
        header => header.includes(columnName) || columnName.includes(header)
      );
    }
    if (columnIndex === -1) {
      return null;
    }

    return sampleData.rows
      .map((row, index) => ({
        key: index,
        value: row[columnIndex]
      }))
      .filter(item => item.value !== null && item.value !== undefined);
  };

  // Get first sample value for a column
  const getFirstSample = (columnName: string): string => {
    const columnSampleData = getColumnSampleData(columnName);
    if (!columnSampleData || columnSampleData.length === 0) {
      return '';
    }
    return String(columnSampleData[0]?.value || '');
  };

  // Get second sample value for a column
  const getSecondSample = (columnName: string): string => {
    const columnSampleData = getColumnSampleData(columnName);
    if (!columnSampleData || columnSampleData.length < 2) {
      return '';
    }
    return String(columnSampleData[1]?.value || '');
  };

  const columnsDef: PaginatedColumnProps<ColumnDef & { key: string }>[] = [
    {
      title: t('Column'),
      dataIndex: 'name',
      key: 'name',
      sorter: true,
      render: (name: string, record: ColumnDef & { key: string }) => {
        const columnSampleData = getColumnSampleData(name);

        const columnNameWithIcon = (
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            {record.isPartitionKey && <KeyIcon style={{ fontSize: '12px', color: '#1890ff' }} />}
            {name}
          </span>
        );

        if (!columnSampleData || columnSampleData.length === 0) {
          return (
            <Popover
              content={
                <div className="sample-popover__no-data">
                  <div className="sample-popover__no-data-content">
                    {!sampleData ? (
                      <div>
                        <div className="sample-popover__no-data-icon"></div>
                        {t('No sample data available')}
                      </div>
                    ) : !sampleData.headers?.includes(name) ? (
                      <div>
                        <div className="sample-popover__no-data-icon"></div>
                        {t('Column not found in sample data')}
                        <div style={{ fontSize: '12px', marginTop: '8px' }}>
                          <strong>Looking for:</strong> "{name}"
                          <br />
                          <strong>Available headers:</strong>
                          <br />
                          {sampleData.headers?.map((h, i) => <div key={i}>• "{h}"</div>)}
                        </div>
                      </div>
                    ) : (
                      <div>
                        <div className="sample-popover__no-data-icon"></div>
                        {t('No sample values available for this column')}
                      </div>
                    )}
                  </div>
                </div>
              }
              title={`${t('Sample data for')} ${name}`}
              trigger="click"
              placement="right"
              overlayClassName="sample-data-popover"
              getPopupContainer={triggerNode => triggerNode.parentElement || document.body}
            >
              <BorderlessButton className="clickable-column-name">
                {columnNameWithIcon}
              </BorderlessButton>
            </Popover>
          );
        }
        return (
          <Popover
            content={<SamplePopover sampleData={columnSampleData} />}
            title={
              <div className="sample-popover-title">
                {t('Sample data for')}{' '}
                <span className="sample-popover-title__column-name">{name}</span>
              </div>
            }
            trigger="click"
            placement="right"
            overlayClassName="sample-data-popover"
            getPopupContainer={triggerNode => triggerNode.parentElement || document.body}
          >
            <BorderlessButton className="clickable-column-name">
              {columnNameWithIcon}
            </BorderlessButton>
          </Popover>
        );
      }
    },
    { title: t('Type'), dataIndex: 'type', key: 'type', sorter: true },
    {
      title: t('Description'),
      dataIndex: 'comment',
      key: 'description',
      render: (_: string | undefined, record: ColumnDef & { key: string }) => {
        const hasValue = Object.prototype.hasOwnProperty.call(descriptions, record.name);

        return (
          <InlineDescriptionEditor
            itemId={record.name}
            currentDescription={descriptions[record.name]}
            originalDescription={record.comment}
            isEditing={editingColumn === record.name}
            editingValue={editingValue}
            hasLoadedDescription={hasValue}
            onStartEdit={(itemId, initialValue) => {
              setEditingColumn(itemId);
              setEditingValue(initialValue);
            }}
            onCancelEdit={() => setEditingColumn(null)}
            onSave={saveDescription}
            onEditingValueChange={setEditingValue}
            placeholder={t('Add a description...')}
          />
        );
      }
    },
    {
      title: t('Sample'),
      dataIndex: 'sample1',
      key: 'sample1',
      render: (_: string | undefined, record: ColumnDef & { key: string }) => {
        const sample = getFirstSample(record.name);
        return sample ? <span title={sample}>{sample}</span> : '';
      }
    },
    {
      title: '',
      dataIndex: 'sample2',
      key: 'sample2',
      render: (_: string | undefined, record: ColumnDef & { key: string }) => {
        const sample = getSecondSample(record.name);
        return sample ? <span title={sample}>{sample}</span> : '';
      }
    }
  ];

  return (
    <div className="hue-details-schema">
      <div className="hue-table-browser__filter">
        <Filter
          search={{ placeholder: t('Filter columns') }}
          onChange={(output: FilterOutput) => {
            const searchValue = String(
              (output as unknown as { search?: unknown[] }).search?.[0] ?? ''
            );
            if (searchValue !== filter) {
              setFilter(searchValue);
              setPageNumber(1);
            }
          }}
        />
      </div>
      <PaginatedTable<ColumnDef & { key: string }>
        data={pageData}
        columns={columnsDef}
        rowKey="key"
        sortByColumn={sortByColumn}
        sortOrder={sortOrder}
        setSortByColumn={column => setSortByColumn(String(column))}
        setSortOrder={setSortOrder}
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
    </div>
  );
};

export default DetailsSchema;

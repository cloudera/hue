// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React, { useMemo, useState } from 'react';
import { Popover } from 'antd';
import Filter from 'cuix/dist/components/Filter';
import BorderlessButton from 'cuix/dist/components/Button/BorderlessButton';
import KeyIcon from '@cloudera/cuix-core/icons/react/KeyIcon';
import InlineDescriptionEditor from '../../sharedComponents/InlineDescriptionEditor';
import PaginatedTable, {
  type ColumnProps as PaginatedColumnProps
} from '../../../../reactComponents/PaginatedTable/PaginatedTable';
import type { FilterOutput } from 'cuix/dist/components/Filter/types';
import type { SortOrder } from 'antd/lib/table/interface';
import { i18nReact } from '../../../../utils/i18nReact';
import { useDescriptionManager } from '../../hooks/useDescriptionManager';
import type { Connector, Compute, Namespace } from '../../../../config/types';
import decodeHtmlEntities from '../../../../utils/strings/decodeHtmlEntities';
import PrettyStructDisplay from '../../sharedComponents/PrettyStructDisplay';

import './Schema.scss';

// Removed in favor of navigating to Column Details page

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
  loadingSamples?: boolean;
  onOpenColumn?: (column: string) => void;
}

const DetailsSchema = ({
  columns,
  sampleData,
  connector,
  namespace,
  compute,
  database,
  table,
  loadingSamples,
  onOpenColumn
}: DetailsSchemaProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [filter, setFilter] = useState('');
  const [pageNumber, setPageNumber] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [sortByColumn, setSortByColumn] = useState<string | undefined>('name');
  const [sortOrder, setSortOrder] = useState<SortOrder>('ascend');

  const isStructType = (type: string): boolean => {
    const lower = (type || '').toLowerCase();
    return lower.includes('struct<');
  };

  const getBaseType = (type: string): string => {
    const lower = (type || '').trim().toLowerCase();
    if (!lower) {
      return '';
    }
    if (lower.startsWith('struct<')) {
      return 'struct';
    }
    if (lower.startsWith('array<')) {
      return 'array';
    }
    if (lower.startsWith('map<')) {
      return 'map';
    }
    // primitives possibly with params, e.g., decimal(10,2), varchar(50)
    const match = lower.match(/^([a-z_]+)/);
    return match ? match[1] : lower;
  };

  type TypeCategory = 'number' | 'text' | 'boolean' | 'time' | 'json' | 'complex' | 'other';

  const categorizeType = (type: string): TypeCategory => {
    const base = getBaseType(type);
    if (!base) {
      return 'other';
    }
    if (
      [
        'int',
        'integer',
        'bigint',
        'smallint',
        'tinyint',
        'float',
        'double',
        'real',
        'decimal',
        'numeric'
      ].includes(base)
    ) {
      return 'number';
    }
    if (['string', 'varchar', 'char', 'binary', 'varbinary'].includes(base)) {
      return 'text';
    }
    if (base === 'boolean') {
      return 'boolean';
    }
    if (['date', 'timestamp', 'timestamptz', 'interval'].includes(base)) {
      return 'time';
    }
    if (base === 'json') {
      return 'json';
    }
    if (['struct', 'array', 'map'].includes(base)) {
      return 'complex';
    }
    return 'other';
  };

  // Colors are applied via SCSS classes using cuix variables.

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
    // Avoid prefetching per-column descriptions to prevent N describe/stats calls
    // We rely on provided column comments and lazy load on explicit actions
    items: undefined,
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
        // Backend is encoding HTML entities in the sample data, so we need to decode them
        value: decodeHtmlEntities(row[columnIndex]) as string | number | null
      }))
      .filter(item => item.value !== null && item.value !== undefined);
  };

  // Get first sample value for a column
  const getFirstSample = (columnName: string): string => {
    const columnSampleData = getColumnSampleData(columnName);
    if (!columnSampleData || columnSampleData.length === 0) {
      return '';
    }
    return String(columnSampleData[0]?.value ?? '');
  };

  // Get second sample value for a column
  const getSecondSample = (columnName: string): string => {
    const columnSampleData = getColumnSampleData(columnName);
    if (!columnSampleData || columnSampleData.length < 2) {
      return '';
    }
    return String(columnSampleData[1]?.value ?? '');
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
              <BorderlessButton
                className="clickable-column-name"
                onClick={() => onOpenColumn && onOpenColumn(name)}
              >
                {columnNameWithIcon}
              </BorderlessButton>
            </Popover>
          );
        }
        return (
          <BorderlessButton
            className="clickable-column-name"
            onClick={() => onOpenColumn && onOpenColumn(name)}
          >
            {columnNameWithIcon}
          </BorderlessButton>
        );
      }
    },
    {
      title: t('Type'),
      dataIndex: 'type',
      key: 'type',
      sorter: true,
      render: (type: string) => {
        const category = categorizeType(type);
        const base = getBaseType(type);

        if (isStructType(type)) {
          return (
            <span className="schema-type-cell">
              <span
                className={`schema-type-label schema-type--${category}`}
                title={type}
                aria-label={`${t('Type')}: ${base}`}
              >
                {base}
              </span>
              <Popover
                title={t('Column type')}
                content={<PrettyStructDisplay structType={type} compact={true} />}
                trigger="click"
                placement="right"
                overlayClassName="schema-type-popover"
                getPopupContainer={triggerNode => triggerNode.parentElement || document.body}
              >
                <BorderlessButton className="schema-popover-trigger">
                  {t('View struct')}
                </BorderlessButton>
              </Popover>
            </span>
          );
        }

        return (
          <span
            className={`schema-type-label schema-type--${category}`}
            title={type}
            aria-label={`${t('Type')}: ${type}`}
          >
            {getBaseType(type)}
          </span>
        );
      }
    },
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
        if (loadingSamples) {
          return (
            <span className="schema-sample--loading" title={t('Loading sample values...')}>
              {t('Loading...')}
            </span>
          );
        }
        if (isStructType(record.type)) {
          const columnSampleData = getColumnSampleData(record.name) || [];
          return (
            <Popover
              content={
                <div className="schema-sample-popover__content">
                  {columnSampleData.length ? (
                    columnSampleData.slice(0, 100).map(item => (
                      <pre key={item.key} className="schema-sample-popover__pre">
                        {String(item.value ?? '')}
                      </pre>
                    ))
                  ) : (
                    <div>{t('No sample values available for this column')}</div>
                  )}
                </div>
              }
              title={`${t('Sample data for')} ${record.name}`}
              trigger="click"
              placement="right"
              overlayClassName="sample-data-popover"
              getPopupContainer={triggerNode => triggerNode.parentElement || document.body}
            >
              <BorderlessButton className="schema-popover-trigger">{t('View')}</BorderlessButton>
            </Popover>
          );
        }
        const sample = getFirstSample(record.name);
        return sample ? <span title={sample}>{sample}</span> : '';
      }
    },
    {
      title: '',
      dataIndex: 'sample2',
      key: 'sample2',
      render: (_: string | undefined, record: ColumnDef & { key: string }) => {
        if (loadingSamples) {
          return (
            <span className="schema-sample--loading" title={t('Loading sample values...')}>
              {t('Loading...')}
            </span>
          );
        }
        if (isStructType(record.type)) {
          return '';
        }
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

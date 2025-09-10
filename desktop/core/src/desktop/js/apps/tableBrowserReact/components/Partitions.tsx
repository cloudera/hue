// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { Select, Space, Tag } from 'antd';
import Button from 'cuix/dist/components/Button/Button';
import Tooltip from 'cuix/dist/components/Tooltip';
import Modal from 'cuix/dist/components/Modal';
import EmptyState from 'cuix/dist/components/EmptyState';
import { i18nReact } from '../../../utils/i18nReact';
import Loading from 'cuix/dist/components/Loading';
import dataCatalog from '../../../catalog/dataCatalog';
import type { Connector, Compute, Namespace } from '../../../config/types';
import type { Analysis, Partitions as PartitionsType } from '../../../catalog/DataCatalogEntry';
import huePubSub from '../../../utils/huePubSub';
import { post } from '../../../api/utils';
// import { PrimaryButton } from 'cuix/dist/components/Button';
import PaginatedTable, {
  type ColumnProps as PaginatedColumnProps,
  SortOrder
} from '../../../reactComponents/PaginatedTable/PaginatedTable';
import Filter from 'cuix/dist/components/Filter';
import type { FilterOutput } from 'cuix/dist/components/Filter/types';

export interface PartitionsProps {
  connector?: Connector | null;
  namespace?: Namespace | null;
  compute?: Compute | null;
  database?: string;
  table?: string;
  // Optional write access gate; if undefined, actions are shown and server enforces
  canWrite?: boolean;
  onCountChange?: (count: number) => void;
}

const Partitions = ({
  connector,
  namespace,
  compute,
  database,
  table,
  canWrite,
  onCountChange
}: PartitionsProps): JSX.Element => {
  const [loading, setLoading] = useState(false);
  const [partitions, setPartitions] = useState<PartitionsType | null>(null);
  const [selectedSpecs, setSelectedSpecs] = useState<string[]>([]);
  const [filters, setFilters] = useState<{ column?: string; value?: string }[]>([]);
  const [searchText, setSearchText] = useState('');
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [addFacetColumn, setAddFacetColumn] = useState<string | undefined>(undefined);

  const [keyDefs, setKeyDefs] = useState<{ name: string; type?: string }[]>([]);

  useEffect(() => {
    const fetch = async () => {
      if (!connector || !namespace || !compute || !database || !table) {
        setPartitions(null);
        return;
      }
      setLoading(true);
      try {
        const entry = await dataCatalog.getEntry({
          connector,
          namespace,
          compute,
          path: [database, table]
        });
        const parts = await entry.getPartitions();
        setPartitions(parts);
        try {
          const analysis: Analysis = await entry.getAnalysis({ silenceErrors: true });
          const cols = (analysis?.cols || []) as { name: string; type: string }[];
          const map = new Map(cols.map(c => [c.name, c.type] as const));
          const defs = (parts?.partition_keys_json || []).map(name => ({
            name,
            type: map.get(name)
          }));
          setKeyDefs(defs);
        } catch (e) {
          setKeyDefs((parts?.partition_keys_json || []).map(name => ({ name })));
        }
        if (onCountChange) {
          onCountChange((parts?.partition_values_json || []).length);
        }
      } catch (err) {
        setPartitions(null);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [connector, namespace, compute, database, table]);

  const { t } = i18nReact.useTranslation();

  const isImpala = useMemo(() => {
    const id = (connector as unknown as { id?: string })?.id;
    const type = (connector as unknown as { type?: string })?.type;
    return id === 'impala' || type === 'impala';
  }, [connector]);

  const keyToIndex = useMemo(() => {
    const map: Record<string, number> = {};
    (partitions?.partition_keys_json || []).forEach((k, idx) => (map[k] = idx));
    return map;
  }, [partitions]);

  const allRows = useMemo(() => partitions?.partition_values_json || [], [partitions]);

  const availableFilterValues = useCallback(
    (column?: string): string[] => {
      if (!column) {
        return [];
      }
      const idx = keyToIndex[column];
      if (typeof idx !== 'number') {
        return [];
      }
      const set = new Set<string>();
      allRows.forEach(r => {
        const v = r.columns[idx];
        if (typeof v === 'string') {
          set.add(v);
        }
      });
      return Array.from(set).sort();
    },
    [allRows, keyToIndex]
  );

  const filteredRows = useMemo(() => {
    let rows = allRows;
    // Apply facet filters (AND)
    filters.forEach(f => {
      if (!f.column || typeof keyToIndex[f.column] !== 'number' || !f.value) {
        return;
      }
      const idx = keyToIndex[f.column];
      rows = rows.filter(r => String(r.columns[idx]) === String(f.value));
    });
    if (searchText) {
      const q = searchText.toLowerCase();
      rows = rows.filter(r => {
        if (r.partitionSpec.toLowerCase().includes(q)) {
          return true;
        }
        return r.columns.some(c => String(c).toLowerCase().includes(q));
      });
    }
    return rows;
  }, [allRows, filters, keyToIndex, searchText]);

  // Note: equality helpers removed; not used in current implementation

  type PartitionRow = {
    key: string;
    values: string;
    spec: string;
    browseUrl: string;
    notebookUrl: string;
  };

  const valuesData: PartitionRow[] = filteredRows.map(row => ({
    key: row.partitionSpec,
    values: `[${row.columns.map(v => `'${v}'`).join(', ')}]`,
    spec: row.partitionSpec,
    browseUrl: row.browseUrl,
    notebookUrl: row.notebookUrl
  }));

  const columns: PaginatedColumnProps<PartitionRow>[] = [
    {
      title: t('Values'),
      dataIndex: 'values',
      key: 'values',
      sorter: true,
      render: (_: string, record) => (
        <Button onClick={() => openEditorForPartition(record.spec)}>
          {_[0] === '[' ? _ : `[${_}]`}
        </Button>
      )
    },
    {
      title: t('Spec'),
      dataIndex: 'spec',
      key: 'spec',
      sorter: true
    },
    ...(!isImpala
      ? ([
          {
            title: t('Browse'),
            dataIndex: 'browseUrl',
            key: 'browse',
            render: (url: string) => (
              <Tooltip title={t('Browse partition files')}>
                <Button onClick={() => browsePartitionFolder(url)}>{t('Files')}</Button>
              </Tooltip>
            )
          }
        ] as PaginatedColumnProps<PartitionRow>[])
      : [])
  ];

  const [sortByColumn, setSortByColumn] =
    useState<PaginatedColumnProps<PartitionRow>['dataIndex']>();
  const [sortOrder, setSortOrder] = useState<SortOrder>(null);
  const sortedData = useMemo(() => {
    if (!sortByColumn || !sortOrder) {
      return valuesData;
    }
    const data = valuesData.slice();
    const key = String(sortByColumn);
    data.sort((a, b) =>
      String((a as Record<string, unknown>)[key]).localeCompare(
        String((b as Record<string, unknown>)[key])
      )
    );
    if (sortOrder === 'descend') {
      data.reverse();
    }
    return data;
  }, [valuesData, sortByColumn, sortOrder]);

  const [pageNumber, setPageNumber] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const totalSize = sortedData.length;
  const totalPages = Math.max(Math.ceil(totalSize / pageSize), 1);
  const start = (pageNumber - 1) * pageSize;
  const pageData = sortedData.slice(start, start + pageSize);

  const onConfirmDrop = async () => {
    try {
      const url = `/metastore/table/${encodeURIComponent(database || '')}/${encodeURIComponent(
        table || ''
      )}/partitions/drop`;
      const params = new URLSearchParams();
      params.set('format', 'json');
      params.set('is_embeddable', 'true');
      const type = ((connector as unknown as { id?: string })?.id ||
        (connector as unknown as { type?: string })?.type ||
        'hive') as string;
      params.set('source_type', type);
      if (namespace) {
        params.set('namespace', JSON.stringify(namespace));
      }
      if (compute) {
        params.set('cluster', JSON.stringify(compute));
      }
      selectedSpecs.forEach(spec => params.append('partition_selection', spec));
      await post(url, params, { silenceErrors: false });
      setSelectedSpecs([]);
      setConfirmOpen(false);
    } catch (e) {
      setConfirmOpen(false);
    }
  };

  const openEditorForPartition = (spec: string): void => {
    if (!database || !table) {
      return;
    }
    const where = spec
      .split('/')
      .map(pair => pair.split('='))
      .filter(([k, v]) => k && typeof v !== 'undefined')
      .map(([k, v]) => `${k}='${String(v).replace(/'/g, "''")}'`)
      .join(' AND ');
    const stmt = `SELECT * FROM ${database}.${table} WHERE ${where} LIMIT 1000;`;
    const type = ((connector as unknown as { id?: string })?.id ||
      (connector as unknown as { type?: string })?.type ||
      'hive') as string;
    huePubSub.publish('open.editor.new.query', {
      type,
      statementType: 'text',
      statement: stmt
    });
  };

  const browsePartitionFolder = (url: string): void => {
    if (!url) {
      return;
    }
    window.open(url, '_blank');
  };

  return (
    <Loading spinning={loading}>
      <div style={{ marginBottom: 8 }}>
        {(partitions?.partition_keys_json || []).map((k, idx) => (
          <Tag key={idx}>{k}</Tag>
        ))}
      </div>

      {!!keyDefs.length && (
        <div className="hue-table-browser__partitions-keys" style={{ marginBottom: 8 }}>
          <h4 style={{ margin: '0 0 8px' }}>{t('Columns')}</h4>
          <PaginatedTable<{ key: string; index: number; name: string; type?: string }>
            data={keyDefs.map((k, i) => ({ key: `${i}-${k.name}`, index: i + 1, ...k }))}
            columns={[
              { title: '#', dataIndex: 'index', key: 'index' },
              { title: t('Name'), dataIndex: 'name', key: 'name' },
              { title: t('Type'), dataIndex: 'type', key: 'type' }
            ]}
            rowKey="key"
            pagination={{
              pageStats: {
                pageNumber: 1,
                totalPages: 1,
                pageSize: keyDefs.length,
                totalSize: keyDefs.length
              }
            }}
          />
        </div>
      )}

      <h4 style={{ margin: '16px 0 8px' }}>{t('Partitions')}</h4>

      <div className="hue-table-browser__filter" style={{ marginBottom: 8 }}>
        <Filter
          search={{ placeholder: t('Filter partitions') }}
          onChange={(output: FilterOutput) => {
            const searchValue = String(
              (output as unknown as { search?: unknown[] }).search?.[0] ?? ''
            );
            if (searchValue !== searchText) {
              setSearchText(searchValue);
            }
          }}
        />
      </div>
      <div style={{ marginBottom: 8, display: 'flex', justifyContent: 'space-between' }}>
        <Space>
          <Select
            style={{ minWidth: 200 }}
            placeholder={t('Add filter')}
            value={addFacetColumn}
            onChange={val => setAddFacetColumn(val)}
            options={(partitions?.partition_keys_json || [])
              .filter(k => !filters.some(f => f.column === k))
              .map(k => ({ label: k, value: k }))}
          />
          <Button
            disabled={!addFacetColumn}
            onClick={() => {
              if (!addFacetColumn) {
                return;
              }
              const next = [...filters, { column: addFacetColumn, value: undefined }];
              setFilters(next);
              setAddFacetColumn(undefined);
            }}
          >
            {t('Add Filter')}
          </Button>
        </Space>
        {canWrite !== false && (
          <Tooltip title={t('Delete the selected partitions')}>
            <Button disabled={!selectedSpecs.length} onClick={() => setConfirmOpen(true)}>
              {t('Drop partition(s)')}
            </Button>
          </Tooltip>
        )}
      </div>
      {!!filters.length && (
        <div style={{ marginBottom: 8 }}>
          {filters.map((f, idx) => (
            <div
              key={`facet-${f.column}-${idx}`}
              style={{ display: 'flex', gap: 8, marginBottom: 8 }}
            >
              <div style={{ minWidth: 140, alignSelf: 'center' }}>{f.column}</div>
              <Select
                showSearch
                style={{ minWidth: 240 }}
                placeholder={t('Select value')}
                value={f.value}
                onChange={val => {
                  const next = filters.slice();
                  next[idx] = { ...next[idx], value: val };
                  setFilters(next);
                }}
                options={availableFilterValues(f.column).map(v => ({ label: v, value: v }))}
                filterOption={(input, option) =>
                  (option?.label as string).toLowerCase().includes(input.toLowerCase())
                }
              />
              <Button onClick={() => setFilters(filters.filter((_, i) => i !== idx))}>
                {t('Remove')}
              </Button>
            </div>
          ))}
        </div>
      )}
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 8 }}>
        {canWrite !== false && (
          <Tooltip title={t('Delete the selected partitions')}>
            <Button disabled={!selectedSpecs.length} onClick={() => setConfirmOpen(true)}>
              {t('Drop partition(s)')}
            </Button>
          </Tooltip>
        )}
      </div>

      {valuesData.length === 0 ? (
        <EmptyState title={t('No partitions')} />
      ) : (
        <PaginatedTable<PartitionRow>
          data={pageData}
          columns={columns}
          rowKey="key"
          onRowSelect={rows => setSelectedSpecs(rows.map(r => r.key))}
          sortByColumn={sortByColumn}
          setSortByColumn={setSortByColumn}
          sortOrder={sortOrder}
          setSortOrder={setSortOrder}
          pagination={{
            pageStats: { pageNumber, totalPages, pageSize, totalSize },
            setPageNumber,
            setPageSize
          }}
        />
      )}

      <Modal
        title={t('Confirm action')}
        open={confirmOpen}
        onOk={onConfirmDrop}
        onCancel={() => setConfirmOpen(false)}
        okButtonProps={{ danger: true }}
      >
        {t('Do you really want to delete the selected partitions?')}
      </Modal>
    </Loading>
  );
};
export default Partitions;

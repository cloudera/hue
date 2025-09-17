// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { ConfigProvider } from 'antd';
import i18n from 'cuix/dist/utils/i18n';
import Button from 'cuix/dist/components/Button/Button';
import { BorderlessButton } from 'cuix/dist/components/Button';
import Tooltip from 'cuix/dist/components/Tooltip';
import Modal from 'cuix/dist/components/Modal';
import EmptyState from 'cuix/dist/components/EmptyState';
import { i18nReact } from '../../../../utils/i18nReact';
import Loading from 'cuix/dist/components/Loading';
import dataCatalog from '../../../../catalog/dataCatalog';
import type { Connector, Compute, Namespace } from '../../../../config/types';
import type { Analysis, Partitions as PartitionsType } from '../../../../catalog/DataCatalogEntry';
import huePubSub from '../../../../utils/huePubSub';
import { post } from '../../../../api/utils';
// import { PrimaryButton } from 'cuix/dist/components/Button';
import PaginatedTable, {
  type ColumnProps as PaginatedColumnProps,
  SortOrder
} from '../../../../reactComponents/PaginatedTable/PaginatedTable';
import Filter from 'cuix/dist/components/Filter';
import type { FilterOutput, BasicFacet } from 'cuix/dist/components/Filter/types';
import './Partitions.scss';

export interface PartitionsProps {
  connector?: Connector | null;
  namespace?: Namespace | null;
  compute?: Compute | null;
  database?: string;
  table?: string;
  // Optional write access gate; if undefined, actions are shown and server enforces
  canWrite?: boolean;
  onCountChange?: (count: number) => void;
  // Triggers refetch after table details refresh completes
  isRefreshing?: boolean;
}

const Partitions = ({
  connector,
  namespace,
  compute,
  database,
  table,
  canWrite,
  onCountChange,
  isRefreshing
}: PartitionsProps): JSX.Element => {
  const [loading, setLoading] = useState(false);
  const [partitions, setPartitions] = useState<PartitionsType | null>(null);
  const [selectedSpecs, setSelectedSpecs] = useState<string[]>([]);
  const [filterOutput, setFilterOutput] = useState<FilterOutput>({});
  const [confirmOpen, setConfirmOpen] = useState(false);

  const [keyDefs, setKeyDefs] = useState<{ name: string; type?: string }[]>([]);

  useEffect(() => {
    const fetch = async () => {
      if (isRefreshing) {
        return; // Wait until parent refresh has completed to avoid stale cache reads
      }
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
  }, [connector, namespace, compute, database, table, isRefreshing]);

  const { t } = i18nReact.useTranslation();

  // Initialize cuix i18n system
  useEffect(() => {
    try {
      if (i18n && typeof i18n.extend === 'function') {
        i18n.extend({
          'label.more': 'More',
          'label.filterBy': 'Filter by',
          'label.clear': 'Clear',
          'label.search': 'Search',
          'label.selected': 'Selected'
        });
      }
    } catch (error) {
      console.warn('Failed to initialize cuix i18n:', error);
    }
  }, []);

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

  // Create facets for all partition columns
  const facets = useMemo((): BasicFacet[] => {
    return keyDefs.map(keyDef => ({
      label: keyDef.name,
      items: availableFilterValues(keyDef.name),
      multiple: true,
      search: true
    }));
  }, [keyDefs, availableFilterValues]);

  const handleFilterChange = useCallback((output: FilterOutput) => {
    // Safely handle the filter output to prevent undefined property errors
    if (output && typeof output === 'object') {
      setFilterOutput(output);
    } else {
      setFilterOutput({});
    }
  }, []);

  const filteredRows = useMemo(() => {
    let rows = allRows;

    // Apply facet filters from FilterOutput
    Object.entries(filterOutput).forEach(([facetLabel, facetValues]) => {
      if (!facetValues || !Array.isArray(facetValues) || facetValues.length === 0) {
        return;
      }

      const columnIndex = keyToIndex[facetLabel];
      if (typeof columnIndex !== 'number') {
        return;
      }

      // Filter rows that match any of the selected values for this facet (OR within facet)
      rows = rows.filter(r => {
        const cellValue = String(r.columns[columnIndex]);
        return facetValues.some(filterValue => cellValue === String(filterValue));
      });
    });

    // Apply search text filter (from the search facet if present)
    const searchValues = filterOutput?.search;
    if (searchValues && Array.isArray(searchValues) && searchValues.length > 0) {
      const searchText = String(searchValues[0]).toLowerCase();
      if (searchText) {
        rows = rows.filter(r => {
          if (r.partitionSpec.toLowerCase().includes(searchText)) {
            return true;
          }
          return r.columns.some(c => String(c).toLowerCase().includes(searchText));
        });
      }
    }

    return rows;
  }, [allRows, filterOutput, keyToIndex]);

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
        <BorderlessButton onClick={() => openEditorForPartition(record.spec)}>
          {_[0] === '[' ? _ : `[${_}]`}
        </BorderlessButton>
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
                <BorderlessButton onClick={() => browsePartitionFolder(url)}>
                  {t('Files')}
                </BorderlessButton>
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
      {!!keyDefs.length && (
        <div className="hue-table-browser__partitions-keys" style={{ marginBottom: 24 }}>
          <h3 className="hue-h3">{t('Columns')}</h3>
          <PaginatedTable<{ key: string; index: number; name: string; type?: string }>
            data={keyDefs.map((k, i) => ({ key: `${i}-${k.name}`, index: i + 1, ...k }))}
            columns={[
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

      <h3 className="hue-h3" style={{ marginBottom: 16 }}>
        {t('Partitions')}
      </h3>

      <div className={`hue-table-browser__filter-and-actions${loading ? ' disabled' : ''}`}>
        <div className="cuix-filter">
          <ConfigProvider
            getPopupContainer={triggerNode => triggerNode?.parentElement || document.body}
          >
            <Filter
              key={`filter-${facets.length}`}
              search={{ placeholder: t('Filter partitions') }}
              facets={facets}
              onChange={handleFilterChange}
            />
          </ConfigProvider>
        </div>

        {canWrite !== false && (
          <div className="hue-table-browser__actions">
            <Tooltip title={t('Delete the selected partitions')}>
              <Button disabled={!selectedSpecs.length} onClick={() => setConfirmOpen(true)}>
                {t('Drop partition(s)')}
              </Button>
            </Tooltip>
          </div>
        )}
      </div>

      {valuesData.length === 0 ? (
        <EmptyState
          title={t('No partitions')}
          subtitle={t('This table isn’t partitioned or no partitions are available.')}
        />
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

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

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Col, Row } from 'antd';
import Button from 'cuix/dist/components/Button/Button';
import Loading from 'cuix/dist/components/Loading';
//
//

import DataBrowserIcon from '@cloudera/cuix-core/icons/react/DataBrowserIcon';

import { i18nReact } from '../../utils/i18nReact';
import CommonHeader from '../../reactComponents/CommonHeader/CommonHeader';
import changeURL from '../../utils/url/changeURL';
import { buildTableBrowserPath, parseTableBrowserPath } from './utils/routing';
import { useDataCatalog } from '../../utils/hooks/useDataCatalog/useDataCatalog';
import Breadcrumbs from './components/Breadcrumbs';
import Tabs, { TabKey } from './components/Tabs';
import Overview from './components/Overview';
import SampleGrid from './components/SampleGrid';
// import DetailsSchema from './components/DetailsSchema';
import DetailsProperties from './components/DetailsProperties';
import Partitions from './components/Partitions';
import SourcesList from './components/SourcesList';
import DatabasesList from './components/DatabasesList';
import TablesList from './components/TablesList';
import dataCatalog from '../../catalog/dataCatalog';
import type { Analysis, SampleMeta } from '../../catalog/DataCatalogEntry';
import ViewSql from './components/ViewSql';
import Queries from './components/Queries';
import Privileges from './components/Privileges';
import huePubSub from '../../utils/huePubSub';
import { GLOBAL_ERROR_TOPIC, GLOBAL_INFO_TOPIC } from '../../reactComponents/GlobalAlert/events';
import formatBytes from '../../utils/formatBytes';
import { formatTimestamp } from '../../utils/dateTimeUtils';

import './TableBrowserPage.scss';

// routing helpers moved to utils/routing

const TableBrowserPage = (): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [locationPath, setLocationPath] = useState<string>(window.location.pathname);
  const route = useMemo(() => parseTableBrowserPath(locationPath), [locationPath]);

  useEffect(() => {
    const onPopState = () => setLocationPath(window.location.pathname);
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  const {
    loading: loadingStates,
    databases,
    database: currentDb,
    setDatabase: selectDb,
    tables,
    connector,
    namespace,
    compute,
    connectors,
    setConnector,
    reloadDatabases,
    reloadTables
  } = useDataCatalog({ autoSelectFirstDatabase: false });

  const [table, setTable] = useState<string | undefined>(route.table);
  const [activeTab, setActiveTab] = useState<TabKey>('overview');
  const [dbFilter, setDbFilter] = useState('');
  const [tableFilter, setTableFilter] = useState('');
  const [loadingData, setLoadingData] = useState(false);
  const [dbPageSize, setDbPageSize] = useState(50);
  const [dbPageNumber, setDbPageNumber] = useState(1);
  const [dbDescriptions, setDbDescriptions] = useState<Record<string, string>>({});
  const [editingDb, setEditingDb] = useState<string | null>(null);
  const [editingValue, setEditingValue] = useState('');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [tableDescriptions, setTableDescriptions] = useState<Record<string, string>>({});
  const [editingTableName, setEditingTableName] = useState<string | null>(null);
  const [editingTableValue, setEditingTableValue] = useState('');
  const [tablePageSize, setTablePageSize] = useState(50);
  const [tablePageNumber, setTablePageNumber] = useState(1);
  const [sourceFilter, setSourceFilter] = useState('');
  const [sourcePageSize, setSourcePageSize] = useState(50);
  const [sourcePageNumber, setSourcePageNumber] = useState(1);
  // Removed forceShowSources per follow-up TODO; derive strictly from URL

  const updatePath = useCallback(
    (nextDatabase?: string, nextTable?: string) => {
      const urlPathname = window.location.pathname;
      const baseIdx = urlPathname.indexOf('/tablebrowser');
      const base = baseIdx !== -1 ? urlPathname.substring(0, baseIdx) : '';
      const sourceType =
        route.sourceType ||
        (connector &&
          ((connector as unknown as { id?: string }).id ||
            (connector as unknown as { type?: string }).type)) ||
        '';
      changeURL(buildTableBrowserPath(base, sourceType, nextDatabase, nextTable));
      setLocationPath(window.location.pathname);
    },
    [locationPath, route.sourceType, connector]
  );

  // Initialize from URL on mount (partial sync)
  useEffect(() => {
    if (route.database) {
      selectDb(route.database);
    }
    if (route.table) {
      setTable(route.table);
    }
    const params = new URLSearchParams(window.location.search);
    const tabParam = (params.get('tab') as TabKey) || 'overview';
    setActiveTab(tabParam);
  }, []);

  // Apply sourceType from URL to connector selection once connectors are loaded
  useEffect(() => {
    if (route.sourceType && connectors && connectors.length && !connector) {
      const wanted = connectors.find(c => {
        const connectorId = (c as unknown as { id?: string }).id;
        return c.type === route.sourceType || connectorId === route.sourceType;
      });
      if (wanted) {
        setConnector(wanted as unknown as never);
      }
    }
  }, [route.sourceType, connectors, connector]);

  // Ensure database matches URL when the list is available
  useEffect(() => {
    if (route.database && databases && databases.length && currentDb !== route.database) {
      selectDb(route.database);
    }
  }, [databases]);

  // If no DB provided in URL, avoid auto-selecting the first DB, and don't force a default source
  useEffect(() => {
    if (!route.database && currentDb) {
      selectDb(undefined);
      const urlPathname = window.location.pathname;
      const baseIdx = urlPathname.indexOf('/tablebrowser');
      const base = baseIdx !== -1 ? urlPathname.substring(0, baseIdx) : '';
      if (route.sourceType) {
        changeURL([base, '/tablebrowser', `/${encodeURIComponent(route.sourceType)}`].join(''));
      } else {
        changeURL([base, '/tablebrowser'].join(''));
      }
    }
  }, [currentDb]);

  // Removed pick default action; DB is not auto-selected.

  // Removed unused onPickMockTable (tables now come from the catalog)

  const onTabChange = (key: TabKey) => {
    const url = new URL(window.location.href);
    url.searchParams.set('tab', key);
    changeURL(url.pathname + url.search);
    setActiveTab(key);
  };

  // Spinner lifecycle handled explicitly in onRefresh

  // Focus management after crumb navigation
  const panelRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    if (panelRef.current) {
      panelRef.current.focus({ preventScroll: false } as unknown as FocusOptions);
    }
  }, [route.sourceType, currentDb, table]);

  // Prefetch database descriptions (Navigator or source metadata) when listing databases
  useEffect(() => {
    const loadDbDescriptions = async () => {
      if (!connector || !namespace || !compute || !databases || currentDb) {
        return;
      }
      try {
        const sourceEntry = await dataCatalog.getEntry({
          connector,
          namespace,
          compute,
          path: []
        });
        await sourceEntry.getChildren({ silenceErrors: true });
        const children = await sourceEntry.loadNavigatorMetaForChildren({ silenceErrors: true });
        const map: Record<string, string> = {};
        children.forEach(child => {
          if ((child as unknown as { path: string[] }).path?.length === 1) {
            map[child.name] = child.getResolvedComment();
          }
        });
        setDbDescriptions(map);
      } catch {}
    };
    loadDbDescriptions();
  }, [connector, namespace, compute, databases, currentDb]);

  const saveDbDescription = async (dbName: string, value: string) => {
    setEditingDb(null);
    // Optimistic update
    setDbDescriptions(prev => ({ ...prev, [dbName]: value }));
    try {
      const entry = await dataCatalog.getEntry({
        connector,
        namespace,
        compute,
        path: [dbName]
      });
      await entry.setComment(value, { silenceErrors: true });
      huePubSub.publish(GLOBAL_INFO_TOPIC, { message: t('Description saved') });
    } catch {
      // Revert on error
      setDbDescriptions(prev => ({ ...prev, [dbName]: prev[dbName] }));
      huePubSub.publish(GLOBAL_ERROR_TOPIC, { message: t('Failed to save description') });
    }
  };

  // Prefetch table descriptions when listing tables for a selected DB
  useEffect(() => {
    const loadTableDescriptions = async () => {
      if (!connector || !namespace || !compute || !currentDb || table) {
        return;
      }
      try {
        const dbEntry = await dataCatalog.getEntry({
          connector,
          namespace,
          compute,
          path: [currentDb]
        });
        await dbEntry.getChildren({ silenceErrors: true });
        const children = await dbEntry.loadNavigatorMetaForChildren({ silenceErrors: true });
        const map: Record<string, string> = {};
        children.forEach(child => {
          if ((child as unknown as { path: string[] }).path?.length === 2) {
            map[child.name] = child.getResolvedComment();
          }
        });
        setTableDescriptions(map);
      } catch {}
    };
    loadTableDescriptions();
  }, [connector, namespace, compute, currentDb, table, tables]);

  const saveTableDescription = async (tblName: string, value: string) => {
    setEditingTableName(null);
    // Optimistic update
    setTableDescriptions(prev => ({ ...prev, [tblName]: value }));
    try {
      const entry = await dataCatalog.getEntry({
        connector,
        namespace,
        compute,
        path: [currentDb as string, tblName]
      });
      await entry.setComment(value, { silenceErrors: true });
      huePubSub.publish(GLOBAL_INFO_TOPIC, { message: t('Description saved') });
    } catch {
      setTableDescriptions(prev => ({ ...prev, [tblName]: prev[tblName] }));
      huePubSub.publish(GLOBAL_ERROR_TOPIC, { message: t('Failed to save description') });
    }
  };

  // Fallback: ensure DB comments via describe for visible page items
  useEffect(() => {
    if (!databases || currentDb) {
      return;
    }
    const filtered = (databases || []).filter(db =>
      dbFilter ? db.toLowerCase().includes(dbFilter.toLowerCase()) : true
    );
    const dbData = filtered.map(name => ({ key: name, name }));
    const dbTotalSize = dbData.length;
    const dbTotalPages = Math.max(Math.ceil(dbTotalSize / dbPageSize), 1);
    const pageNumber = Math.min(dbPageNumber, dbTotalPages);
    const start = (pageNumber - 1) * dbPageSize;
    const pageData = dbData.slice(start, start + dbPageSize);

    pageData.forEach(({ name }) => {
      if (typeof dbDescriptions[name] === 'undefined' && connector && namespace && compute) {
        (async () => {
          try {
            const entry = await dataCatalog.getEntry({
              connector,
              namespace,
              compute,
              path: [name]
            });
            const describe: unknown = await entry.getAnalysis({ silenceErrors: true });
            const comment = (describe as unknown as { comment?: string }).comment || '';
            if (typeof comment !== 'undefined') {
              setDbDescriptions(prev => ({ ...prev, [name]: comment }));
            }
          } catch {}
        })();
      }
    });
  }, [
    databases,
    dbFilter,
    dbPageNumber,
    dbPageSize,
    connector,
    namespace,
    compute,
    currentDb,
    dbDescriptions
  ]);

  // Fallback: ensure table comments via describe for visible page items
  useEffect(() => {
    if (!currentDb || !tables || table) {
      return;
    }
    const filtered = (tables || []).filter(item =>
      tableFilter ? item.name.toLowerCase().includes(tableFilter.toLowerCase()) : true
    );
    const tableData = filtered.map(item => ({ key: item.name, name: item.name }));
    const totalSize = tableData.length;
    const totalPages = Math.max(Math.ceil(totalSize / tablePageSize), 1);
    const pageNumber = Math.min(tablePageNumber, totalPages);
    const start = (pageNumber - 1) * tablePageSize;
    const pageData = tableData.slice(start, start + tablePageSize);

    pageData.forEach(({ name }) => {
      if (typeof tableDescriptions[name] === 'undefined' && connector && namespace && compute) {
        (async () => {
          try {
            const entry = await dataCatalog.getEntry({
              connector,
              namespace,
              compute,
              path: [currentDb, name]
            });
            const describe: unknown = await entry.getAnalysis({ silenceErrors: true });
            const comment = (describe as unknown as { comment?: string }).comment || '';
            if (typeof comment !== 'undefined') {
              setTableDescriptions(prev => ({ ...prev, [name]: comment }));
            }
          } catch {}
        })();
      }
    });
  }, [
    currentDb,
    tables,
    tableFilter,
    tablePageNumber,
    tablePageSize,
    connector,
    namespace,
    compute,
    table,
    tableDescriptions
  ]);

  // Load table analysis and sample when table is selected
  const [overviewProps, setOverviewProps] = useState<{
    properties?: { name: string; value: string }[];
    stats?: {
      files?: number | string;
      rows?: number | string;
      totalSize?: string;
      lastUpdated?: string;
    };
    hdfsLink?: string;
  }>();
  const [sampleData, setSampleData] = useState<{
    headers: string[];
    rows: (string | number | null)[][];
  }>();
  const [detailsColumns, setDetailsColumns] = useState<
    {
      name: string;
      type: string;
      comment?: string;
      sample?: string;
    }[]
  >([]);
  const [detailsProperties, setDetailsProperties] = useState<{ name: string; value: string }[]>([]);
  const [detailsSections, setDetailsSections] = useState<{
    baseInfo?: { name: string; value: string }[];
    tableParameters?: { name: string; value: string }[];
    storageInfo?: { name: string; value: string }[];
    storageDescParams?: { name: string; value: string }[];
  }>({});

  const fetchData = useCallback(async () => {
    setLoadingData(true);
    if (!currentDb || !table || !connector || !namespace || !compute) {
      setOverviewProps(undefined);
      setSampleData(undefined);
      setDetailsColumns([]);
      setLoadingData(false);
      return;
    }
    try {
      const entry = await dataCatalog.getEntry({
        connector,
        namespace,
        compute,
        path: [currentDb, table]
      });
      const analysis: Analysis = await entry.getAnalysis({ silenceErrors: true });
      const analysisDetails = (
        analysis as unknown as {
          details?: { properties?: Record<string, string>; stats?: Record<string, string> };
        }
      ).details;
      const isPartitioned = analysisDetails?.properties?.partitioned;
      const tableType = analysisDetails?.properties?.table_type;
      const createdBy = analysisDetails?.properties?.owner || 'hive';
      const createdTime = analysisDetails?.stats?.created_time;
      const createdTimeFormatted = createdTime
        ? (() => {
            const numeric = Number(createdTime);
            if (!isNaN(numeric) && isFinite(numeric)) {
              const ms = numeric < 1e12 ? numeric * 1000 : numeric;
              return formatTimestamp(new Date(ms));
            }
            const d = new Date(createdTime as unknown as string);
            return isNaN(d.getTime()) ? String(createdTime) : formatTimestamp(d);
          })()
        : undefined;
      const props = [
        { name: t('Partitioned Table'), value: isPartitioned ? t('Yes') : t('No') },
        {
          name: t('Managed and stored in location'),
          value:
            (tableType === 'MANAGED_TABLE' ? t('Managed') + ' · ' : t('External') + ' · ') +
            ((analysis as unknown as { hdfs_link?: string })?.hdfs_link || '-')
        },
        {
          name: t('Created'),
          value: createdTimeFormatted
            ? `${t('by')} ${createdBy} ${t('on')} ${createdTimeFormatted}`
            : '-'
        }
      ];
      const hdfsLink = (analysis as unknown as { hdfs_link?: string })?.hdfs_link;
      const detailStats = (analysis as unknown as { details?: { stats?: Record<string, string> } })
        ?.details?.stats;
      const stats = detailStats
        ? (() => {
            const files =
              (detailStats as Record<string, string>).num_files ||
              (detailStats as Record<string, string>).numFiles ||
              (detailStats as Record<string, string>).files;
            const rows =
              (detailStats as Record<string, string>).num_rows ||
              (detailStats as Record<string, string>).numRows ||
              (detailStats as Record<string, string>).rows;
            const rawTotalSize =
              (detailStats as Record<string, string>).total_size ||
              (detailStats as Record<string, string>).totalSize ||
              (detailStats as Record<string, string>).size;
            const totalSize = (() => {
              const n = Number(rawTotalSize);
              return !isNaN(n) && isFinite(n)
                ? formatBytes(n)
                : (rawTotalSize as unknown as string);
            })();
            const rawLastUpdated =
              (detailStats as Record<string, string>).last_modified_time ||
              (detailStats as Record<string, string>).lastModified ||
              (detailStats as Record<string, string>).lastUpdated;
            const lastUpdated = (() => {
              const n = Number(rawLastUpdated);
              if (!isNaN(n) && isFinite(n)) {
                const ms = n < 1e12 ? n * 1000 : n;
                return formatTimestamp(new Date(ms));
              }
              const d = new Date(rawLastUpdated as unknown as string);
              return isNaN(d.getTime())
                ? (rawLastUpdated as unknown as string)
                : formatTimestamp(d);
            })();
            return { files, rows, totalSize, lastUpdated };
          })()
        : undefined;
      const columnsForOverview = (analysis.cols || []).map(c => ({
        name: (c as unknown as { name: string }).name,
        type: (c as unknown as { type: string }).type,
        comment: (c as unknown as { comment?: string }).comment
      }));
      setOverviewProps({ properties: props, hdfsLink, stats });
      // Build structured Details sections similar to legacy Metastore
      const rawProps = (analysisDetails?.properties || {}) as Record<string, unknown>;
      const baseInfo: { name: string; value: string }[] = [];
      const storageInfo: { name: string; value: string }[] = [];
      const storageDescParams: { name: string; value: string }[] = [];
      const tableParameters: { name: string; value: string }[] = [];

      const add = (arr: { name: string; value: string }[], name: string, value?: unknown) => {
        if (typeof value !== 'undefined' && value !== null && String(value) !== '') {
          arr.push({ name, value: String(value) });
        }
      };

      // Detailed Table Information
      add(baseInfo, t('Database'), currentDb || '');
      add(baseInfo, t('OwnerType'), rawProps.owner_type || rawProps.ownertype);
      add(baseInfo, t('Owner'), rawProps.owner);
      add(baseInfo, t('CreateTime'), createdTimeFormatted);
      const lastAccessRaw =
        (rawProps as Record<string, unknown>).last_access_time ||
        (rawProps as Record<string, unknown>).lastAccessTime ||
        'UNKNOWN';
      const lastAccessFormatted = (() => {
        if (lastAccessRaw === 'UNKNOWN') {
          return 'UNKNOWN';
        }
        const n = Number(lastAccessRaw as unknown as string);
        if (!isNaN(n) && isFinite(n)) {
          const ms = n < 1e12 ? n * 1000 : n;
          return formatTimestamp(new Date(ms));
        }
        const d = new Date(lastAccessRaw as unknown as string);
        return isNaN(d.getTime()) ? String(lastAccessRaw) : formatTimestamp(d);
      })();
      add(baseInfo, t('LastAccessTime'), lastAccessFormatted);
      add(baseInfo, t('Retention'), rawProps.retention);
      add(baseInfo, t('Location'), (analysis as unknown as { hdfs_link?: string })?.hdfs_link);
      add(baseInfo, t('Table Type'), rawProps.table_type || rawProps.tableType);

      // Table Parameters: everything under details.stats and details.properties that looks like parameters
      Object.keys(analysis.details.stats || {}).forEach(key => {
        const valueRaw = (analysis.details.stats as Record<string, unknown>)[key];
        const lower = key.toLowerCase();
        let value: string | undefined;
        if (lower.includes('size') || lower.includes('bytes') || lower.endsWith('length')) {
          const n = Number(valueRaw as unknown as string);
          if (!isNaN(n) && isFinite(n)) {
            value = formatBytes(n);
          }
        } else if (
          lower.includes('time') ||
          lower.includes('timestamp') ||
          lower.includes('date') ||
          lower.includes('modified')
        ) {
          const n = Number(valueRaw as unknown as string);
          if (!isNaN(n) && isFinite(n)) {
            const ms = n < 1e12 ? n * 1000 : n;
            value = formatTimestamp(new Date(ms));
          } else if (typeof valueRaw === 'string') {
            const d = new Date(valueRaw);
            if (!isNaN(d.getTime())) {
              value = formatTimestamp(d);
            }
          }
        }
        tableParameters.push({ name: key, value: String(value ?? valueRaw ?? '') });
      });
      // Legacy lists some from properties as well (transactional, etc.)
      [
        'transactional',
        'transactional_properties',
        'transient_lastDdlTime',
        'COLUMN_STATS_ACCURATE',
        'bucketing_version'
      ].forEach(key => {
        if (typeof rawProps[key] !== 'undefined') {
          tableParameters.push({ name: key, value: String(rawProps[key] as unknown as string) });
        }
      });

      // Storage Information
      add(
        storageInfo,
        t('SerDe Library'),
        rawProps['SerDe Library:'] || rawProps.serde_lib || rawProps.serdeLibName
      );
      add(
        storageInfo,
        t('InputFormat'),
        rawProps.InputFormat || rawProps.input_format || rawProps.inputFormat
      );
      add(
        storageInfo,
        t('OutputFormat'),
        rawProps.OutputFormat || rawProps.output_format || rawProps.outputFormat
      );
      add(storageInfo, t('Compressed'), rawProps.compressed ? t('Yes') : t('No'));
      add(storageInfo, t('Num Buckets'), rawProps.numBuckets || rawProps.num_buckets || -1);
      add(
        storageInfo,
        t('Bucket Columns'),
        Array.isArray(rawProps.bucketCols)
          ? JSON.stringify(rawProps.bucketCols)
          : rawProps.bucketCols || '[]'
      );
      add(
        storageInfo,
        t('Sort Columns'),
        Array.isArray(rawProps.sortCols)
          ? JSON.stringify(rawProps.sortCols)
          : rawProps.sortCols || '[]'
      );

      // Storage Desc Params: try to parse properties following legacy conventions
      if (rawProps['Storage Desc Params:']) {
        storageDescParams.push({
          name: t('serialization.format'),
          value: String(rawProps['Storage Desc Params:'])
        });
      }

      // Fallback simple flat list
      const allProps = Object.keys(rawProps).map(key => ({
        name: key,
        value: String(rawProps[key] ?? '')
      }));
      setDetailsProperties(allProps);
      setDetailsSections({ baseInfo, tableParameters, storageInfo, storageDescParams });
      setDetailsColumns(columnsForOverview);
      const sample = await entry.getSample({ silenceErrors: true });
      const headers = Array.isArray(sample.meta)
        ? (sample.meta as SampleMeta[]).map((m: SampleMeta) => m.name)
        : [];
      setSampleData({ headers, rows: sample.data || [] });
      const cols = (analysis.cols || []).map(c => ({
        name: (c as unknown as { name: string }).name,
        type: (c as unknown as { type: string }).type,
        comment: (c as unknown as { comment?: string }).comment
      }));
      setDetailsColumns(cols);
    } catch (err) {
      huePubSub.publish(GLOBAL_ERROR_TOPIC, { message: t('Failed to load table data') });
    } finally {
      setLoadingData(false);
    }
  }, [currentDb, table, connector, namespace, compute]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <div className="hue-table-browser">
      <CommonHeader title={t('Table Browser')} icon={<DataBrowserIcon />} />
      <div className="hue-table-browser__container">
        <Breadcrumbs
          sourceType={route.sourceType}
          database={currentDb}
          table={table}
          sourceOptions={(connectors || []).map(c => c.type)}
          onClickDataSources={() => {
            // Navigate to Data sources root and clear selection
            const urlPathname = window.location.pathname;
            const baseIdx = urlPathname.indexOf('/tablebrowser');
            const base = baseIdx !== -1 ? urlPathname.substring(0, baseIdx) : '';
            selectDb(undefined);
            setTable(undefined);
            changeURL(buildTableBrowserPath(base));
            setLocationPath(window.location.pathname);
          }}
          onClickDatabases={() => {
            // Navigate to source root and clear db/table selection
            const urlPathname = window.location.pathname;
            const baseIdx = urlPathname.indexOf('/tablebrowser');
            const base = baseIdx !== -1 ? urlPathname.substring(0, baseIdx) : '';
            const sourceType = route.sourceType || 'hive';
            selectDb(undefined);
            setTable(undefined);
            changeURL(buildTableBrowserPath(base, sourceType));
            setLocationPath(window.location.pathname);
          }}
          onClickDatabase={(db: string) => {
            // Navigate to db and clear table selection
            const urlPathname = window.location.pathname;
            const baseIdx = urlPathname.indexOf('/tablebrowser');
            const base = baseIdx !== -1 ? urlPathname.substring(0, baseIdx) : '';
            const sourceType = route.sourceType || 'hive';
            if (db !== currentDb) {
              selectDb(db);
            }
            setTable(undefined);
            changeURL(buildTableBrowserPath(base, sourceType, db));
            setLocationPath(window.location.pathname);
          }}
          onSelectSource={src => {
            const wanted = (connectors || []).find(
              c => c.type === src || (c as unknown as { id?: string }).id === src
            );
            if (wanted) {
              setConnector(wanted as unknown as never);
            }
            // Reset DB and Table on source change
            selectDb(undefined);
            setTable(undefined);
            const urlPathname = window.location.pathname;
            const baseIdx = urlPathname.indexOf('/tablebrowser');
            const base = baseIdx !== -1 ? urlPathname.substring(0, baseIdx) : '';
            changeURL(buildTableBrowserPath(base, src));
            setLocationPath(window.location.pathname);
          }}
        />
        <Row gutter={16}>
          <Col span={24}>
            <div
              className="hue-table-browser__panel"
              data-testid="tb-right-panel"
              tabIndex={-1}
              ref={panelRef}
            >
              {!route.sourceType && (
                <SourcesList
                  sources={
                    Array.from(
                      new Set(
                        (connectors || []).map(
                          c => c.type || (c as unknown as { id?: string }).id || ''
                        )
                      )
                    ).filter(Boolean) as string[]
                  }
                  loading={!!loadingStates.database}
                  isRefreshing={isRefreshing}
                  sourceFilter={sourceFilter}
                  setSourceFilter={setSourceFilter}
                  sourcePageNumber={sourcePageNumber}
                  setSourcePageNumber={setSourcePageNumber}
                  sourcePageSize={sourcePageSize}
                  setSourcePageSize={setSourcePageSize}
                  onOpenSource={src => {
                    const wanted = (connectors || []).find(
                      c => c.type === src || (c as unknown as { id?: string }).id === src
                    );
                    if (wanted) {
                      setConnector(wanted as unknown as never);
                    }
                    selectDb(undefined);
                    setTable(undefined);
                    const urlPathname = window.location.pathname;
                    const baseIdx = urlPathname.indexOf('/tablebrowser');
                    const base = baseIdx !== -1 ? urlPathname.substring(0, baseIdx) : '';
                    changeURL(buildTableBrowserPath(base, src));
                    setLocationPath(window.location.pathname);
                  }}
                />
              )}
              {route.sourceType && !currentDb && (
                <DatabasesList
                  databases={databases || []}
                  loading={!!loadingStates.database}
                  isRefreshing={isRefreshing}
                  onRefresh={async () => {
                    try {
                      if (connector && namespace && compute) {
                        setIsRefreshing(true);
                        const sourceEntry = await dataCatalog.getEntry({
                          connector,
                          namespace,
                          compute,
                          path: []
                        });
                        await sourceEntry.clearCache({ cascade: true, silenceErrors: true });
                        await reloadDatabases();
                      }
                    } catch {
                      huePubSub.publish(GLOBAL_ERROR_TOPIC, {
                        message: t('Failed to refresh databases')
                      });
                    } finally {
                      setIsRefreshing(false);
                    }
                  }}
                  dbFilter={dbFilter}
                  setDbFilter={setDbFilter}
                  dbPageNumber={dbPageNumber}
                  setDbPageNumber={setDbPageNumber}
                  dbPageSize={dbPageSize}
                  setDbPageSize={setDbPageSize}
                  dbDescriptions={dbDescriptions}
                  editingDb={editingDb}
                  editingValue={editingValue}
                  setEditingDb={setEditingDb}
                  setEditingValue={setEditingValue}
                  onOpenDatabase={db => {
                    if (db !== currentDb) {
                      selectDb(db);
                    }
                    setTable(undefined);
                    updatePath(db, undefined);
                  }}
                  onSaveDescription={saveDbDescription}
                  onDropDatabases={async names => {
                    try {
                      await fetch(`/metastore/databases/drop`, {
                        method: 'POST',
                        headers: {
                          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                        },
                        body: names
                          .map(n => `database_selection=${encodeURIComponent(n)}`)
                          .concat(['is_embeddable=true'])
                          .join('&')
                      });
                      await reloadDatabases();
                    } catch {
                      huePubSub.publish(GLOBAL_ERROR_TOPIC, {
                        message: t('Failed to drop databases')
                      });
                    }
                  }}
                />
              )}

              {route.sourceType && !!currentDb && !table && (
                <TablesList
                  tables={(tables || []).map(item => ({
                    name: item.name,
                    type: item.type,
                    comment: item.comment
                  }))}
                  loading={!!loadingStates.table}
                  isRefreshing={isRefreshing}
                  onRefresh={async () => {
                    try {
                      if (connector && namespace && compute && currentDb) {
                        setIsRefreshing(true);
                        const dbEntry = await dataCatalog.getEntry({
                          connector,
                          namespace,
                          compute,
                          path: [currentDb]
                        });
                        await dbEntry.clearCache({ cascade: true, silenceErrors: true });
                        await reloadTables();
                      }
                    } catch {
                      huePubSub.publish(GLOBAL_ERROR_TOPIC, {
                        message: t('Failed to refresh tables')
                      });
                    } finally {
                      setIsRefreshing(false);
                    }
                  }}
                  tableFilter={tableFilter}
                  setTableFilter={setTableFilter}
                  tablePageNumber={tablePageNumber}
                  setTablePageNumber={setTablePageNumber}
                  tablePageSize={tablePageSize}
                  setTablePageSize={setTablePageSize}
                  tableDescriptions={tableDescriptions}
                  editingTableName={editingTableName}
                  editingTableValue={editingTableValue}
                  setEditingTableName={setEditingTableName}
                  setEditingTableValue={setEditingTableValue}
                  onOpenTable={tbl => {
                    setTable(tbl);
                    updatePath(currentDb, tbl);
                  }}
                  onSaveDescription={saveTableDescription}
                  onViewSelection={name => {
                    setTable(name);
                    updatePath(currentDb, name);
                  }}
                  onQuerySelection={name => {
                    huePubSub.publish('open.editor.new.query', {
                      type: route.sourceType || 'hive',
                      statementType: 'text',
                      statementPath: currentDb && name ? `${currentDb}.${name}` : undefined
                    });
                  }}
                  onDropSelection={async names => {
                    try {
                      await fetch(
                        `/metastore/tables/drop/${encodeURIComponent(currentDb as string)}`,
                        {
                          method: 'POST',
                          headers: {
                            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                          },
                          body: `table_selection=${encodeURIComponent(
                            JSON.stringify(names)
                          )}&skip_trash=off&is_embeddable=true`
                        }
                      );
                      await reloadTables();
                    } catch {
                      huePubSub.publish(GLOBAL_ERROR_TOPIC, {
                        message: t('Failed to drop tables')
                      });
                    }
                  }}
                />
              )}

              {!!currentDb && !!table && (
                <div>
                  <Tabs
                    activeKey={activeTab}
                    onChange={onTabChange}
                    sampleCount={sampleData?.rows?.length}
                    partitionsCount={
                      overviewProps?.stats ? Number(overviewProps?.stats?.files) : undefined
                    }
                  />
                  <Loading spinning={false}>
                    {activeTab === 'overview' && (
                      <Overview
                        properties={overviewProps?.properties}
                        stats={overviewProps?.stats}
                        hdfsLink={overviewProps?.hdfsLink}
                        columns={detailsColumns}
                        loadingProperties={loadingData && !overviewProps?.properties}
                        loadingStats={loadingData && !overviewProps?.stats}
                        loadingColumns={loadingData && !detailsColumns.length}
                        onRefreshStats={async () => {
                          // Reuse toolbar refresh to invalidate and refetch
                          try {
                            if (currentDb && table && connector && namespace && compute) {
                              const entry = await dataCatalog.getEntry({
                                connector,
                                namespace,
                                compute,
                                path: [currentDb, table]
                              });
                              setLoadingData(true);
                              await entry.clearCache({ cascade: true, silenceErrors: true });
                            }
                          } catch {}
                          await fetchData();
                          setLoadingData(false);
                        }}
                      />
                    )}
                    {activeTab === 'sample' && (
                      <Loading spinning={loadingData && !sampleData}>
                        <SampleGrid data={sampleData} />
                      </Loading>
                    )}
                    {activeTab === 'details' && (
                      <Loading
                        spinning={
                          loadingData &&
                          !(
                            detailsProperties?.length ||
                            detailsSections.baseInfo?.length ||
                            detailsSections.tableParameters?.length ||
                            detailsSections.storageInfo?.length ||
                            detailsSections.storageDescParams?.length
                          )
                        }
                      >
                        <DetailsProperties
                          properties={detailsProperties}
                          baseInfo={detailsSections.baseInfo}
                          tableParameters={detailsSections.tableParameters}
                          storageInfo={detailsSections.storageInfo}
                          storageDescParams={detailsSections.storageDescParams}
                        />
                      </Loading>
                    )}
                    {activeTab === 'partitions' && (
                      <Loading spinning={loadingData && !overviewProps}>
                        <Partitions
                          connector={connector}
                          namespace={namespace}
                          compute={compute}
                          database={currentDb}
                          table={table}
                          onCountChange={() => {}}
                        />
                      </Loading>
                    )}
                    {activeTab === 'queries' && (
                      <Loading spinning={loadingData && !overviewProps}>
                        <Queries
                          connector={connector}
                          namespace={namespace}
                          compute={compute}
                          database={currentDb}
                          table={table}
                        />
                      </Loading>
                    )}
                    {activeTab === 'viewSql' && (
                      <Loading spinning={loadingData && !overviewProps?.properties}>
                        <ViewSql
                          sql={
                            (overviewProps?.properties || []).find(
                              p =>
                                p.name.toLowerCase() === 'view original text:' ||
                                p.name.toLowerCase() === 'original query:'
                            )?.value
                          }
                        />
                      </Loading>
                    )}
                    {activeTab === 'privileges' && (
                      <Loading spinning={loadingData && !overviewProps}>
                        <Privileges database={currentDb} table={table} />
                      </Loading>
                    )}
                  </Loading>
                  {!!table && (
                    <div style={{ marginTop: 12 }}>
                      <Button
                        onClick={() => {
                          setTable(undefined);
                          updatePath(currentDb, undefined);
                        }}
                        data-testid="tb-back"
                      >
                        {t('Back to tables')}
                      </Button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default TableBrowserPage;

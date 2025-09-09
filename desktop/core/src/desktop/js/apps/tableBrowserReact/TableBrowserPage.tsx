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

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Button, Col, Row, Input, Skeleton } from 'antd';
import Loading from 'cuix/dist/components/Loading';
import EmptyState from 'cuix/dist/components/EmptyState';
import Filter from 'cuix/dist/components/Filter';
import PaginatedTable, {
  type ColumnProps as PaginatedColumnProps
} from '../../reactComponents/PaginatedTable/PaginatedTable';
import type { FilterOutput } from 'cuix/dist/components/Filter/types';

import DataBrowserIcon from '@cloudera/cuix-core/icons/react/DataBrowserIcon';

import { i18nReact } from '../../utils/i18nReact';
import CommonHeader from '../../reactComponents/CommonHeader/CommonHeader';
import changeURL from '../../utils/url/changeURL';
import { useDataCatalog } from '../../utils/hooks/useDataCatalog/useDataCatalog';
import Breadcrumbs from './components/Breadcrumbs';
import Toolbar from './components/Toolbar';
import Tabs, { TabKey } from './components/Tabs';
import Overview from './components/Overview';
import SampleGrid from './components/SampleGrid';
import DetailsSchema from './components/DetailsSchema';
import Partitions from './components/Partitions';
import dataCatalog from '../../catalog/dataCatalog';
import type { Analysis, SampleMeta } from '../../catalog/DataCatalogEntry';
import ViewSql from './components/ViewSql';
import Queries from './components/Queries';
import Privileges from './components/Privileges';
import huePubSub from '../../utils/huePubSub';
import { GLOBAL_ERROR_TOPIC, GLOBAL_INFO_TOPIC } from '../../reactComponents/GlobalAlert/events';

import './TableBrowserPage.scss';

function parsePath(pathname: string): { sourceType?: string; database?: string; table?: string } {
  // Expect: <base>/tablebrowser[/<sourceType>[/<database>[/<table>]]]
  const idx = pathname.indexOf('/tablebrowser');
  if (idx === -1) {
    return {};
  }
  const rest = pathname.substring(idx + '/tablebrowser'.length);
  const segments = rest.split('/').filter(Boolean);
  return {
    sourceType: segments[0],
    database: segments[1],
    table: segments[2]
  };
}

const TableBrowserPage = (): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const route = useMemo(() => parsePath(window.location.pathname), [window.location.pathname]);

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
    setConnector
  } = useDataCatalog();

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
  const [forceShowSources, setForceShowSources] = useState(false);

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
      const nextPath = [
        base,
        '/tablebrowser',
        sourceType ? `/${encodeURIComponent(sourceType)}` : '',
        nextDatabase ? `/${encodeURIComponent(nextDatabase)}` : '',
        nextTable ? `/${encodeURIComponent(nextTable)}` : ''
      ].join('');
      changeURL(nextPath);
    },
    [window.location.pathname, route.sourceType, connector]
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
    if (route.sourceType && connectors && connectors.length) {
      const wanted = connectors.find(c => {
        const connectorId = (c as unknown as { id?: string }).id;
        return c.type === route.sourceType || connectorId === route.sourceType;
      });
      if (wanted) {
        setConnector(wanted as unknown as never);
      }
    }
  }, [route.sourceType, connectors]);

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
      const props = (analysis.properties || []).map(p => ({
        name: (p as unknown as { col_name?: string }).col_name || '',
        value: (p as unknown as { data_type?: string }).data_type || ''
      }));
      const hdfsLink = (analysis as unknown as { hdfs_link?: string })?.hdfs_link;
      setOverviewProps({ properties: props, hdfsLink });
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
            setForceShowSources(true);
            changeURL(`${base}/tablebrowser/`);
          }}
          onClickDatabases={() => {
            // Navigate to source root and clear db/table selection
            const urlPathname = window.location.pathname;
            const baseIdx = urlPathname.indexOf('/tablebrowser');
            const base = baseIdx !== -1 ? urlPathname.substring(0, baseIdx) : '';
            const sourceType = route.sourceType || 'hive';
            selectDb(undefined);
            setTable(undefined);
            setForceShowSources(false);
            changeURL(`${base}/tablebrowser/${encodeURIComponent(sourceType)}`);
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
            changeURL(
              `${base}/tablebrowser/${encodeURIComponent(sourceType)}/${encodeURIComponent(db)}`
            );
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
            changeURL(`${base}/tablebrowser/${encodeURIComponent(src)}`);
          }}
        />
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            margin: '8px 0 12px'
          }}
        >
          <div />
          <Toolbar
            sourceType={route.sourceType}
            database={currentDb}
            table={table}
            onRefresh={async () => {
              try {
                if (currentDb && table && connector && namespace && compute) {
                  const entry = await dataCatalog.getEntry({
                    connector,
                    namespace,
                    compute,
                    path: [currentDb, table]
                  });
                  await entry.clearCache({ cascade: true, silenceErrors: true });
                } else if (!currentDb && connector && namespace && compute) {
                  setIsRefreshing(true);
                  const sourceEntry = await dataCatalog.getEntry({
                    connector,
                    namespace,
                    compute,
                    path: []
                  });
                  await sourceEntry.clearCache({ cascade: true, silenceErrors: true });
                  window.setTimeout(() => setIsRefreshing(false), 600);
                } else if (currentDb && !table && connector && namespace && compute) {
                  setIsRefreshing(true);
                  const dbEntry = await dataCatalog.getEntry({
                    connector,
                    namespace,
                    compute,
                    path: [currentDb]
                  });
                  await dbEntry.clearCache({ cascade: true, silenceErrors: true });
                  window.setTimeout(() => setIsRefreshing(false), 600);
                }
              } catch {
                huePubSub.publish(GLOBAL_ERROR_TOPIC, { message: t('Failed to refresh metadata') });
                setIsRefreshing(false);
              }
              // Reload current view data via Data Catalog (no full reload)
              if (currentDb && table) {
                fetchData();
              }
            }}
            onLoadData={async () => {
              if (!currentDb || !table) {
                return;
              }
              try {
                await fetch(
                  `/metastore/table/${encodeURIComponent(currentDb)}/${encodeURIComponent(
                    table
                  )}/load`,
                  {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                    },
                    body: 'is_embeddable=true'
                  }
                );
                huePubSub.publish(GLOBAL_INFO_TOPIC, { message: t('Load data request sent') });
              } catch {
                huePubSub.publish(GLOBAL_ERROR_TOPIC, {
                  message: t('Failed to load data into table')
                });
              } finally {
                fetchData();
              }
            }}
            onDrop={async () => {
              if (!currentDb || !table) {
                return;
              }
              // Call legacy drop endpoint in the background
              try {
                await fetch(`/metastore/tables/drop/${encodeURIComponent(currentDb)}`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8' },
                  body: `table_selection=${encodeURIComponent(JSON.stringify([table]))}&skip_trash=off&is_embeddable=true`
                });
                // Navigate back to db on success
                updatePath(currentDb, undefined);
              } catch {
                huePubSub.publish(GLOBAL_ERROR_TOPIC, { message: t('Failed to drop table') });
              }
            }}
          />
        </div>
        <Row gutter={16}>
          <Col span={24}>
            <div className="hue-table-browser__panel" data-testid="tb-right-panel">
              {(!route.sourceType || forceShowSources) && (
                <div>
                  <div style={{ marginBottom: 8 }}>{t('Data sources')}</div>
                  <Loading spinning={!!loadingStates.database || isRefreshing}>
                    <div className="hue-table-browser__filter">
                      <Filter
                        search={{ placeholder: t('Filter sources') }}
                        onChange={(output: FilterOutput) => {
                          const searchValue = String(
                            (output as unknown as { search?: unknown[] }).search?.[0] ?? ''
                          );
                          setSourceFilter(searchValue);
                        }}
                      />
                    </div>
                    {(() => {
                      const list = (connectors || []).map(
                        c => c.type || (c as unknown as { id?: string }).id || ''
                      );
                      const unique = Array.from(new Set(list)).filter(Boolean) as string[];
                      const filtered = unique.filter(src =>
                        sourceFilter ? src.toLowerCase().includes(sourceFilter.toLowerCase()) : true
                      );
                      if (!loadingStates.database && filtered.length === 0) {
                        return <EmptyState title={t('No sources')} />;
                      }
                      const sourceColumns: PaginatedColumnProps<{ name: string }>[] = [
                        {
                          title: t('Source'),
                          dataIndex: 'name',
                          key: 'name',
                          render: (text: string, record: { name: string }) => (
                            <Button
                              type="link"
                              aria-label={t('Open source')}
                              onClick={() => {
                                const src = record.name;
                                const wanted = (connectors || []).find(
                                  c =>
                                    c.type === src || (c as unknown as { id?: string }).id === src
                                );
                                if (wanted) {
                                  setConnector(wanted as unknown as never);
                                }
                                selectDb(undefined);
                                setTable(undefined);
                                setForceShowSources(false);
                                const urlPathname = window.location.pathname;
                                const baseIdx = urlPathname.indexOf('/tablebrowser');
                                let base = '';
                                if (baseIdx !== -1) {
                                  base = urlPathname.substring(0, baseIdx);
                                }
                                changeURL(`${base}/tablebrowser/${encodeURIComponent(src)}`);
                              }}
                            >
                              {text.toUpperCase()}
                            </Button>
                          )
                        }
                      ];
                      const sourceData = filtered.map(name => ({ key: name, name }));
                      const totalSize = sourceData.length;
                      const totalPages = Math.max(Math.ceil(totalSize / sourcePageSize), 1);
                      const start = (sourcePageNumber - 1) * sourcePageSize;
                      const pageData = sourceData.slice(start, start + sourcePageSize);
                      return (
                        <PaginatedTable<{ name: string }>
                          data={pageData}
                          columns={sourceColumns}
                          rowKey="key"
                          pagination={{
                            pageStats: {
                              pageNumber: sourcePageNumber,
                              totalPages,
                              pageSize: sourcePageSize,
                              totalSize
                            },
                            setPageNumber: setSourcePageNumber,
                            setPageSize: setSourcePageSize
                          }}
                        />
                      );
                    })()}
                  </Loading>
                </div>
              )}
              {route.sourceType && !currentDb && (
                <div>
                  <div style={{ marginBottom: 8 }}>{t('Databases')}</div>
                  <Loading spinning={!!loadingStates.database || isRefreshing}>
                    <div className="hue-table-browser__filter">
                      <Filter
                        search={{ placeholder: t('Filter databases') }}
                        onChange={(output: FilterOutput) => {
                          const searchValue = String(
                            (output as unknown as { search?: unknown[] }).search?.[0] ?? ''
                          );
                          setDbFilter(searchValue);
                        }}
                      />
                    </div>
                    {(() => {
                      const filtered = (databases || []).filter(db =>
                        dbFilter ? db.toLowerCase().includes(dbFilter.toLowerCase()) : true
                      );
                      if (!loadingStates.database && filtered.length === 0) {
                        return <EmptyState title={t('No databases')} />;
                      }
                      const dbColumns: PaginatedColumnProps<{
                        name: string;
                        description?: string;
                      }>[] = [
                        {
                          title: t('Database'),
                          dataIndex: 'name',
                          key: 'name',
                          render: (text: string, record: { name: string }) => (
                            <Button
                              type="link"
                              aria-label={t('Open database')}
                              onClick={() => {
                                const db = record.name;
                                selectDb(db);
                                setTable(undefined);
                                updatePath(db, undefined);
                              }}
                            >
                              {text}
                            </Button>
                          )
                        },
                        {
                          title: t('Description'),
                          dataIndex: 'description',
                          key: 'description',
                          render: (_: string | undefined, record: { name: string }) => {
                            const hasValue = Object.prototype.hasOwnProperty.call(
                              dbDescriptions,
                              record.name
                            );
                            const current = dbDescriptions[record.name] || '';
                            if (editingDb === record.name) {
                              return (
                                <Input.TextArea
                                  autoSize={{ minRows: 1, maxRows: 4 }}
                                  value={editingValue}
                                  onChange={e => setEditingValue(e.target.value)}
                                  onBlur={() => saveDbDescription(record.name, editingValue)}
                                  onPressEnter={e => {
                                    e.preventDefault();
                                    saveDbDescription(record.name, editingValue);
                                  }}
                                />
                              );
                            }
                            if (!hasValue) {
                              return (
                                <Skeleton.Input active size="small" style={{ width: '60%' }} />
                              );
                            }
                            return (
                              <div>
                                <span style={{ whiteSpace: 'pre-wrap' }}>{current || ''}</span>
                                <Button
                                  type="link"
                                  size="small"
                                  onClick={() => {
                                    setEditingDb(record.name);
                                    setEditingValue(current);
                                  }}
                                >
                                  {t('Edit')}
                                </Button>
                              </div>
                            );
                          }
                        }
                      ];
                      const dbData = filtered.map(name => ({ key: name, name }));
                      const dbTotalSize = dbData.length;
                      const dbTotalPages = Math.max(Math.ceil(dbTotalSize / dbPageSize), 1);
                      const start = (dbPageNumber - 1) * dbPageSize;
                      const pageData = dbData.slice(start, start + dbPageSize);
                      return (
                        <PaginatedTable<{ name: string; description?: string }>
                          data={pageData}
                          columns={dbColumns}
                          rowKey="key"
                          pagination={{
                            pageStats: {
                              pageNumber: dbPageNumber,
                              totalPages: dbTotalPages,
                              pageSize: dbPageSize,
                              totalSize: dbTotalSize
                            },
                            setPageNumber: setDbPageNumber,
                            setPageSize: setDbPageSize
                          }}
                        />
                      );
                    })()}
                  </Loading>
                </div>
              )}

              {route.sourceType && !!currentDb && !table && (
                <div>
                  <div style={{ marginBottom: 8 }}>{t('Tables')}</div>
                  <Loading spinning={!!loadingStates.table || isRefreshing}>
                    <div className="hue-table-browser__filter">
                      <Filter
                        search={{ placeholder: t('Filter tables') }}
                        onChange={(output: FilterOutput) => {
                          const searchValue = String(
                            (output as unknown as { search?: unknown[] }).search?.[0] ?? ''
                          );
                          setTableFilter(searchValue);
                        }}
                      />
                    </div>
                    {(() => {
                      const filtered = (tables || []).filter(item =>
                        tableFilter
                          ? item.name.toLowerCase().includes(tableFilter.toLowerCase())
                          : true
                      );
                      if (!loadingStates.table && filtered.length === 0) {
                        return <EmptyState title={t('No tables')} />;
                      }
                      const tableColumns: PaginatedColumnProps<{
                        name: string;
                        type: string;
                        comment: string;
                      }>[] = [
                        {
                          title: t('Table'),
                          dataIndex: 'name',
                          key: 'name',
                          render: (text: string, record: { name: string }) => (
                            <Button
                              type="link"
                              aria-label={t('Open table')}
                              onClick={() => {
                                const tbl = record.name;
                                setTable(tbl);
                                updatePath(currentDb, tbl);
                              }}
                            >
                              {text}
                            </Button>
                          )
                        },
                        { title: t('Type'), dataIndex: 'type', key: 'type' },
                        {
                          title: t('Description'),
                          dataIndex: 'comment',
                          key: 'description',
                          render: (_: string, record: { name: string }) => {
                            const hasValue = Object.prototype.hasOwnProperty.call(
                              tableDescriptions,
                              record.name
                            );
                            const current = tableDescriptions[record.name] || '';
                            if (editingTableName === record.name) {
                              return (
                                <Input.TextArea
                                  autoSize={{ minRows: 1, maxRows: 4 }}
                                  value={editingTableValue}
                                  onChange={e => setEditingTableValue(e.target.value)}
                                  onBlur={() =>
                                    saveTableDescription(record.name, editingTableValue)
                                  }
                                  onPressEnter={e => {
                                    e.preventDefault();
                                    saveTableDescription(record.name, editingTableValue);
                                  }}
                                />
                              );
                            }
                            if (!hasValue) {
                              return (
                                <Skeleton.Input active size="small" style={{ width: '60%' }} />
                              );
                            }
                            return (
                              <div>
                                <span style={{ whiteSpace: 'pre-wrap' }}>{current || ''}</span>
                                <Button
                                  type="link"
                                  size="small"
                                  onClick={() => {
                                    setEditingTableName(record.name);
                                    setEditingTableValue(current);
                                  }}
                                >
                                  {t('Edit')}
                                </Button>
                              </div>
                            );
                          }
                        }
                      ];
                      const tableData = filtered.map(item => ({
                        key: item.name,
                        name: item.name,
                        type: item.type,
                        comment: item.comment
                      }));
                      const totalSize = tableData.length;
                      const totalPages = Math.max(Math.ceil(totalSize / tablePageSize), 1);
                      const start = (tablePageNumber - 1) * tablePageSize;
                      const pageData = tableData.slice(start, start + tablePageSize);
                      return (
                        <PaginatedTable<{
                          name: string;
                          type: string;
                          comment: string;
                        }>
                          data={pageData}
                          columns={tableColumns}
                          rowKey="key"
                          onRowClick={record => ({
                            onClick: () => {
                              const tbl = (record as unknown as { name: string }).name;
                              setTable(tbl);
                              updatePath(currentDb, tbl);
                            }
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
                      );
                    })()}
                  </Loading>
                </div>
              )}

              {!!currentDb && !!table && (
                <div>
                  <Tabs
                    activeKey={activeTab}
                    onChange={onTabChange}
                    sampleCount={sampleData?.rows?.length}
                  />
                  <Loading spinning={loadingData}>
                    {activeTab === 'overview' && (
                      <Overview
                        properties={overviewProps?.properties}
                        stats={overviewProps?.stats}
                        hdfsLink={overviewProps?.hdfsLink}
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
                    {activeTab === 'sample' && <SampleGrid data={sampleData} />}
                    {activeTab === 'details' && <DetailsSchema columns={detailsColumns} />}
                    {activeTab === 'partitions' && (
                      <Partitions
                        connector={connector}
                        namespace={namespace}
                        compute={compute}
                        database={currentDb}
                        table={table}
                      />
                    )}
                    {activeTab === 'queries' && (
                      <Queries
                        connector={connector}
                        namespace={namespace}
                        compute={compute}
                        database={currentDb}
                        table={table}
                      />
                    )}
                    {activeTab === 'viewSql' && (
                      <ViewSql
                        sql={
                          (overviewProps?.properties || []).find(
                            p =>
                              p.name.toLowerCase() === 'view original text:' ||
                              p.name.toLowerCase() === 'original query:'
                          )?.value
                        }
                      />
                    )}
                    {activeTab === 'privileges' && (
                      <Privileges database={currentDb} table={table} />
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

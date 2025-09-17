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

import React, { useCallback, useEffect, useRef, useState, useMemo } from 'react';
import i18nCuix from 'cuix/dist/utils/i18n';
import { Col, Row } from 'antd';
import DataBrowserIcon from '@cloudera/cuix-core/icons/react/DataBrowserIcon';

import { i18nReact } from '../../utils/i18nReact';
import CommonHeader from '../../reactComponents/CommonHeader/CommonHeader';
import { useTableBrowserController } from './hooks/useTableBrowserController';
import { useDataCatalog } from '../../utils/hooks/useDataCatalog/useDataCatalog';
import TableDetails from './TableDetails/TableDetails';
import ColumnDetails from './ColumnDetails/ColumnDetails';
import TypeDetails from './TypeDetails/TypeDetails';
import SourcesList from './SourceListing/SourcesList';
import DatabasesList from './DatabaseListing/DatabasesList';
import TablesList from './TableListing/TablesList';
import dataCatalog from '../../catalog/dataCatalog';
import { notifyError } from './utils/notifier';
import { useTableDetails } from './hooks/useTableDetails';
import { getConnectorIdOrType } from './utils/connector';
import { post } from '../../api/utils';
import { useDescriptionManager } from './hooks/useDescriptionManager';
import { useDatabaseProperties } from './hooks/useDatabaseProperties';

import './TableBrowserPage.scss';

// routing helpers moved to utils/routing

const TableBrowserPage = (): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const {
    route,
    activeTab,
    onTabChange,
    navigateToSources,
    navigateToSource,
    navigateToDatabase,
    navigateToTable,
    navigateToColumn,
    navigateToField
  } = useTableBrowserController();

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
  } = useDataCatalog({
    autoSelectFirstDatabase: false,
    autoSelectFirstConnector: !!route.sourceType // don't auto-select on sources page
  });

  const [table, setTable] = useState<string | undefined>(route.table);
  // activeTab provided by controller
  const [dbFilter, setDbFilter] = useState('');
  const [tableFilter, setTableFilter] = useState('');
  // Details loading state is provided by useTableDetails
  const [dbPageSize, setDbPageSize] = useState(50);
  const [dbPageNumber, setDbPageNumber] = useState(1);
  // Memoize arrays to prevent unnecessary re-renders
  const emptyPath = useMemo(() => [], []);
  const tablePath = useMemo(() => (currentDb ? [currentDb] : []), [currentDb]);
  const tableNames = useMemo(() => tables?.map(t => t.name) || [], [tables]);

  // Database description management using custom hook
  const {
    descriptions: dbDescriptions,
    editingItem: editingDb,
    editingValue,
    setEditingItem: setEditingDb,
    setEditingValue,
    saveDescription: saveDbDescription
  } = useDescriptionManager({
    connector,
    namespace,
    compute,
    items: databases,
    path: emptyPath,
    currentItem: currentDb
  });
  const [isRefreshing, setIsRefreshing] = useState(false);
  // Table description management using custom hook
  const {
    descriptions: tableDescriptions,
    editingItem: editingTableName,
    editingValue: editingTableValue,
    setEditingItem: setEditingTableName,
    setEditingValue: setEditingTableValue,
    saveDescription: saveTableDescription
  } = useDescriptionManager({
    connector,
    namespace,
    compute,
    items: tableNames,
    path: tablePath,
    currentItem: table
  });
  const [tablePageSize, setTablePageSize] = useState(50);
  const [tablePageNumber, setTablePageNumber] = useState(1);
  const [sourceFilter, setSourceFilter] = useState('');
  const [sourcePageSize, setSourcePageSize] = useState(50);
  const [sourcePageNumber, setSourcePageNumber] = useState(1);
  // Removed forceShowSources per follow-up TODO; derive strictly from URL

  // Database properties management using custom hook
  const { properties: databaseProperties, loading: loadingDatabaseProperties } =
    useDatabaseProperties({
      sourceType: route.sourceType,
      connector,
      database: currentDb,
      table
    });

  const updatePath = useCallback(
    (nextDatabase?: string, nextTable?: string) => {
      const sourceType = route.sourceType || getConnectorIdOrType(connector) || 'hive';
      if (nextDatabase && nextTable) {
        navigateToTable(nextDatabase, nextTable);
      } else if (nextDatabase) {
        navigateToDatabase(nextDatabase);
      } else if (sourceType) {
        navigateToSource(sourceType);
      } else {
        navigateToSources();
      }
    },
    [
      route.sourceType,
      connector,
      navigateToDatabase,
      navigateToTable,
      navigateToSource,
      navigateToSources
    ]
  );

  // Initialize from URL on mount (partial sync)
  useEffect(() => {
    // Initialize default CUIX i18n messages used by components (e.g., Filter empty states)
    try {
      if (i18nCuix && typeof i18nCuix.extend === 'function') {
        i18nCuix.extend({
          'message.noResultsFound': 'No results found'
        });
      }
    } catch {
      // noop
    }

    if (route.database) {
      selectDb(route.database);
    }
    if (route.table) {
      setTable(route.table);
    }
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
  }, [databases, route.database, currentDb, selectDb]);

  // If no DB provided in URL, avoid auto-selecting the first DB, and don't force a default source
  useEffect(() => {
    if (!route.database && currentDb) {
      selectDb(undefined);
      if (route.sourceType) {
        navigateToSource(route.sourceType);
      } else {
        navigateToSources();
      }
    }
  }, [currentDb, route.database, route.sourceType, navigateToSource, navigateToSources, selectDb]);

  // Focus management after crumb navigation
  const panelRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    if (panelRef.current) {
      panelRef.current.focus({ preventScroll: false } as unknown as FocusOptions);
    }
  }, [route.sourceType, currentDb, table]);

  const tableDetails = useTableDetails({
    connector,
    namespace,
    compute,
    database: currentDb,
    table
  });

  const sources = useMemo(
    () =>
      Array.from(
        new Set((connectors || []).map(c => c.type || (c as unknown as { id?: string }).id || ''))
      ).filter(Boolean) as string[],
    [connectors]
  );

  return (
    <div className="hue-table-browser">
      <CommonHeader title={t('Table Browser')} icon={<DataBrowserIcon />} />
      <div className="hue-table-browser__container">
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
                  sources={sources}
                  isInitializing={
                    !isRefreshing &&
                    (!!loadingStates.connector || !(connectors && connectors.length))
                  }
                  isRefreshing={isRefreshing}
                  onRefresh={async () => {
                    try {
                      setIsRefreshing(true);
                      // Refresh connectors/sources by reloading databases which triggers connector refresh
                      await reloadDatabases();
                    } catch {
                      notifyError(t('Failed to refresh data sources'));
                    } finally {
                      setIsRefreshing(false);
                    }
                  }}
                  sourceFilter={sourceFilter}
                  setSourceFilter={setSourceFilter}
                  sourcePageNumber={sourcePageNumber}
                  setSourcePageNumber={setSourcePageNumber}
                  sourcePageSize={sourcePageSize}
                  setSourcePageSize={setSourcePageSize}
                  sourceType={route.sourceType}
                  database={currentDb}
                  table={table}
                  sourceOptions={(connectors || []).map(c => c.type)}
                  onClickDataSources={() => {
                    // Already on data sources page, no action needed
                  }}
                  onClickDatabases={() => {
                    // Navigate to source root
                    const sourceType = route.sourceType || 'hive';
                    selectDb(undefined);
                    setTable(undefined);
                    navigateToSource(sourceType);
                  }}
                  onClickDatabase={(db: string) => {
                    // Navigate to database
                    if (db !== currentDb) {
                      selectDb(db);
                    }
                    setTable(undefined);
                    navigateToDatabase(db);
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
                    navigateToSource(src);
                  }}
                  onOpenSource={src => {
                    const wanted = (connectors || []).find(
                      c => c.type === src || (c as unknown as { id?: string }).id === src
                    );
                    if (wanted) {
                      setConnector(wanted as unknown as never);
                    }
                    selectDb(undefined);
                    setTable(undefined);
                    navigateToSource(src);
                  }}
                />
              )}
              {route.sourceType && !currentDb && (
                <DatabasesList
                  databases={databases || []}
                  isInitializing={
                    !!loadingStates.connector ||
                    !!loadingStates.namespace ||
                    !!loadingStates.compute ||
                    !!loadingStates.database ||
                    // initial render case while DBs are not fetched yet
                    !databases ||
                    databases.length === 0
                  }
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
                      notifyError(t('Failed to refresh databases'));
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
                  sourceType={route.sourceType}
                  database={currentDb}
                  table={table}
                  sourceOptions={(connectors || []).map(c => c.type)}
                  onClickDataSources={() => {
                    // Navigate to Data sources root and clear selection
                    selectDb(undefined);
                    setTable(undefined);
                    navigateToSources();
                  }}
                  onClickDatabases={() => {
                    // Navigate to source root and clear db/table selection
                    const sourceType = route.sourceType || 'hive';
                    selectDb(undefined);
                    setTable(undefined);
                    navigateToSource(sourceType);
                  }}
                  onClickDatabase={(db: string) => {
                    // Navigate to db and clear table selection
                    if (db !== currentDb) {
                      selectDb(db);
                    }
                    setTable(undefined);
                    navigateToDatabase(db);
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
                    navigateToSource(src);
                  }}
                  onDropDatabases={async names => {
                    try {
                      // Create URLSearchParams for proper form encoding without qs array notation
                      const formData = new URLSearchParams();
                      // Send database names as individual form fields (metastore expects getlist)
                      names.forEach(name => {
                        formData.append('database_selection', name);
                      });
                      formData.append('is_embeddable', 'true');
                      formData.append(
                        'source_type',
                        route.sourceType || getConnectorIdOrType(connector) || 'hive'
                      );
                      formData.append('start_time', Date.now().toString());

                      if (namespace) {
                        formData.append('namespace', JSON.stringify(namespace));
                      }

                      if (compute) {
                        formData.append('cluster', JSON.stringify(compute));
                      }

                      const result = await post<{ history_uuid?: string; message?: string }>(
                        '/metastore/databases/drop',
                        formData,
                        {
                          silenceErrors: false,
                          qsEncodeData: false // Don't use qs.stringify, send URLSearchParams directly
                        }
                      );

                      // Handle the task execution response
                      if (result?.message) {
                        notifyError(result.message);
                        // If there's an error message, reload databases to restore state
                        await reloadDatabases();
                        return;
                      }

                      // For successful operations (with or without history_uuid), reload databases
                      await reloadDatabases();
                    } catch (error) {
                      notifyError(t('Failed to drop databases'));
                      // On error, reload databases to restore the correct state
                      await reloadDatabases();
                    }
                  }}
                  onCreateDatabase={async (name, comment, location) => {
                    try {
                      // Use the beeswax create database endpoint with proper API utils
                      const formData: Record<string, string> = {
                        name: name
                      };

                      if (comment) {
                        formData.comment = comment;
                      }

                      if (location) {
                        formData.external_location = location;
                        formData.use_default_location = 'false';
                      } else {
                        formData.use_default_location = 'true';
                      }

                      // Use the post utility which handles CSRF tokens automatically
                      const result = await post<{ status?: number; message?: string }>(
                        '/beeswax/create/database',
                        formData,
                        {
                          silenceErrors: false
                        }
                      );

                      // Check if there was an error
                      if (result?.status === -1) {
                        notifyError(result.message || t('Failed to create database'));
                        return;
                      }

                      // Reload databases to show the new one
                      await reloadDatabases();
                    } catch (error) {
                      notifyError(t('Failed to create database'));
                      console.error('Create database error:', error);
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
                  isInitializing={
                    !!loadingStates.connector ||
                    !!loadingStates.namespace ||
                    !!loadingStates.compute ||
                    !!loadingStates.database ||
                    // ensure initial render after selecting DB shows loading until first fetch completes
                    (!!currentDb && (!tables || tables.length === 0))
                  }
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
                      notifyError(t('Failed to refresh tables'));
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
                    type Publish = (topic: string, payload: unknown) => void;
                    const w = window as unknown as { huePubSub?: { publish?: Publish } };
                    w.huePubSub?.publish?.('open.editor.new.query', {
                      type: route.sourceType || 'hive',
                      statementType: 'text',
                      statementPath: currentDb && name ? `${currentDb}.${name}` : undefined
                    });
                  }}
                  onDropSelection={async (names, skipTrash = false) => {
                    try {
                      // Create URLSearchParams for proper form encoding without qs array notation
                      const formData = new URLSearchParams();
                      // Send table names as individual form fields (metastore expects getlist)
                      names.forEach(name => {
                        formData.append('table_selection', name);
                      });
                      formData.append('is_embeddable', 'true');
                      formData.append('skip_trash', skipTrash ? 'on' : 'off');
                      formData.append(
                        'source_type',
                        route.sourceType || getConnectorIdOrType(connector) || 'hive'
                      );
                      formData.append('start_time', Date.now().toString());

                      if (namespace) {
                        formData.append('namespace', JSON.stringify(namespace));
                      }

                      if (compute) {
                        formData.append('cluster', JSON.stringify(compute));
                      }

                      const result = await post<{ history_uuid?: string; message?: string }>(
                        `/metastore/tables/drop/${encodeURIComponent(currentDb as string)}`,
                        formData,
                        {
                          silenceErrors: false,
                          qsEncodeData: false // Don't use qs.stringify, send URLSearchParams directly
                        }
                      );

                      // Handle the task execution response
                      if (result.message) {
                        notifyError(result.message);
                        // If there's an error message, reload tables to restore state
                        await reloadTables();
                        return;
                      }

                      // For successful operations (with or without history_uuid), reload tables
                      await reloadTables();
                    } catch (error) {
                      notifyError(t('Failed to drop tables'));
                      // On error, reload tables to restore the correct state
                      await reloadTables();
                    }
                  }}
                  onCreateTable={() => {
                    // Navigate to the importer for table creation
                    const hueUrls = (
                      window as unknown as { HUE_URLS?: { IMPORTER_CREATE_TABLE?: string } }
                    ).HUE_URLS;
                    const baseUrl = hueUrls?.IMPORTER_CREATE_TABLE;

                    if (baseUrl && currentDb) {
                      // Get the base path (e.g., "/hue")
                      const basePath = window.location.pathname.split('/tablebrowser')[0] || '';

                      // Construct URL with base path, database name and query parameters
                      const sourceType =
                        route.sourceType || getConnectorIdOrType(connector) || 'hive';
                      const params = new URLSearchParams({
                        sourceType,
                        ...(namespace && { namespace: JSON.stringify(namespace) }),
                        ...(compute && { compute: JSON.stringify(compute) })
                      });

                      const url = `${basePath}${baseUrl}${currentDb}/?${params.toString()}`;
                      window.open(url, '_blank');
                    } else {
                      console.warn('Importer URL not available or database not selected');
                    }
                  }}
                  databaseName={currentDb}
                  databaseProperties={databaseProperties}
                  loadingDatabaseProperties={loadingDatabaseProperties}
                  sourceType={route.sourceType}
                  table={table}
                  sourceOptions={(connectors || []).map(c => c.type)}
                  onClickDataSources={() => {
                    // Navigate to Data sources root and clear selection
                    selectDb(undefined);
                    setTable(undefined);
                    navigateToSources();
                  }}
                  onClickDatabases={() => {
                    // Navigate to source root and clear db/table selection
                    const sourceType = route.sourceType || 'hive';
                    selectDb(undefined);
                    setTable(undefined);
                    navigateToSource(sourceType);
                  }}
                  onClickDatabase={(db: string) => {
                    // Navigate to db and clear table selection
                    if (db !== currentDb) {
                      selectDb(db);
                    }
                    setTable(undefined);
                    navigateToDatabase(db);
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
                    navigateToSource(src);
                  }}
                />
              )}

              {!!currentDb && !!table && !route.column && (
                <TableDetails
                  sourceType={route.sourceType}
                  database={currentDb}
                  table={table}
                  activeTab={activeTab}
                  onTabChange={onTabChange}
                  onBackToTables={() => {
                    setTable(undefined);
                    navigateToDatabase(currentDb);
                  }}
                  connector={connector}
                  namespace={namespace}
                  compute={compute}
                  tableDetails={tableDetails}
                  onReloadTables={reloadTables}
                  sourceOptions={(connectors || []).map(c => c.type)}
                  onClickDataSources={() => {
                    // Navigate to Data sources root and clear selection
                    selectDb(undefined);
                    setTable(undefined);
                    navigateToSources();
                  }}
                  onClickDatabases={() => {
                    // Navigate to source root and clear db/table selection
                    const sourceType = route.sourceType || 'hive';
                    selectDb(undefined);
                    setTable(undefined);
                    navigateToSource(sourceType);
                  }}
                  onClickDatabase={(db: string) => {
                    // Navigate to db and clear table selection
                    if (db !== currentDb) {
                      selectDb(db);
                    }
                    setTable(undefined);
                    navigateToDatabase(db);
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
                    navigateToSource(src);
                  }}
                  onOpenColumn={col => {
                    navigateToColumn(currentDb, table, col);
                  }}
                />
              )}

              {!!currentDb &&
                !!table &&
                !!route.column &&
                (route.fields && route.fields.length ? (
                  <TypeDetails
                    key={`typedetails-${route.column}-${route.fields.join('.')}`}
                    sourceType={route.sourceType}
                    database={currentDb}
                    table={table}
                    column={route.column}
                    fields={route.fields}
                    tableDetails={tableDetails}
                    onOpenField={next =>
                      navigateToField(currentDb, table, route.column as string, next)
                    }
                    onClickDataSources={() => {
                      selectDb(undefined);
                      setTable(undefined);
                      navigateToSources();
                    }}
                    onClickDatabases={() => {
                      selectDb(undefined);
                      setTable(undefined);
                      navigateToSource(route.sourceType || 'hive');
                    }}
                    onClickDatabase={db => {
                      if (db !== currentDb) {
                        selectDb(db);
                      }
                      setTable(undefined);
                      navigateToDatabase(db);
                    }}
                    onClickTable={tbl => {
                      if (currentDb) {
                        setTable(tbl);
                        navigateToTable(currentDb, tbl);
                      }
                    }}
                  />
                ) : (
                  <ColumnDetails
                    key={`${route.column}-root`}
                    sourceType={route.sourceType}
                    database={currentDb}
                    table={table}
                    column={route.column}
                    fields={route.fields}
                    connector={connector}
                    namespace={namespace}
                    compute={compute}
                    tableDetails={tableDetails}
                    onBackToTable={() => navigateToTable(currentDb, table)}
                    onOpenField={next =>
                      navigateToField(currentDb, table, route.column as string, next)
                    }
                  />
                ))}
            </div>
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default TableBrowserPage;

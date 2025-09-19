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
import { useTableDetailsState } from './TableDetails/useTableDetailsState';
import ColumnDetails from './ColumnDetails/ColumnDetails';
import TypeDetails from './TypeDetails/TypeDetails';
import SourcesList from './SourceListing/SourcesList';
import { useSourcesListState } from './SourceListing/useSourcesListState';
import DatabasesList from './DatabaseListing/DatabasesList';
import { useDatabasesListState } from './DatabaseListing/useDatabasesListState';
import TablesList from './TableListing/TablesList';
import { useTablesListState } from './TableListing/useTablesListState';
import { useDatabaseProperties } from './hooks/useDatabaseProperties';
import { useTableBrowserActions } from './hooks/useTableBrowserActions';
import { getConnectorIdOrType } from './utils/connector';
import './TableBrowserPage.scss';
import { NavigationProvider } from './sharedComponents/NavigationContext';

const TableBrowserPage = (): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  // ===== HOOKS AND STATE =====
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

  // Local state
  const [table, setTable] = useState<string | undefined>(route.table);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Derived state
  const tableNames = useMemo(() => tables?.map(t => t.name) || [], [tables]);

  // Feature state hooks
  const sourcesListState = useSourcesListState({ connectors });
  const databasesListState = useDatabasesListState({
    connector: connector || undefined,
    namespace: namespace || undefined,
    compute: compute || undefined,
    databases,
    currentDatabase: currentDb
  });
  const tablesListState = useTablesListState({
    connector: connector || undefined,
    namespace: namespace || undefined,
    compute: compute || undefined,
    database: currentDb,
    tables: tableNames
  });
  const tableDetailsState = useTableDetailsState({
    database: currentDb as string,
    table: table as string,
    connector,
    namespace,
    compute,
    activeTab,
    onTabChange
  });

  const { properties: databaseProperties, loading: loadingDatabaseProperties } =
    useDatabaseProperties({
      sourceType: route.sourceType,
      connector,
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

  // ===== NAVIGATION HELPERS =====
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

  // ===== ACTIONS CONTROLLER =====
  const actions = useTableBrowserActions({
    connector,
    namespace,
    compute,
    connectors,
    currentDb,
    route,
    setIsRefreshing,
    setTable,
    setConnector,
    selectDb,
    reloadDatabases,
    reloadTables,
    updatePath,
    navigateToSource,
    navigateToDatabase
  });

  // ===== EFFECTS =====
  // Initialize cuix i18n labels similar to Partitions tab so "Filter by" shows
  useEffect(() => {
    try {
      if (i18nCuix && typeof i18nCuix.extend === 'function') {
        i18nCuix.extend({
          'label.more': 'More',
          'label.filterBy': 'Filter by',
          'label.clear': 'Clear',
          'label.search': 'Search',
          'label.selected': 'Selected',
          'message.noResultsFound': 'No results found'
        });
      }
    } catch (e) {
      // no-op
    }
  }, []);

  // Initialize from URL on mount (partial sync)
  useEffect(() => {
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

  // ===== RENDER =====
  return (
    <NavigationProvider
      value={{
        navigateToSources: () => {
          selectDb(undefined);
          setTable(undefined);
          navigateToSources();
        },
        navigateToSource: (src: string) => {
          selectDb(undefined);
          setTable(undefined);
          navigateToSource(src);
        },
        navigateToDatabase: (db: string) => {
          if (db !== currentDb) {
            selectDb(db);
          }
          setTable(undefined);
          navigateToDatabase(db);
        },
        navigateToTable: (db: string, tbl: string) => {
          setTable(tbl);
          navigateToTable(db, tbl);
        },
        navigateToColumn,
        navigateToField
      }}
    >
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
                    isRefreshing={isRefreshing}
                    onRefresh={actions.handleRefreshSources}
                    state={sourcesListState}
                    sourceType={route.sourceType}
                    database={currentDb}
                    table={table}
                    sourceOptions={(connectors || []).map(c => c.type)}
                    onClickDataSources={() => {}}
                    onClickDatabases={actions.handleClickDatabases}
                    onClickDatabase={actions.handleClickDatabase}
                    onSelectSource={actions.handleSelectSource}
                    onOpenSource={actions.handleSelectSource}
                  />
                )}
                {route.sourceType && !currentDb && (
                  <DatabasesList
                    databases={databases || []}
                    isRefreshing={isRefreshing}
                    onRefresh={actions.handleRefreshDatabases}
                    state={databasesListState}
                    onOpenDatabase={actions.handleOpenDatabase}
                    sourceType={route.sourceType}
                    database={currentDb}
                    table={table}
                    sourceOptions={(connectors || []).map(c => c.type)}
                    onSelectSource={actions.handleSelectSource}
                    onDropDatabases={actions.handleDropDatabases}
                    onCreateDatabase={actions.handleCreateDatabase}
                  />
                )}

                {route.sourceType && !!currentDb && !table && (
                  <TablesList
                    tables={(tables || []).map(item => ({
                      name: item.name,
                      type: item.type,
                      comment: item.comment
                    }))}
                    isRefreshing={isRefreshing}
                    onRefresh={actions.handleRefreshTables}
                    onOpenTable={actions.handleOpenTable}
                    onViewSelection={actions.handleOpenTable}
                    onQuerySelection={actions.handleQuerySelection}
                    onDropSelection={actions.handleDropTables}
                    onCreateTable={actions.handleCreateTable}
                    databaseName={currentDb}
                    databaseProperties={databaseProperties}
                    loadingDatabaseProperties={loadingDatabaseProperties}
                    sourceType={route.sourceType}
                    table={table}
                    sourceOptions={(connectors || []).map(c => c.type)}
                    onSelectSource={actions.handleSelectSource}
                    state={tablesListState}
                  />
                )}

                {!!currentDb && !!table && !route.column && (
                  <TableDetails
                    sourceType={route.sourceType}
                    database={currentDb}
                    table={table}
                    connector={connector}
                    namespace={namespace}
                    compute={compute}
                    sourceOptions={(connectors || []).map(c => c.type)}
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
                    state={tableDetailsState}
                    onReloadTables={reloadTables}
                    onBackToTables={() => {
                      setTable(undefined);
                      updatePath(currentDb, undefined);
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
                      tableDetails={tableDetailsState.tableDetails}
                      onOpenField={next =>
                        navigateToField(currentDb, table, route.column as string, next)
                      }
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
                      tableDetails={tableDetailsState.tableDetails}
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
    </NavigationProvider>
  );
};

export default TableBrowserPage;

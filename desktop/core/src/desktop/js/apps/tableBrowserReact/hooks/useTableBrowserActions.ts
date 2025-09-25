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

import { useCallback } from 'react';
import { i18nReact } from '../../../utils/i18nReact';
import { post } from '../../../api/utils';
import { notifyError } from '../utils/notifier';
import { getConnectorIdOrType } from '../utils/connector';
import dataCatalog from '../../../catalog/dataCatalog';
import type { Connector, Namespace, Compute } from '../../../config/types';

export interface UseTableBrowserActionsArgs {
  // Data catalog dependencies
  connector?: Connector | null;
  namespace?: Namespace | null;
  compute?: Compute | null;
  connectors?: Connector[];

  // Current state
  currentDb?: string;
  route: {
    sourceType?: string;
  };

  // State setters
  setIsRefreshing: (refreshing: boolean) => void;
  setTable: (table: string | undefined) => void;
  setConnector: (connector: Connector) => void;
  selectDb: (db: string | undefined) => void;

  // Data reloaders
  reloadDatabases: () => Promise<void>;
  reloadTables: () => Promise<void>;

  // Navigation functions
  updatePath: (database?: string, table?: string) => void;
  navigateToSource: (sourceType: string) => void;
  navigateToDatabase: (database: string) => void;

  // Optimistic update methods
  optimisticallyRemoveDatabases: (databaseNames: string[]) => void;
  optimisticallyAddDatabase: (databaseName: string) => void;
  revertOptimisticUpdates: () => void;
}

export interface TableBrowserActions {
  // Table actions
  handleRefreshTables: () => Promise<void>;
  handleOpenTable: (tableName: string) => void;
  handleQuerySelection: (tableName: string) => void;
  handleDropTables: (tableNames: string[], skipTrash?: boolean) => Promise<void>;
  handleCreateTable: () => void;

  // Database actions
  handleRefreshDatabases: () => Promise<void>;
  handleOpenDatabase: (db: string) => void;
  handleDropDatabases: (names: string[]) => Promise<void>;
  handleCreateDatabase: (name: string, comment?: string, location?: string) => Promise<void>;

  // Source actions
  handleRefreshSources: () => Promise<void>;
  handleSelectSource: (src: string) => void;

  // Navigation actions
  handleClickDatabases: () => void;
  handleClickDatabase: (db: string) => void;
}

export function useTableBrowserActions(args: UseTableBrowserActionsArgs): TableBrowserActions {
  const {
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
    navigateToDatabase,
    optimisticallyRemoveDatabases,
    optimisticallyAddDatabase,
    revertOptimisticUpdates
  } = args;

  const { t } = i18nReact.useTranslation();

  // ===== TABLE ACTIONS =====
  const handleRefreshTables = useCallback(async () => {
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
  }, [connector, namespace, compute, currentDb, reloadTables, t, setIsRefreshing]);

  const handleOpenTable = useCallback(
    (tableName: string) => {
      setTable(tableName);
      updatePath(currentDb, tableName);
    },
    [currentDb, updatePath, setTable]
  );

  const handleQuerySelection = useCallback(
    (tableName: string) => {
      type Publish = (topic: string, payload: unknown) => void;
      const w = window as unknown as { huePubSub?: { publish?: Publish } };
      w.huePubSub?.publish?.('open.editor.new.query', {
        type: route.sourceType || 'hive',
        statementType: 'text',
        statementPath: currentDb && tableName ? `${currentDb}.${tableName}` : undefined
      });
    },
    [route.sourceType, currentDb]
  );

  const handleDropTables = useCallback(
    async (tableNames: string[], skipTrash = false) => {
      try {
        // Create URLSearchParams for proper form encoding without qs array notation
        const formData = new URLSearchParams();
        // Send table names as individual form fields (metastore expects getlist)
        tableNames.forEach(name => {
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
    },
    [route.sourceType, connector, namespace, compute, currentDb, reloadTables, t]
  );

  const handleCreateTable = useCallback(() => {
    // Navigate to the importer for table creation
    const hueUrls = (window as unknown as { HUE_URLS?: { IMPORTER_CREATE_TABLE?: string } })
      .HUE_URLS;
    const baseUrl = hueUrls?.IMPORTER_CREATE_TABLE;

    if (baseUrl && currentDb) {
      // Get the base path (e.g., "/hue")
      const basePath = window.location.pathname.split('/tablebrowser')[0] || '';

      // Construct URL with base path, database name and query parameters
      const sourceType = route.sourceType || getConnectorIdOrType(connector) || 'hive';
      const params = new URLSearchParams({
        sourceType,
        ...(namespace && { namespace: JSON.stringify(namespace) }),
        ...(compute && { compute: JSON.stringify(compute) })
      });

      const url = `${basePath}${baseUrl}${currentDb}/?${params.toString()}`;
      window.open(url, '_blank');
    }
  }, [currentDb, route.sourceType, connector, namespace, compute]);

  // ===== DATABASE ACTIONS =====
  const handleRefreshDatabases = useCallback(async () => {
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
  }, [connector, namespace, compute, reloadDatabases, t, setIsRefreshing]);

  const handleOpenDatabase = useCallback(
    (db: string) => {
      if (db !== currentDb) {
        selectDb(db);
      }
      setTable(undefined);
      updatePath(db, undefined);
    },
    [currentDb, selectDb, updatePath, setTable]
  );

  const handleDropDatabases = useCallback(
    async (names: string[]) => {
      // Optimistically remove databases from the list immediately
      optimisticallyRemoveDatabases(names);

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
          // If there's an error message, revert optimistic update and reload
          revertOptimisticUpdates();
          await reloadDatabases();
          return;
        }

        // For successful operations, reload databases to get the authoritative state
        // This will reset the optimistic state and confirm the deletion
        await reloadDatabases();
      } catch (error) {
        notifyError(t('Failed to drop databases'));
        // On error, revert optimistic update and reload to restore correct state
        revertOptimisticUpdates();
        await reloadDatabases();
      }
    },
    [
      route.sourceType,
      connector,
      namespace,
      compute,
      reloadDatabases,
      optimisticallyRemoveDatabases,
      revertOptimisticUpdates,
      t
    ]
  );

  const handleCreateDatabase = useCallback(
    async (name: string, comment?: string, location?: string) => {
      // Optimistically add the database to the list immediately
      optimisticallyAddDatabase(name);

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
          // Revert optimistic update and reload to restore correct state
          revertOptimisticUpdates();
          await reloadDatabases();
          return;
        }

        // For successful operations, reload databases to get the authoritative state
        // This will reset the optimistic state and confirm the creation
        await reloadDatabases();
      } catch (error) {
        notifyError(t('Failed to create database'));
        // On error, revert optimistic update and reload to restore correct state
        revertOptimisticUpdates();
        await reloadDatabases();
      }
    },
    [reloadDatabases, optimisticallyAddDatabase, revertOptimisticUpdates, t]
  );

  // ===== SOURCE ACTIONS =====
  const handleRefreshSources = useCallback(async () => {
    try {
      setIsRefreshing(true);
      // Refresh connectors/sources by reloading databases which triggers connector refresh
      await reloadDatabases();
    } catch {
      notifyError(t('Failed to refresh data sources'));
    } finally {
      setIsRefreshing(false);
    }
  }, [reloadDatabases, t, setIsRefreshing]);

  const handleSelectSource = useCallback(
    (src: string) => {
      const wanted = (connectors || []).find(
        c => c.type === src || (c as unknown as { id?: string }).id === src
      );
      if (wanted) {
        setConnector(wanted);
      }
      // Reset DB and Table on source change
      selectDb(undefined);
      setTable(undefined);
      navigateToSource(src);
    },
    [connectors, setConnector, selectDb, setTable, navigateToSource]
  );

  // ===== NAVIGATION ACTIONS =====
  const handleClickDatabases = useCallback(() => {
    // Navigate to source root
    const sourceType = route.sourceType || 'hive';
    selectDb(undefined);
    setTable(undefined);
    navigateToSource(sourceType);
  }, [route.sourceType, selectDb, setTable, navigateToSource]);

  const handleClickDatabase = useCallback(
    (db: string) => {
      // Navigate to database
      if (db !== currentDb) {
        selectDb(db);
      }
      setTable(undefined);
      navigateToDatabase(db);
    },
    [currentDb, selectDb, setTable, navigateToDatabase]
  );

  return {
    // Table actions
    handleRefreshTables,
    handleOpenTable,
    handleQuerySelection,
    handleDropTables,
    handleCreateTable,

    // Database actions
    handleRefreshDatabases,
    handleOpenDatabase,
    handleDropDatabases,
    handleCreateDatabase,

    // Source actions
    handleRefreshSources,
    handleSelectSource,

    // Navigation actions
    handleClickDatabases,
    handleClickDatabase
  };
}

export default useTableBrowserActions;

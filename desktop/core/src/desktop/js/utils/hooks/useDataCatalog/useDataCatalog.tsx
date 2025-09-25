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

import { useState, useEffect } from 'react';
import { Connector, Compute, Namespace, EditorInterpreter } from '../../../config/types';
import { DataCatalog } from '../../../catalog/dataCatalog';
import { filterEditorConnectors } from '../../../config/hueConfig';
import { getNamespaces } from '../../../catalog/contextCatalog';

interface TableEntry {
  name: string;
  type: string;
  comment: string;
}

interface LoadingState {
  connector: boolean;
  namespace: boolean;
  compute: boolean;
  database: boolean;
  table: boolean;
}

const fetchSourceMeta = async (
  connector: Connector,
  namespace: Namespace,
  compute: Compute,
  path: string[] = []
): Promise<{ databases?: string[]; tables_meta?: TableEntry[] }> => {
  const dataCatalog = new DataCatalog(connector);
  const dataEntry = await dataCatalog.getEntry({
    namespace,
    compute,
    path,
    definition: { type: 'source' }
  });
  const result = await dataEntry.getSourceMeta();

  return result;
};

interface UseDataCatalog {
  loading: LoadingState;
  connectors: EditorInterpreter[];
  connector: Connector | null;
  namespace: Namespace | null;
  computes: Compute[];
  compute: Compute | null;
  database: string | undefined;
  databases: string[];
  tables: TableEntry[];
  setConnector: (connector: Connector) => void;
  setNamespace: (namespace: Namespace) => void;
  setCompute: (compute: Compute) => void;
  setDatabase: (database: string | undefined) => void;
  reloadDatabases: () => Promise<void>;
  reloadTables: () => Promise<void>;
  // Optimistic update methods
  optimisticallyRemoveDatabases: (databaseNames: string[]) => void;
  optimisticallyAddDatabase: (databaseName: string) => void;
  revertOptimisticUpdates: () => void;
}

interface UseDataCatalogOptions {
  autoSelectFirstDatabase?: boolean;
  autoSelectFirstConnector?: boolean;
}

export const useDataCatalog = (options?: UseDataCatalogOptions): UseDataCatalog => {
  const { autoSelectFirstDatabase = true, autoSelectFirstConnector = true } = options || {};
  const [connectors, setConnectors] = useState<EditorInterpreter[]>([]);
  const [computes, setComputes] = useState<Compute[]>([]);
  const [connector, setConnector] = useState<Connector | null>(null);
  const [namespace, setNamespace] = useState<Namespace | null>(null);
  const [compute, setCompute] = useState<Compute | null>(null);
  const [databases, setDatabases] = useState<string[]>([]);
  const [database, setDatabase] = useState<string | undefined>();
  const [tables, setTables] = useState<TableEntry[]>([]);
  const [loading, setLoading] = useState<LoadingState>({
    connector: false,
    namespace: false,
    compute: false,
    database: false,
    table: false
  });

  // Track original databases for optimistic updates
  const [originalDatabases, setOriginalDatabases] = useState<string[] | null>(null);

  const loadDatabases = async (
    namespace: Namespace,
    compute: Compute,
    connector: Connector
  ): Promise<void> => {
    try {
      setLoading(prev => ({ ...prev, database: true }));
      const databaseEntries = await fetchSourceMeta(connector, namespace, compute);
      const newDatabases = databaseEntries?.databases ?? [];
      setDatabases(newDatabases);
      setOriginalDatabases(null); // Reset optimistic state
      if (autoSelectFirstDatabase) {
        setDatabase(newDatabases[0]);
      }
    } catch (error) {
      setDatabases([]);
      setDatabase(undefined);
      setTables([]);
      setOriginalDatabases(null);
    } finally {
      setLoading(prev => ({ ...prev, database: false }));
    }
  };

  const loadTables = async (
    connector: Connector,
    namespace: Namespace,
    compute: Compute,
    database?: string
  ): Promise<void> => {
    if (!database) {
      return;
    }
    try {
      setLoading(prev => ({ ...prev, table: true }));
      const tableEntries = await fetchSourceMeta(connector, namespace, compute, [database]);
      // Include both tables and views (don't filter by type)
      setTables(tableEntries?.tables_meta ?? []);
    } catch (error) {
      setTables([]);
    } finally {
      setLoading(prev => ({ ...prev, table: false }));
    }
  };

  const reloadDatabases = async (): Promise<void> => {
    if (!connector || !namespace || !compute) {
      return;
    }
    try {
      setLoading(prev => ({ ...prev, database: true }));
      const databaseEntries = await fetchSourceMeta(connector, namespace, compute);
      const newDatabases = databaseEntries?.databases ?? [];
      setDatabases(newDatabases);
      setOriginalDatabases(null); // Reset optimistic state
      // Do not auto-select a database on reload; preserve current selection
    } catch (error) {
      setDatabases([]);
      setOriginalDatabases(null);
    } finally {
      setLoading(prev => ({ ...prev, database: false }));
    }
  };

  const reloadTables = async (): Promise<void> => {
    if (!connector || !namespace || !compute || !database) {
      return;
    }
    try {
      setLoading(prev => ({ ...prev, table: true }));
      const tableEntries = await fetchSourceMeta(connector, namespace, compute, [database]);
      // Include both tables and views (don't filter by type)
      setTables(tableEntries?.tables_meta ?? []);
    } catch (error) {
      setTables([]);
    } finally {
      setLoading(prev => ({ ...prev, table: false }));
    }
  };

  const loadNamespaces = async (connector: Connector) => {
    try {
      setLoading(prev => ({ ...prev, namespace: true, compute: true }));
      const { namespaces } = await getNamespaces({ connector });

      const namespacesWithCompute = namespaces.filter(namespace => namespace.computes.length);

      if (namespacesWithCompute.length) {
        const namespace = namespacesWithCompute[0];
        setNamespace(namespace);

        const computes = namespace.computes;
        const compute = computes[0];
        setComputes(computes);
        setCompute(computes[0]);

        await loadDatabases(namespace, compute, connector);
      } else {
        setNamespace(namespaces[0]);
      }
    } catch (error) {
      setNamespace(null);
      setCompute(null);
      setDatabases([]);
      setDatabase(undefined);
      setTables([]);
    } finally {
      setLoading(prev => ({ ...prev, namespace: false, compute: false }));
    }
  };

  useEffect(() => {
    if (connector && namespace && compute && database) {
      loadTables(connector, namespace, compute, database);
    }
  }, [namespace, compute, connector, database]);

  useEffect(() => {
    setLoading(prev => ({ ...prev, connector: true }));
    const availableConnectors = filterEditorConnectors(connector => connector.is_sql);

    if (availableConnectors.length > 0) {
      setConnectors(availableConnectors);
      if (autoSelectFirstConnector) {
        setConnector(availableConnectors[0]);
      }
    }
    setLoading(prev => ({ ...prev, connector: false }));
  }, []);

  // Reload namespaces, computes and databases when connector changes (e.g., source switch)
  useEffect(() => {
    if (connector) {
      // Clear old data immediately to prevent stale data flash
      setDatabases([]);
      setDatabase(undefined);
      setTables([]);
      setOriginalDatabases(null);

      loadNamespaces(connector);
    }
  }, [connector]);

  // Optimistic update methods
  const optimisticallyRemoveDatabases = (databaseNames: string[]): void => {
    if (originalDatabases === null) {
      // Store original state before first optimistic update
      setOriginalDatabases(databases);
    }

    // Remove databases optimistically
    const updatedDatabases = databases.filter(db => !databaseNames.includes(db));
    setDatabases(updatedDatabases);

    // If current database was deleted, clear it
    if (database && databaseNames.includes(database)) {
      setDatabase(undefined);
    }
  };

  const optimisticallyAddDatabase = (databaseName: string): void => {
    if (originalDatabases === null) {
      // Store original state before first optimistic update
      setOriginalDatabases(databases);
    }

    // Add database optimistically (avoid duplicates)
    if (!databases.includes(databaseName)) {
      const updatedDatabases = [...databases, databaseName].sort();
      setDatabases(updatedDatabases);
    }
  };

  const revertOptimisticUpdates = (): void => {
    if (originalDatabases !== null) {
      // Restore original state
      setDatabases(originalDatabases);
      setOriginalDatabases(null);

      // If current database is not in original list, clear it
      if (database && !originalDatabases.includes(database)) {
        setDatabase(undefined);
      }
    }
  };

  return {
    loading,
    connectors,
    connector,
    namespace,
    computes,
    compute,
    databases,
    database,
    tables,
    setConnector,
    setNamespace,
    setCompute,
    setDatabase,
    reloadDatabases,
    reloadTables,
    // Optimistic update methods
    optimisticallyRemoveDatabases,
    optimisticallyAddDatabase,
    revertOptimisticUpdates
  };
};

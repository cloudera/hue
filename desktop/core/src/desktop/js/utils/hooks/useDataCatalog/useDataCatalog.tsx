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
  return dataEntry.getSourceMeta();
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
}

export const useDataCatalog = (): UseDataCatalog => {
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

  const loadDatabases = async (
    namespace: Namespace,
    compute: Compute,
    connector: Connector
  ): Promise<void> => {
    try {
      setLoading(prev => ({ ...prev, database: true }));
      const databaseEntries = await fetchSourceMeta(connector, namespace, compute);
      setDatabases(databaseEntries?.databases ?? []);
      setDatabase(databaseEntries.databases?.[0]);
    } catch (error) {
      setDatabases([]);
      setDatabase(undefined);
      setTables([]);
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
      const tables = tableEntries?.tables_meta?.filter(
        table => table.type?.toLowerCase() === 'table'
      );
      setTables(tables ?? []);
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
      setConnector(availableConnectors[0]);
      loadNamespaces(availableConnectors[0]);
    }
    setLoading(prev => ({ ...prev, connector: false }));
  }, []);

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
    setDatabase
  };
};

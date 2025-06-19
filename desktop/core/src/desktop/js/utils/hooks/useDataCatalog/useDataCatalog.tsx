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

const fetchSourceMeta = async (
  connector: Connector,
  namespace: Namespace,
  compute: Compute,
  path: string[] = []
): Promise<{ databases?: string[]; tables_meta?: string[] }> => {
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
  loading: boolean;
  connectors: EditorInterpreter[];
  connector: Connector | null;
  namespace: Namespace | null;
  computes: Compute[];
  compute: Compute | null;
  database: string | null;
  databases: string[];
  tables: string[];
  setConnector: (connector: Connector) => void;
  setNamespace: (namespace: Namespace) => void;
  setCompute: (compute: Compute) => void;
  setDatabase: (database: string | null) => void;
}

export const useDataCatalog = (): UseDataCatalog => {
  const [connectors, setConnectors] = useState<EditorInterpreter[]>([]);
  const [computes, setComputes] = useState<Compute[]>([]);
  const [connector, setConnector] = useState<Connector | null>(null);
  const [namespace, setNamespace] = useState<Namespace | null>(null);
  const [compute, setCompute] = useState<Compute | null>(null);
  const [loading, setLoading] = useState(true);
  const [databases, setDatabases] = useState<string[]>([]);
  const [database, setDatabase] = useState<string | null>(null);
  const [tables, setTables] = useState<string[]>([]);

  const loadDatabases = async (
    namespace: Namespace,
    compute: Compute,
    connector: Connector
  ): Promise<void> => {
    try {
      setLoading(true);
      const databaseEntries = await fetchSourceMeta(connector, namespace, compute);
      setDatabases(databaseEntries?.databases ?? []);
      setDatabase(databaseEntries.databases?.[0] ?? null);
      await loadTables(connector, namespace, compute, databaseEntries.databases?.[0]);
    } catch (error) {
      console.error('Error loading databases:', error);
    } finally {
      setLoading(false);
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
      setLoading(true);
      const tableEntries = await fetchSourceMeta(connector, namespace, compute, [database]);
      setTables(tableEntries?.tables_meta ?? []);
    } catch (error) {
      console.error('Error loading tables:', error);
      setTables([]);
    } finally {
      setLoading(false);
    }
  };

  const loadNamespaces = async (connector: Connector) => {
    try {
      setLoading(true);
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
      console.error('Error loading namespaces:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (connector && namespace && compute && database) {
      loadTables(connector, namespace, compute, database);
    }
  }, [namespace, compute, connector, database]);

  useEffect(() => {
    const availableConnectors = filterEditorConnectors(connector => connector.is_sql);

    if (availableConnectors.length > 0) {
      setConnectors(availableConnectors);
      setConnector(availableConnectors[0]);
      loadNamespaces(availableConnectors[0]);
    }
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

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

import { useCallback, useEffect, useState } from 'react';
import { post } from '../../../api/utils';
import { getConnectorIdOrType } from '../utils/connector';
import type { Connector } from '../../../config/types';

export interface DatabaseProperties {
  owner_name?: string;
  owner_type?: string;
  location?: string;
  hdfs_link?: string;
  parameters?: string;
}

export interface UseDatabasePropertiesArgs {
  sourceType?: string;
  connector?: Connector | null;
  database?: string;
  table?: string;
}

export interface DatabasePropertiesState {
  properties?: DatabaseProperties;
  loading: boolean;
  fetchProperties: (databaseName: string) => Promise<void>;
}

export function useDatabaseProperties({
  sourceType,
  connector,
  database,
  table
}: UseDatabasePropertiesArgs): DatabasePropertiesState {
  const [properties, setProperties] = useState<DatabaseProperties | undefined>(undefined);
  const [loading, setLoading] = useState(false);

  const fetchProperties = useCallback(
    async (databaseName: string) => {
      if (!databaseName) {
        return;
      }

      try {
        setLoading(true);
        const effectiveType = (sourceType || getConnectorIdOrType(connector) || 'hive')
          .toString()
          .toLowerCase();

        // Skip Hive Metastore call for connectors that don't use it (e.g. PostgreSQL)
        if (effectiveType === 'postgresql') {
          setProperties(undefined);
          return;
        }
        const result = await post<{ status: number; data: DatabaseProperties }>(
          `/metastore/databases/${encodeURIComponent(databaseName)}/metadata`,
          {
            source_type: effectiveType
          },
          {
            silenceErrors: true
          }
        );

        if (result?.status === 0 && result.data) {
          setProperties(result.data);
        } else {
          setProperties(undefined);
        }
      } catch (error) {
        console.warn('Failed to fetch database properties:', error);
        setProperties(undefined);
      } finally {
        setLoading(false);
      }
    },
    [sourceType, connector]
  );

  // Fetch database properties when database changes
  useEffect(() => {
    if (database && !table) {
      fetchProperties(database);
    } else {
      setProperties(undefined);
    }
  }, [database, table, fetchProperties]);

  return {
    properties,
    loading,
    fetchProperties
  };
}

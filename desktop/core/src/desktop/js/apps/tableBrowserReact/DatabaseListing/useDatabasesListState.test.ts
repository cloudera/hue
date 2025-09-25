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

import { renderHook } from '@testing-library/react-hooks';
import { useDatabasesListState } from './useDatabasesListState';
import type { Connector, Namespace, Compute } from '../../../config/types';

// Mock the useDescriptionManager hook
jest.mock('../hooks/useDescriptionManager', () => ({
  useDescriptionManager: jest.fn(() => ({
    descriptions: {},
    editingItem: null,
    editingValue: '',
    setEditingItem: jest.fn(),
    setEditingValue: jest.fn(),
    saveDescription: jest.fn()
  }))
}));

describe('useDatabasesListState', () => {
  const mockConnectorHive: Connector = {
    id: 'hive',
    type: 'hive',
    displayName: 'Hive',
    is_sql: true,
    dialect: 'hive'
  } as Connector;

  const mockConnectorImpala: Connector = {
    id: 'impala',
    type: 'impala',
    displayName: 'Impala',
    is_sql: true,
    dialect: 'impala'
  } as Connector;

  const mockNamespace: Namespace = {
    id: 'default',
    name: 'default'
  } as Namespace;

  const mockCompute: Compute = {
    id: 'default',
    name: 'default'
  } as Compute;

  const mockDatabases = ['db1', 'db2', 'db3'];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('stale data prevention', () => {
    it('should prevent stale databases from being passed to useDescriptionManager when connector changes', () => {
      const { useDescriptionManager } = require('../hooks/useDescriptionManager');

      // Initial render with Hive connector and databases
      const { rerender } = renderHook(
        ({ connector, databases }) =>
          useDatabasesListState({
            connector,
            namespace: mockNamespace,
            compute: mockCompute,
            databases,
            currentDatabase: undefined
          }),
        {
          initialProps: {
            connector: mockConnectorHive,
            databases: mockDatabases
          }
        }
      );

      // Verify useDescriptionManager was called with Hive databases
      expect(useDescriptionManager).toHaveBeenCalledWith(
        expect.objectContaining({
          connector: mockConnectorHive,
          items: mockDatabases
        })
      );

      // Clear the mock to track the next call
      useDescriptionManager.mockClear();

      // Switch to Impala connector but databases still contain old Hive data
      // This simulates the race condition where connector changes before databases are cleared
      rerender({
        connector: mockConnectorImpala,
        databases: mockDatabases // Still contains Hive databases!
      });

      // Verify useDescriptionManager was called with EMPTY array, not stale Hive databases
      expect(useDescriptionManager).toHaveBeenCalledWith(
        expect.objectContaining({
          connector: mockConnectorImpala,
          items: [] // Should be empty, not mockDatabases
        })
      );
    });

    it('should allow databases through once connector has stabilized', () => {
      const { useDescriptionManager } = require('../hooks/useDescriptionManager');
      const impalaDBs = ['_impala_builtins', 'default'];

      // Initial render with Impala connector and no databases
      const { rerender } = renderHook(
        ({ connector, databases }) =>
          useDatabasesListState({
            connector,
            namespace: mockNamespace,
            compute: mockCompute,
            databases,
            currentDatabase: undefined
          }),
        {
          initialProps: {
            connector: mockConnectorImpala,
            databases: []
          }
        }
      );

      useDescriptionManager.mockClear();

      // Now new Impala databases arrive
      rerender({
        connector: mockConnectorImpala, // Same connector
        databases: impalaDBs // New databases for same connector
      });

      // Verify useDescriptionManager receives the new databases since connector hasn't changed
      expect(useDescriptionManager).toHaveBeenCalledWith(
        expect.objectContaining({
          connector: mockConnectorImpala,
          items: impalaDBs
        })
      );
    });

    it('should return empty array when connector/namespace/compute are missing', () => {
      const { useDescriptionManager } = require('../hooks/useDescriptionManager');

      renderHook(() =>
        useDatabasesListState({
          connector: undefined,
          namespace: mockNamespace,
          compute: mockCompute,
          databases: mockDatabases,
          currentDatabase: undefined
        })
      );

      expect(useDescriptionManager).toHaveBeenCalledWith(
        expect.objectContaining({
          items: [] // Should be empty when connector is missing
        })
      );
    });

    it('should handle multiple rapid connector switches correctly', () => {
      const { useDescriptionManager } = require('../hooks/useDescriptionManager');

      const { rerender } = renderHook(
        ({ connector, databases }) =>
          useDatabasesListState({
            connector,
            namespace: mockNamespace,
            compute: mockCompute,
            databases,
            currentDatabase: undefined
          }),
        {
          initialProps: {
            connector: mockConnectorHive,
            databases: ['hive_db1', 'hive_db2']
          }
        }
      );

      useDescriptionManager.mockClear();

      // Rapid switch: Hive -> Impala -> Hive
      rerender({
        connector: mockConnectorImpala,
        databases: ['hive_db1', 'hive_db2'] // Stale Hive databases
      });

      // Should block stale data
      expect(useDescriptionManager).toHaveBeenCalledWith(
        expect.objectContaining({
          connector: mockConnectorImpala,
          items: []
        })
      );

      useDescriptionManager.mockClear();

      // Switch back to Hive with stale Impala databases
      rerender({
        connector: mockConnectorHive,
        databases: ['_impala_builtins', 'default'] // Stale Impala databases
      });

      // Should block stale data again
      expect(useDescriptionManager).toHaveBeenCalledWith(
        expect.objectContaining({
          connector: mockConnectorHive,
          items: []
        })
      );
    });
  });
});

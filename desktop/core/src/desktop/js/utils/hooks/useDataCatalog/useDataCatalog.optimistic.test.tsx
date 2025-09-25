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

/**
 * Tests for optimistic update functionality in useDataCatalog hook
 */

import { renderHook, act } from '@testing-library/react';
import { useDataCatalog } from './useDataCatalog';

// Mock the API calls
jest.mock('../../../catalog/contextCatalog', () => ({
  getNamespaces: jest.fn()
}));

jest.mock('../../../config/hueConfig', () => ({
  filterEditorConnectors: jest.fn()
}));

const mockGetNamespaces = require('../../../catalog/contextCatalog').getNamespaces;
const mockFilterEditorConnectors = require('../../../config/hueConfig').filterEditorConnectors;

// Mock DataCatalog
jest.mock('../../../catalog/dataCatalog', () => ({
  DataCatalog: jest.fn().mockImplementation(() => ({
    getEntry: jest.fn().mockResolvedValue({
      getSourceMeta: jest.fn().mockResolvedValue({
        databases: ['db1', 'db2', 'db3'],
        tables_meta: []
      })
    })
  }))
}));

describe('useDataCatalog optimistic updates', () => {
  const mockConnector = { id: 'hive', type: 'hive', is_sql: true };
  const mockNamespace = { id: 'default', name: 'default', computes: [{ id: 'compute1' }] };
  const mockCompute = { id: 'compute1' };

  beforeEach(() => {
    jest.clearAllMocks();

    mockFilterEditorConnectors.mockReturnValue([mockConnector]);
    mockGetNamespaces.mockResolvedValue({
      namespaces: [mockNamespace]
    });
  });

  it('should optimistically remove databases', async () => {
    const { result } = renderHook(() => useDataCatalog({ autoSelectFirstConnector: false }));

    // Wait for initial load to complete
    await act(async () => {
      result.current.setConnector(mockConnector);
      // Allow async operations to complete
      await new Promise(resolve => setTimeout(resolve, 100));
    });

    // Verify initial state
    expect(result.current.databases).toEqual(['db1', 'db2', 'db3']);

    // Perform optimistic removal
    act(() => {
      result.current.optimisticallyRemoveDatabases(['db2']);
    });

    // Verify optimistic update
    expect(result.current.databases).toEqual(['db1', 'db3']);
  });

  it('should optimistically add databases', async () => {
    const { result } = renderHook(() => useDataCatalog({ autoSelectFirstConnector: false }));

    // Wait for initial load to complete
    await act(async () => {
      result.current.setConnector(mockConnector);
      await new Promise(resolve => setTimeout(resolve, 100));
    });

    // Verify initial state
    expect(result.current.databases).toEqual(['db1', 'db2', 'db3']);

    // Perform optimistic addition
    act(() => {
      result.current.optimisticallyAddDatabase('new_db');
    });

    // Verify optimistic update (should be sorted)
    expect(result.current.databases).toEqual(['db1', 'db2', 'db3', 'new_db']);
  });

  it('should revert optimistic updates', async () => {
    const { result } = renderHook(() => useDataCatalog({ autoSelectFirstConnector: false }));

    // Wait for initial load to complete
    await act(async () => {
      result.current.setConnector(mockConnector);
      await new Promise(resolve => setTimeout(resolve, 100));
    });

    const originalDatabases = result.current.databases;
    expect(originalDatabases).toEqual(['db1', 'db2', 'db3']);

    // Perform optimistic changes
    act(() => {
      result.current.optimisticallyRemoveDatabases(['db2']);
    });

    act(() => {
      result.current.optimisticallyAddDatabase('new_db');
    });

    // Verify changes (should be sorted)
    expect(result.current.databases).toEqual(['db1', 'db3', 'new_db']);

    // Revert optimistic updates
    act(() => {
      result.current.revertOptimisticUpdates();
    });

    // Verify reversion
    expect(result.current.databases).toEqual(originalDatabases);
  });

  it('should clear current database if it was optimistically removed', async () => {
    const { result } = renderHook(() => useDataCatalog({ autoSelectFirstConnector: false }));

    // Wait for initial load to complete
    await act(async () => {
      result.current.setConnector(mockConnector);
      await new Promise(resolve => setTimeout(resolve, 100));
    });

    // Set a current database
    act(() => {
      result.current.setDatabase('db2');
    });

    expect(result.current.database).toBe('db2');

    // Optimistically remove the current database
    act(() => {
      result.current.optimisticallyRemoveDatabases(['db2']);
    });

    // Verify current database is cleared
    expect(result.current.database).toBeUndefined();
    expect(result.current.databases).toEqual(['db1', 'db3']);
  });

  it('should not add duplicate databases', async () => {
    const { result } = renderHook(() => useDataCatalog({ autoSelectFirstConnector: false }));

    // Wait for initial load to complete
    await act(async () => {
      result.current.setConnector(mockConnector);
      await new Promise(resolve => setTimeout(resolve, 100));
    });

    expect(result.current.databases).toEqual(['db1', 'db2', 'db3']);

    // Try to add existing database
    act(() => {
      result.current.optimisticallyAddDatabase('db2');
    });

    // Verify no duplicate was added
    expect(result.current.databases).toEqual(['db1', 'db2', 'db3']);
  });

  it('should reset optimistic state when reloading databases', async () => {
    const { result } = renderHook(() => useDataCatalog({ autoSelectFirstConnector: false }));

    // Wait for initial load to complete
    await act(async () => {
      result.current.setConnector(mockConnector);
      await new Promise(resolve => setTimeout(resolve, 100));
    });

    // Perform optimistic changes
    act(() => {
      result.current.optimisticallyRemoveDatabases(['db1']);
    });

    expect(result.current.databases).toEqual(['db2', 'db3']);

    // Reload databases
    await act(async () => {
      await result.current.reloadDatabases();
    });

    // Verify optimistic state is reset
    expect(result.current.databases).toEqual(['db1', 'db2', 'db3']);
  });
});

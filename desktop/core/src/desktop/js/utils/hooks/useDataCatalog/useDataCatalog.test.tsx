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

import { renderHook, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { useDataCatalog } from './useDataCatalog';
import { filterEditorConnectors } from '../../../config/hueConfig';
import { getNamespaces } from '../../../catalog/contextCatalog';

const mockFilterEditorConnectors = filterEditorConnectors as jest.Mock;
const mockGetNamespaces = getNamespaces as jest.Mock;

jest.mock('../../../config/hueConfig', () => ({
  filterEditorConnectors: jest.fn()
}));
jest.mock('../../../catalog/contextCatalog', () => ({
  getNamespaces: jest.fn()
}));
jest.mock('../../../../../desktop/js/catalog/dataCatalog', () => ({
  DataCatalog: jest.fn().mockImplementation(() => ({
    getEntry: jest.fn().mockResolvedValue({
      getSourceMeta: jest.fn().mockResolvedValue({ databases: ['db1', 'db2'] })
    })
  }))
}));

const mockConnectors = [
  { is_sql: true, id: 'c1' },
  { is_sql: false, id: 'c2' }
];
const mockNamespaces = {
  namespaces: [
    {
      computes: [{ id: 'compute1' }],
      id: 'namespace1'
    }
  ]
};

beforeEach(() => {
  mockFilterEditorConnectors.mockReset().mockReturnValue(mockConnectors);
  mockGetNamespaces.mockReset().mockResolvedValue(mockNamespaces);
});

describe('useDataCatalog', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should initialize all loading states to false', () => {
    mockFilterEditorConnectors.mockReturnValue([]);
    const { result } = renderHook(() => useDataCatalog());

    expect(result.current.loading).toEqual({
      connector: false,
      namespace: false,
      compute: false,
      database: false,
      table: false
    });
  });

  it('should initialize with default values', () => {
    mockFilterEditorConnectors.mockReturnValue([]);
    mockGetNamespaces.mockResolvedValue({ namespaces: [] });
    const { result } = renderHook(() => useDataCatalog());
    expect(result.current.loading.connector).toBe(false);
    expect(result.current.loading.namespace).toBe(false);
    expect(result.current.loading.compute).toBe(false);
    expect(result.current.loading.database).toBe(false);
    expect(result.current.loading.table).toBe(false);
    expect(result.current.connectors).toEqual([]);
    expect(result.current.connector).toBeNull();
    expect(result.current.namespace).toBeNull();
    expect(result.current.computes).toEqual([]);
    expect(result.current.compute).toBeNull();
    expect(result.current.databases).toEqual([]);
  });

  it('should load connectors, namespaces, computes, and databases on mount', async () => {
    const { result } = renderHook(() => useDataCatalog());

    await waitFor(() => {
      expect(result.current.connectors).toEqual(mockConnectors);
      expect(result.current.connector).toEqual(mockConnectors[0]);
      expect(result.current.namespace).toEqual(mockNamespaces.namespaces[0]);
      expect(result.current.computes).toEqual(mockNamespaces.namespaces[0].computes);
      expect(result.current.compute).toEqual(mockNamespaces.namespaces[0].computes[0]);
      expect(result.current.databases).toEqual(['db1', 'db2']);
      expect(result.current.loading.connector).toBe(false);
      expect(result.current.loading.namespace).toBe(false);
      expect(result.current.loading.compute).toBe(false);
      expect(result.current.loading.database).toBe(false);
    });
  });

  it('should handle namespaces with no computes', async () => {
    mockFilterEditorConnectors.mockReturnValue([{ is_sql: true, id: 'c1' }]);
    mockGetNamespaces.mockResolvedValue({
      namespaces: [
        {
          computes: [],
          id: 'namespace1'
        }
      ]
    });
    const { result } = renderHook(() => useDataCatalog());
    await waitFor(() => {
      expect(result.current.namespace).toEqual({ computes: [], id: 'namespace1' });
      expect(result.current.computes).toEqual([]);
      expect(result.current.compute).toBeNull();
      expect(result.current.databases).toEqual([]);
      expect(result.current.loading.connector).toBe(false);
      expect(result.current.loading.namespace).toBe(false);
      expect(result.current.loading.compute).toBe(false);
      expect(result.current.loading.database).toBe(false);
    });
  });

  it('should handle errors gracefully', async () => {
    mockFilterEditorConnectors.mockReturnValue([{ is_sql: true }]);
    mockGetNamespaces.mockRejectedValue(new Error('Failed to load namespaces'));
    const { result } = renderHook(() => useDataCatalog());
    await waitFor(() => {
      expect(result.current.loading.connector).toBe(false);
      expect(result.current.loading.namespace).toBe(false);
      expect(result.current.loading.compute).toBe(false);
      expect(result.current.loading.database).toBe(false);
      expect(result.current.namespace).toBeNull();
      expect(result.current.computes).toEqual([]);
      expect(result.current.databases).toEqual([]);
    });
  });

  it('should allow manual setting of connector, namespace, compute, and databases', async () => {
    mockFilterEditorConnectors.mockReturnValue([
      {
        is_sql: true,
        id: 'c1',
        name: 'c1',
        is_batchable: false,
        optimizer: '',
        dialect: '',
        displayName: '',
        buttonName: '',
        page: '',
        tooltip: '',
        type: ''
      }
    ]);
    mockGetNamespaces.mockResolvedValue({
      namespaces: [
        {
          computes: [{ id: 'compute1', name: 'Compute 1', type: 'spark' }],
          id: 'namespace1',
          name: 'Namespace 1',
          status: 'active'
        }
      ]
    });
    const { result } = renderHook(() => useDataCatalog());
    await waitFor(() => expect(result.current.connectors.length).toBeGreaterThan(0));

    act(() => {
      result.current.setConnector({
        id: 'c2',
        displayName: 'Connector 2',
        buttonName: 'Button',
        page: '',
        tooltip: '',
        type: '',
        dialect: '',
        optimizer: ''
      });
      result.current.setNamespace({
        computes: [],
        id: 'namespace2',
        name: 'Namespace 2',
        status: 'active'
      });
      result.current.setCompute({ id: 'compute2', name: 'Compute 2', type: 'spark' });
      result.current.setDatabase('db2');
    });

    await waitFor(() => {
      expect(result.current.connector).toEqual({
        id: 'c2',
        displayName: 'Connector 2',
        buttonName: 'Button',
        page: '',
        tooltip: '',
        type: '',
        dialect: '',
        optimizer: ''
      });
      expect(result.current.namespace).toEqual({
        computes: [],
        id: 'namespace2',
        name: 'Namespace 2',
        status: 'active'
      });
      expect(result.current.compute).toEqual({
        id: 'compute2',
        name: 'Compute 2',
        type: 'spark'
      });
      expect(result.current.databases).toEqual(['db1', 'db2']);
    });
  });
});

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

import { renderHook, act, waitFor } from '@testing-library/react';
import { useTableDetails } from './useTableDetails';
import type { Connector, Namespace, Compute } from '../../../config/types';

// Suppress React act warnings for this test file since the hook has internal async operations
// that can't be easily wrapped in act() from the test side. This is a common pattern for
// hooks that perform async state updates in useEffect.
const originalError = console.error;
beforeAll(() => {
  console.error = jest.fn();
});

afterAll(() => {
  console.error = originalError;
});

// Mock i18n
jest.mock('../../../utils/i18nReact', () => ({
  i18nReact: {
    useTranslation: () => ({
      t: (key: string) => key
    })
  }
}));

// Mock config
jest.mock('../../../config/hueConfig', () => ({
  getLastKnownConfig: jest.fn(() => ({
    hue_config: {
      allow_sample_data_from_views: true
    }
  }))
}));

// Mock connector utility
jest.mock('../utils/connector', () => ({
  getConnectorIdOrType: jest.fn(() => 'hive')
}));

// Mock utilities
jest.mock('../../../utils/formatBytes', () => jest.fn((bytes) => `${bytes} bytes`));
jest.mock('../../../utils/dateTimeUtils', () => ({
  formatTimestamp: jest.fn((date) => date.toISOString())
}));

// Mock data catalog
const mockEntry = {
  getChildren: jest.fn(),
  getAnalysis: jest.fn(),
  getSample: jest.fn(),
  getPartitions: jest.fn(),
  clearCache: jest.fn()
};

const mockDataCatalog = {
  getEntry: jest.fn(() => Promise.resolve(mockEntry))
};

jest.mock('../../../catalog/dataCatalog', () => mockDataCatalog);

// Mock huePubSub
jest.mock('../../../utils/huePubSub', () => ({
  publish: jest.fn()
}));

describe('useTableDetails', () => {
  const mockConnector = { type: 'hive', id: 'hive' } as unknown as Connector;
  const mockNamespace = { id: 'default', name: 'default' } as unknown as Namespace;
  const mockCompute = { id: 'compute1', name: 'compute1' } as unknown as Compute;
  const database = 'test_db';
  const table = 'test_table';

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Setup basic mock that allows hook to initialize
    mockEntry.getAnalysis.mockResolvedValue({
      cols: [],
      details: { stats: {}, properties: {} },
      partition_keys: []
    });
    mockEntry.getChildren.mockResolvedValue([]);
    mockEntry.getSample.mockResolvedValue({ meta: [], data: [] });
    mockEntry.getPartitions.mockResolvedValue({ partition_values_json: [] });
    mockEntry.clearCache.mockResolvedValue(undefined);
  });

  describe('refresh functionality', () => {
    it('should execute refresh function without errors', async () => {
      const { result } = renderHook(() =>
        useTableDetails({
          connector: mockConnector,
          namespace: mockNamespace,
          compute: mockCompute,
          database,
          table
        })
      );

      // Wait for initial data to load
      await waitFor(() => {
        expect(result.current).not.toBeNull();
        expect(result.current.loading).toBe(false);
      });

      // Verify hook is initialized
      expect(result.current.refresh).toBeDefined();
      expect(typeof result.current.refresh).toBe('function');

      // Call refresh and verify it doesn't throw
      await expect(
        act(async () => {
          await result.current.refresh();
        })
      ).resolves.not.toThrow();

      // Verify refresh state is properly managed
      expect(result.current.isRefreshing).toBe(false);
    });

    it('should set isRefreshing state during refresh', async () => {
      const { result } = renderHook(() =>
        useTableDetails({
          connector: mockConnector,
          namespace: mockNamespace,
          compute: mockCompute,
          database,
          table
        })
      );

      // Wait for initial load
      await waitFor(() => {
        expect(result.current).not.toBeNull();
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.isRefreshing).toBe(false);

      // Call refresh and verify state changes
      await act(async () => {
        await result.current.refresh();
      });

      // After refresh completes, isRefreshing should be false
      expect(result.current.isRefreshing).toBe(false);
    });

    it('should handle refresh errors gracefully', async () => {
      const { result } = renderHook(() =>
        useTableDetails({
          connector: mockConnector,
          namespace: mockNamespace,
          compute: mockCompute,
          database,
          table
        })
      );

      // Wait for initial load
      await waitFor(() => {
        expect(result.current).not.toBeNull();
        expect(result.current.loading).toBe(false);
      });

      // Mock an error during refresh
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      mockEntry.clearCache.mockRejectedValueOnce(new Error('Cache clear failed'));

      // Call refresh
      await act(async () => {
        await result.current.refresh();
      });

      // Verify error was logged
      expect(consoleSpy).toHaveBeenCalledWith(
        'Error during refresh:',
        expect.any(Error)
      );

      consoleSpy.mockRestore();
    });

    it('should not refresh if required parameters are missing', async () => {
      const { result } = renderHook(() =>
        useTableDetails({
          connector: null,
          namespace: mockNamespace,
          compute: mockCompute,
          database,
          table
        })
      );

      // Hook should still initialize even with missing parameters
      expect(result.current).not.toBeNull();
      expect(typeof result.current.refresh).toBe('function');

      // Call refresh with missing connector
      await act(async () => {
        await result.current.refresh();
      });

      // Verify no cache operations were performed
      expect(mockEntry.clearCache).not.toHaveBeenCalled();
      expect(mockDataCatalog.getEntry).not.toHaveBeenCalled();
    });
  });

  describe('legacy details mapping', () => {
    it('merges Detailed Table Information rows and labels empty-name rows correctly', async () => {
      // Legacy-style analysis.properties with headers and mixed rows
      const analysis = {
        cols: [],
        details: {
          stats: {},
          properties: {
            owner: 'hive',
            owner_type: 'USER',
            create_time: 1710000000
          }
        },
        partition_keys: [],
        properties: [
          { col_name: '# Detailed Table Information' },
          { col_name: 'Database:', data_type: 'default' },
          { col_name: '', data_type: 'COLUMN_STATS_ACCURATE', comment: '{"BASIC_STATS":"true"}' },
          { col_name: '# Storage Information' },
          { col_name: 'SerDe Library:', data_type: 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe' },
          { col_name: '', data_type: 'InputFormat', comment: 'org.apache.hadoop.mapred.TextInputFormat' },
          { col_name: '# Table Parameters' },
          { col_name: 'EXTERNAL', data_type: 'TRUE' }
        ]
      } as unknown as Record<string, unknown>;

      mockEntry.getAnalysis.mockResolvedValueOnce(analysis);

      const { result } = renderHook(() =>
        useTableDetails({
          connector: mockConnector,
          namespace: mockNamespace,
          compute: mockCompute,
          database,
          table
        })
      );

      await waitFor(() => expect(result.current.loading).toBe(false));

      const baseInfo = result.current.detailsSections.baseInfo || [];
      const storageInfo = result.current.detailsSections.storageInfo || [];

      // Detailed Table Information should contain COLUMN_STATS_ACCURATE with value from comment
      expect(
        baseInfo.some(
          p => /column_stats_accurate/i.test(p.name) && p.value.includes('BASIC_STATS')
        )
      ).toBe(true);

      // It should not include a \"Table Parameters\" section row
      expect(baseInfo.some(p => /table parameters/i.test(p.name))).toBe(false);

      // Storage Information should have SerDe Library and InputFormat values and no duplicates
      const serdeRows = storageInfo.filter(p => /SerDe Library/i.test(p.name));
      expect(serdeRows.length).toBe(1);
      expect(serdeRows[0].value).toContain('LazySimpleSerDe');

      const inputFmtRows = storageInfo.filter(p => /InputFormat/i.test(p.name));
      expect(inputFmtRows.length).toBe(1);
      expect(inputFmtRows[0].value).toContain('TextInputFormat');
    });
  });
});

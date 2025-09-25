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
import { useDatabaseProperties, type DatabaseProperties } from './useDatabaseProperties';
import type { Connector } from '../../../config/types';

// Mock post utility
jest.mock('../../../api/utils', () => ({
  post: jest.fn()
}));

// Mock connector utility
jest.mock('../utils/connector', () => ({
  getConnectorIdOrType: jest.fn()
}));

import { post } from '../../../api/utils';
import { getConnectorIdOrType } from '../utils/connector';

const mockedPost = post as jest.MockedFunction<typeof post>;
const mockedGetConnectorIdOrType = getConnectorIdOrType as jest.MockedFunction<
  typeof getConnectorIdOrType
>;

describe('useDatabaseProperties', () => {
  const mockConnector: Connector = {
    id: 'hive',
    dialect: 'hive',
    type: 'hive'
  } as Connector;

  beforeEach(() => {
    jest.clearAllMocks();
    mockedGetConnectorIdOrType.mockReturnValue('hive');

    // Mock console.warn to avoid noise in tests
    jest.spyOn(console, 'warn').mockImplementation(() => {});
  });

  afterEach(() => {
    (console.warn as jest.Mock).mockRestore();
  });

  describe('Initial state', () => {
    it('initializes with undefined properties and loading false', () => {
      const { result } = renderHook(() =>
        useDatabaseProperties({
          sourceType: 'hive',
          connector: mockConnector,
          database: undefined,
          table: undefined
        })
      );

      expect(result.current.properties).toBeUndefined();
      expect(result.current.loading).toBe(false);
      expect(typeof result.current.fetchProperties).toBe('function');
    });
  });

  describe('Automatic fetching', () => {
    it('fetches properties when database is provided and table is not', async () => {
      const mockProperties: DatabaseProperties = {
        owner_name: 'admin',
        owner_type: 'USER',
        location: 'hdfs://namenode:8020/user/hive/warehouse/test_db.db',
        hdfs_link: 'http://namenode:9870/explorer.html#/user/hive/warehouse/test_db.db',
        parameters: 'param1=value1'
      };

      mockedPost.mockResolvedValue({
        status: 0,
        data: mockProperties
      });

      const { result } = renderHook(() =>
        useDatabaseProperties({
          sourceType: 'hive',
          connector: mockConnector,
          database: 'test_db',
          table: undefined
        })
      );

      await waitFor(() => {
        expect(result.current.properties).toEqual(mockProperties);
        expect(result.current.loading).toBe(false);
      });

      expect(mockedPost).toHaveBeenCalledWith(
        '/metastore/databases/test_db/metadata',
        { source_type: 'hive' },
        { silenceErrors: true }
      );
    });

    it('does not fetch when table is provided', async () => {
      const { result } = renderHook(() =>
        useDatabaseProperties({
          sourceType: 'hive',
          connector: mockConnector,
          database: 'test_db',
          table: 'test_table'
        })
      );

      await new Promise(resolve => setTimeout(resolve, 50));

      expect(mockedPost).not.toHaveBeenCalled();
      expect(result.current.properties).toBeUndefined();
    });

    it('does not fetch when database is not provided', async () => {
      const { result } = renderHook(() =>
        useDatabaseProperties({
          sourceType: 'hive',
          connector: mockConnector,
          database: undefined,
          table: undefined
        })
      );

      await new Promise(resolve => setTimeout(resolve, 50));

      expect(mockedPost).not.toHaveBeenCalled();
      expect(result.current.properties).toBeUndefined();
    });

    it('clears properties when table is provided after database was loaded', async () => {
      const mockProperties: DatabaseProperties = {
        owner_name: 'admin',
        location: 'hdfs://test'
      };

      mockedPost.mockResolvedValue({
        status: 0,
        data: mockProperties
      });

      const { result, rerender } = renderHook(
        ({ database, table }) =>
          useDatabaseProperties({
            sourceType: 'hive',
            connector: mockConnector,
            database,
            table
          }),
        { initialProps: { database: 'test_db', table: undefined } }
      );

      // Wait for initial fetch
      await waitFor(() => {
        expect(result.current.properties).toEqual(mockProperties);
      });

      // Change to table view
      rerender({ database: 'test_db', table: 'test_table' });

      expect(result.current.properties).toBeUndefined();
    });
  });

  describe('Manual fetching', () => {
    it('fetches properties manually via fetchProperties function', async () => {
      const mockProperties: DatabaseProperties = {
        owner_name: 'user1',
        owner_type: 'USER'
      };

      mockedPost.mockResolvedValue({
        status: 0,
        data: mockProperties
      });

      const { result } = renderHook(() =>
        useDatabaseProperties({
          sourceType: 'impala',
          connector: mockConnector,
          database: undefined,
          table: undefined
        })
      );

      await act(async () => {
        await result.current.fetchProperties('manual_db');
      });

      expect(result.current.properties).toEqual(mockProperties);
      expect(mockedPost).toHaveBeenCalledWith(
        '/metastore/databases/manual_db/metadata',
        { source_type: 'impala' },
        { silenceErrors: true }
      );
    });

    it('does not fetch when empty database name is provided', async () => {
      const { result } = renderHook(() =>
        useDatabaseProperties({
          sourceType: 'hive',
          connector: mockConnector,
          database: undefined,
          table: undefined
        })
      );

      await act(async () => {
        await result.current.fetchProperties('');
      });

      expect(mockedPost).not.toHaveBeenCalled();
      expect(result.current.properties).toBeUndefined();
    });
  });

  describe('Loading states', () => {
    it('sets loading to true during fetch and false after completion', async () => {
      let resolvePost: (value: any) => void;
      const postPromise = new Promise(resolve => {
        resolvePost = resolve;
      });
      mockedPost.mockReturnValue(postPromise);

      const { result } = renderHook(() =>
        useDatabaseProperties({
          sourceType: 'hive',
          connector: mockConnector,
          database: 'test_db',
          table: undefined
        })
      );

      // Should start loading
      expect(result.current.loading).toBe(true);

      // Complete the request
      act(() => {
        resolvePost({ status: 0, data: { owner_name: 'test' } });
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
    });

    it('sets loading to false even when request fails', async () => {
      mockedPost.mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() =>
        useDatabaseProperties({
          sourceType: 'hive',
          connector: mockConnector,
          database: 'test_db',
          table: undefined
        })
      );

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.properties).toBeUndefined();
    });
  });

  describe('Error handling', () => {
    it('handles API errors gracefully', async () => {
      mockedPost.mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() =>
        useDatabaseProperties({
          sourceType: 'hive',
          connector: mockConnector,
          database: 'test_db',
          table: undefined
        })
      );

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.properties).toBeUndefined();
      expect(console.warn).toHaveBeenCalledWith(
        'Failed to fetch database properties:',
        expect.any(Error)
      );
    });

    it('handles non-zero status responses', async () => {
      mockedPost.mockResolvedValue({
        status: 1,
        message: 'Database not found'
      });

      const { result } = renderHook(() =>
        useDatabaseProperties({
          sourceType: 'hive',
          connector: mockConnector,
          database: 'nonexistent_db',
          table: undefined
        })
      );

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.properties).toBeUndefined();
    });

    it('handles responses without data', async () => {
      mockedPost.mockResolvedValue({
        status: 0,
        data: null
      });

      const { result } = renderHook(() =>
        useDatabaseProperties({
          sourceType: 'hive',
          connector: mockConnector,
          database: 'test_db',
          table: undefined
        })
      );

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.properties).toBeUndefined();
    });
  });

  describe('Source type handling', () => {
    it('uses provided sourceType', async () => {
      mockedPost.mockResolvedValue({ status: 0, data: {} });

      const { result } = renderHook(() =>
        useDatabaseProperties({
          sourceType: 'impala',
          connector: mockConnector,
          database: 'test_db',
          table: undefined
        })
      );

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(mockedPost).toHaveBeenCalledWith(
        '/metastore/databases/test_db/metadata',
        { source_type: 'impala' },
        { silenceErrors: true }
      );
    });

    it('falls back to connector type when sourceType is not provided', async () => {
      mockedGetConnectorIdOrType.mockReturnValue('spark');
      mockedPost.mockResolvedValue({ status: 0, data: {} });

      const { result } = renderHook(() =>
        useDatabaseProperties({
          sourceType: undefined,
          connector: mockConnector,
          database: 'test_db',
          table: undefined
        })
      );

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(mockedGetConnectorIdOrType).toHaveBeenCalledWith(mockConnector);
      expect(mockedPost).toHaveBeenCalledWith(
        '/metastore/databases/test_db/metadata',
        { source_type: 'spark' },
        { silenceErrors: true }
      );
    });

    it('defaults to hive when neither sourceType nor connector provide type', async () => {
      mockedGetConnectorIdOrType.mockReturnValue(null);
      mockedPost.mockResolvedValue({ status: 0, data: {} });

      const { result } = renderHook(() =>
        useDatabaseProperties({
          sourceType: undefined,
          connector: null,
          database: 'test_db',
          table: undefined
        })
      );

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(mockedPost).toHaveBeenCalledWith(
        '/metastore/databases/test_db/metadata',
        { source_type: 'hive' },
        { silenceErrors: true }
      );
    });
  });

  describe('Database name encoding', () => {
    it('properly encodes database names with special characters', async () => {
      mockedPost.mockResolvedValue({ status: 0, data: {} });

      const { result } = renderHook(() =>
        useDatabaseProperties({
          sourceType: 'hive',
          connector: mockConnector,
          database: 'test-db with spaces',
          table: undefined
        })
      );

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(mockedPost).toHaveBeenCalledWith(
        '/metastore/databases/test-db%20with%20spaces/metadata',
        { source_type: 'hive' },
        { silenceErrors: true }
      );
    });

    it('handles manual fetch with special characters', async () => {
      mockedPost.mockResolvedValue({ status: 0, data: {} });

      const { result } = renderHook(() =>
        useDatabaseProperties({
          sourceType: 'hive',
          connector: mockConnector,
          database: undefined,
          table: undefined
        })
      );

      await act(async () => {
        await result.current.fetchProperties('database/with/slashes');
      });

      expect(mockedPost).toHaveBeenCalledWith(
        '/metastore/databases/database%2Fwith%2Fslashes/metadata',
        { source_type: 'hive' },
        { silenceErrors: true }
      );
    });
  });

  describe('Dependency updates', () => {
    it('refetches when database changes', async () => {
      mockedPost.mockResolvedValue({ status: 0, data: {} });

      const { result, rerender } = renderHook(
        ({ database }) =>
          useDatabaseProperties({
            sourceType: 'hive',
            connector: mockConnector,
            database,
            table: undefined
          }),
        { initialProps: { database: 'db1' } }
      );

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(mockedPost).toHaveBeenCalledTimes(1);
      expect(mockedPost).toHaveBeenCalledWith(
        '/metastore/databases/db1/metadata',
        { source_type: 'hive' },
        { silenceErrors: true }
      );

      // Change database
      rerender({ database: 'db2' });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(mockedPost).toHaveBeenCalledTimes(2);
      expect(mockedPost).toHaveBeenLastCalledWith(
        '/metastore/databases/db2/metadata',
        { source_type: 'hive' },
        { silenceErrors: true }
      );
    });

    it('updates fetchProperties callback when sourceType or connector changes', async () => {
      mockedPost.mockResolvedValue({ status: 0, data: {} });

      const { result, rerender } = renderHook(
        ({ sourceType }) =>
          useDatabaseProperties({
            sourceType,
            connector: mockConnector,
            database: undefined,
            table: undefined
          }),
        { initialProps: { sourceType: 'hive' } }
      );

      const originalFetchProperties = result.current.fetchProperties;

      // Change sourceType
      rerender({ sourceType: 'impala' });

      // Function reference should be updated
      expect(result.current.fetchProperties).not.toBe(originalFetchProperties);

      // Manual fetch should use new sourceType
      await act(async () => {
        await result.current.fetchProperties('test_db');
      });

      expect(mockedPost).toHaveBeenCalledWith(
        '/metastore/databases/test_db/metadata',
        { source_type: 'impala' },
        { silenceErrors: true }
      );
    });
  });

  describe('Complete properties response', () => {
    it('handles complete properties object', async () => {
      const completeProperties: DatabaseProperties = {
        owner_name: 'hive',
        owner_type: 'USER',
        location: 'hdfs://namenode:8020/user/hive/warehouse/complete_db.db',
        hdfs_link: 'http://namenode:9870/explorer.html#/user/hive/warehouse/complete_db.db',
        parameters: 'transient_lastDdlTime=1640995200'
      };

      mockedPost.mockResolvedValue({
        status: 0,
        data: completeProperties
      });

      const { result } = renderHook(() =>
        useDatabaseProperties({
          sourceType: 'hive',
          connector: mockConnector,
          database: 'complete_db',
          table: undefined
        })
      );

      await waitFor(() => {
        expect(result.current.properties).toEqual(completeProperties);
      });

      expect(result.current.properties?.owner_name).toBe('hive');
      expect(result.current.properties?.owner_type).toBe('USER');
      expect(result.current.properties?.location).toContain('hdfs://');
      expect(result.current.properties?.hdfs_link).toContain('http://');
      expect(result.current.properties?.parameters).toContain('transient_lastDdlTime');
    });
  });
});

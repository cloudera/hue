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

import { renderHook, act, waitFor } from '@testing-library/react';
import useLoadData from './useLoadData';
import { get } from '../../api/utils';

// Mock the `get` function
jest.mock('../../api/utils', () => ({
  get: jest.fn()
}));

const mockGet = get as jest.MockedFunction<typeof get>;
const mockUrlPrefix = 'https://api.example.com';
const mockEndpoint = '/endpoint';
const mockUrl = `${mockUrlPrefix}${mockEndpoint}`;
const mockData = { id: 1, product: 'Hue' };
const mockOptions = {
  params: { id: 1 }
};

describe('useLoadData', () => {
  beforeAll(() => {
    jest.clearAllMocks();
  });

  beforeEach(() => {
    mockGet.mockResolvedValue(mockData);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should fetch data successfully', async () => {
    const { result } = renderHook(() => useLoadData(mockUrl));
    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalledWith(mockUrl, undefined, expect.any(Object));
      expect(result.current.data).toEqual(mockData);
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
    });
  });

  it('should fetch data with params successfully', async () => {
    const { result } = renderHook(() => useLoadData(mockUrl, mockOptions));

    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalledWith(mockUrl, mockOptions.params, expect.any(Object));
      expect(result.current.data).toEqual(mockData);
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
    });
  });

  it('should handle fetch errors', async () => {
    const mockError = new Error('Fetch error');
    mockGet.mockRejectedValue(mockError);

    const { result } = renderHook(() => useLoadData(mockUrl));

    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalledWith(mockUrl, undefined, expect.any(Object));
      expect(result.current.data).toBeUndefined();
      expect(result.current.error).toEqual(mockError);
      expect(result.current.loading).toBe(false);
    });
  });

  it('should respect the skip option', () => {
    const { result } = renderHook(() => useLoadData(mockUrl, { skip: true }));

    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(false);
    expect(mockGet).not.toHaveBeenCalled();
  });

  it('should call refetch function', async () => {
    const { result } = renderHook(() => useLoadData(mockUrl));

    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalledWith(mockUrl, undefined, expect.any(Object));
      expect(result.current.data).toEqual(mockData);
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
    });

    mockGet.mockResolvedValueOnce({ ...mockData, product: 'Hue 2' });

    act(() => {
      result.current.reloadData();
    });

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalledTimes(2);
      expect(mockGet).toHaveBeenCalledWith(mockUrl, undefined, expect.any(Object));
      expect(result.current.data).toEqual({ ...mockData, product: 'Hue 2' });
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
    });
  });

  it('should handle URL prefix correctly', async () => {
    const { result } = renderHook(() => useLoadData(mockEndpoint, { urlPrefix: mockUrlPrefix }));

    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalledWith(mockUrl, undefined, expect.any(Object));
      expect(result.current.data).toEqual(mockData);
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
    });
  });

  it('should update options correctly', async () => {
    const { result, rerender } = renderHook(
      (props: { url: string; options }) => useLoadData(props.url, props.options),
      {
        initialProps: { url: mockUrl, options: mockOptions }
      }
    );

    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalledWith(mockUrl, mockOptions.params, expect.any(Object));
      expect(result.current.data).toEqual(mockData);
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
    });

    const newOptions = {
      params: { id: 2 }
    };
    const newMockData = { ...mockData, id: 2 };
    mockGet.mockResolvedValueOnce(newMockData);

    rerender({ url: mockUrl, options: newOptions });

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalledWith(mockUrl, newOptions.params, expect.any(Object));
      expect(result.current.data).toEqual(newMockData);
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
    });
  });

  it('should call onSuccess callback', async () => {
    const mockOnSuccess = jest.fn();
    const mockOnError = jest.fn();
    const { result } = renderHook(() =>
      useLoadData(mockUrl, {
        onSuccess: mockOnSuccess,
        onError: mockOnError
      })
    );

    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalledWith(mockUrl, undefined, expect.any(Object));
      expect(result.current.data).toEqual(mockData);
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
      expect(mockOnSuccess).toHaveBeenCalledWith(mockData);
      expect(mockOnError).not.toHaveBeenCalled();
    });
  });

  it('should call onError callback', async () => {
    const mockError = new Error('Fetch error');
    mockGet.mockRejectedValue(mockError);

    const mockOnSuccess = jest.fn();
    const mockOnError = jest.fn();
    const { result } = renderHook(() =>
      useLoadData(mockUrl, {
        onSuccess: mockOnSuccess,
        onError: mockOnError
      })
    );

    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalledWith(mockUrl, undefined, expect.any(Object));
      expect(result.current.data).toBeUndefined();
      expect(result.current.error).toEqual(mockError);
      expect(result.current.loading).toBe(false);
      expect(mockOnSuccess).not.toHaveBeenCalled();
      expect(mockOnError).toHaveBeenCalledWith(mockError);
    });
  });
});

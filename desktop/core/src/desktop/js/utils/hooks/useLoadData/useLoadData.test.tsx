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

import { act, renderHook, waitFor } from '@testing-library/react';
import useLoadData from './useLoadData';
import { get } from '../../../api/utils';
import { convertKeysToCamelCase } from '../../string/changeCasing';

jest.mock('../../../api/utils', () => ({
  get: jest.fn()
}));

const mockGet = get as jest.MockedFunction<typeof get>;
const mockUrlPrefix = 'https://api.example.com';
const mockEndpoint = '/endpoint';
const mockUrl = `${mockUrlPrefix}${mockEndpoint}`;
const mockData = { product_id: 1, product_name: 'Hue' };
const mockDataResponse = convertKeysToCamelCase(mockData);
const mockOptions = {
  params: { id: 1 }
};

const mockRequestOptions = {
  silenceErrors: true,
  ignoreSuccessErrors: true
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
      expect(mockGet).toHaveBeenCalledWith(mockUrl, undefined, mockRequestOptions);
      expect(result.current.data).toEqual(mockDataResponse);
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
      expect(mockGet).toHaveBeenCalledWith(mockUrl, mockOptions.params, mockRequestOptions);
      expect(result.current.data).toEqual(mockDataResponse);
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
      expect(mockGet).toHaveBeenCalledWith(mockUrl, undefined, mockRequestOptions);
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
      expect(mockGet).toHaveBeenCalledWith(mockUrl, undefined, mockRequestOptions);
      expect(result.current.data).toEqual(mockDataResponse);
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
    });

    const updatedMockResult = { ...mockDataResponse, product: 'Hue 2' };
    mockGet.mockResolvedValueOnce(updatedMockResult);

    await act(async () => {
      const reloadResult = await result.current.reloadData();
      expect(reloadResult).toEqual(updatedMockResult);
    });

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalledTimes(2);
      expect(mockGet).toHaveBeenCalledWith(mockUrl, undefined, mockRequestOptions);
      expect(result.current.data).toEqual(updatedMockResult);
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
      expect(mockGet).toHaveBeenCalledWith(mockUrl, mockOptions.params, mockRequestOptions);
      expect(result.current.data).toEqual(mockDataResponse);
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
    });

    const newOptions = {
      params: { id: 2 }
    };
    const newMockData = { ...mockDataResponse, productId: 2 };
    mockGet.mockResolvedValueOnce(newMockData);

    rerender({ url: mockUrl, options: newOptions });

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalledWith(mockUrl, newOptions.params, mockRequestOptions);
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
      expect(mockGet).toHaveBeenCalledWith(mockUrl, undefined, mockRequestOptions);
      expect(result.current.data).toEqual(mockDataResponse);
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
      expect(mockOnSuccess).toHaveBeenCalledWith(mockDataResponse);
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
      expect(mockGet).toHaveBeenCalledWith(mockUrl, undefined, mockRequestOptions);
      expect(result.current.data).toBeUndefined();
      expect(result.current.error).toEqual(mockError);
      expect(result.current.loading).toBe(false);
      expect(mockOnSuccess).not.toHaveBeenCalled();
      expect(mockOnError).toHaveBeenCalledWith(mockError);
    });
  });

  it('should force fetch data when reloadData is called even with skip option', async () => {
    const { result } = renderHook(() => useLoadData(mockUrl, { skip: true }));

    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(false);
    expect(mockGet).not.toHaveBeenCalled();

    await act(async () => {
      await result.current.reloadData();
    });

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalledWith(mockUrl, undefined, mockRequestOptions);
      expect(result.current.data).toEqual(mockDataResponse);
      expect(result.current.loading).toBe(false);
    });
  });

  it('should poll data at specified interval', async () => {
    jest.useFakeTimers();

    const pollInterval = 5000;
    const { result } = renderHook(() => useLoadData(mockUrl, { pollInterval }));

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalledTimes(1);
      expect(result.current.data).toEqual(mockDataResponse);
    });

    mockGet.mockClear();

    act(() => {
      jest.advanceTimersByTime(pollInterval);
    });

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalledTimes(1);
    });

    mockGet.mockClear();
    act(() => {
      jest.advanceTimersByTime(pollInterval);
    });

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalledTimes(1);
    });

    jest.useRealTimers();
  });

  it('should clear polling interval when component unmounts', async () => {
    jest.useFakeTimers();

    const clearIntervalSpy = jest.spyOn(global, 'clearInterval');

    const pollInterval = 5000; // 5 seconds
    const { result, unmount } = renderHook(() => useLoadData(mockUrl, { pollInterval }));

    await waitFor(() => {
      expect(result.current.data).toEqual(mockDataResponse);
    });

    unmount();

    expect(clearIntervalSpy).toHaveBeenCalled();

    clearIntervalSpy.mockRestore();
    jest.useRealTimers();
  });

  it('should clear previous interval when pollInterval changes', async () => {
    jest.useFakeTimers();

    const clearIntervalSpy = jest.spyOn(global, 'clearInterval');
    const setIntervalSpy = jest.spyOn(global, 'setInterval');

    const { result, rerender } = renderHook(
      (props: { pollInterval?: number }) =>
        useLoadData(mockUrl, { pollInterval: props.pollInterval }),
      { initialProps: { pollInterval: 5000 } }
    );

    await waitFor(() => {
      expect(result.current.data).toEqual(mockDataResponse);
    });

    expect(setIntervalSpy).toHaveBeenCalledWith(expect.any(Function), 5000);

    rerender({ pollInterval: 10000 });

    await waitFor(() => {
      expect(result.current.data).toEqual(mockDataResponse);
      expect(clearIntervalSpy).toHaveBeenCalled();
      expect(setIntervalSpy).toHaveBeenCalledWith(expect.any(Function), 10000);
    });

    clearIntervalSpy.mockRestore();
    setIntervalSpy.mockRestore();
    jest.useRealTimers();
  });

  describe('transformKeys option', () => {
    it('should fetch data and transform keys to camelCase when transformKeys is "camelCase"', async () => {
      const { result } = renderHook(() =>
        useLoadData(mockUrl, {
          transformKeys: 'camelCase'
        })
      );

      expect(result.current.data).toBeUndefined();
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(true);

      await waitFor(() => {
        expect(mockGet).toHaveBeenCalledWith(mockUrl, undefined, mockRequestOptions);
        expect(result.current.data).toEqual({ productId: 1, productName: 'Hue' });
        expect(result.current.error).toBeUndefined();
        expect(result.current.loading).toBe(false);
      });
    });

    it('should fetch data without transforming keys when transformKeys is "none"', async () => {
      const { result } = renderHook(() =>
        useLoadData(mockUrl, {
          transformKeys: 'none'
        })
      );

      expect(result.current.data).toBeUndefined();
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(true);

      await waitFor(() => {
        expect(mockGet).toHaveBeenCalledWith(mockUrl, undefined, mockRequestOptions);
        expect(result.current.data).toEqual(mockData);
        expect(result.current.error).toBeUndefined();
        expect(result.current.loading).toBe(false);
      });
    });

    it('should fetch data and transform keys to camelCase when transformKeys is undefined', async () => {
      const { result } = renderHook(() => useLoadData(mockUrl));

      expect(result.current.data).toBeUndefined();
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(true);

      await waitFor(() => {
        expect(mockGet).toHaveBeenCalledWith(mockUrl, undefined, mockRequestOptions);
        expect(result.current.data).toEqual({ productId: 1, productName: 'Hue' });
        expect(result.current.error).toBeUndefined();
        expect(result.current.loading).toBe(false);
      });
    });

    it('should handle camelCase transformation for nested objects', async () => {
      const mockData = {
        product_details: {
          product_id: 1,
          product_name: 'Hue'
        }
      };
      mockGet.mockResolvedValue(mockData);
      const { result } = renderHook(() =>
        useLoadData(mockUrl, {
          transformKeys: 'camelCase'
        })
      );

      expect(result.current.data).toBeUndefined();
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(true);

      await waitFor(() => {
        expect(mockGet).toHaveBeenCalledWith(mockUrl, undefined, mockRequestOptions);
        expect(result.current.data).toEqual({
          productDetails: {
            productId: 1,
            productName: 'Hue'
          }
        });
        expect(result.current.error).toBeUndefined();
        expect(result.current.loading).toBe(false);
      });
    });

    it('should not transform keys when transformKeys is "none" for nested objects', async () => {
      const mockData = {
        product_details: {
          product_id: 1,
          product_name: 'Hue'
        }
      };
      mockGet.mockResolvedValue(mockData);
      const { result } = renderHook(() =>
        useLoadData(mockUrl, {
          transformKeys: 'none'
        })
      );

      expect(result.current.data).toBeUndefined();
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(true);

      await waitFor(() => {
        expect(mockGet).toHaveBeenCalledWith(mockUrl, undefined, mockRequestOptions);
        expect(result.current.data).toEqual(mockData);
        expect(result.current.error).toBeUndefined();
        expect(result.current.loading).toBe(false);
      });
    });
  });
});

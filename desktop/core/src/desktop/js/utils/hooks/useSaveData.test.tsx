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
import useSaveData from './useSaveData';
import { post } from '../../api/utils';

jest.mock('../../api/utils', () => ({
  post: jest.fn()
}));

const mockPost = post as jest.MockedFunction<typeof post>;
const mockUrlPrefix = 'https://api.example.com';
const mockEndpoint = '/save-endpoint';
const mockUrl = `${mockUrlPrefix}${mockEndpoint}`;
const mockData = { id: 1, product: 'Hue' };
const mockBody = { id: 1 };

describe('useSaveData', () => {
  beforeAll(() => {
    jest.clearAllMocks();
  });

  beforeEach(() => {
    mockPost.mockResolvedValue(mockData);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should save data with body successfully', async () => {
    const { result } = renderHook(() => useSaveData(mockUrl));

    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(false);

    act(() => {
      result.current.save(mockBody);
    });
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(mockPost).toHaveBeenCalledTimes(1);
      expect(mockPost).toHaveBeenCalledWith(mockUrl, mockBody, expect.any(Object));
      expect(result.current.data).toEqual(mockData);
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
    });
  });

  it('should handle save errors', async () => {
    const mockError = new Error('Save error');
    mockPost.mockRejectedValue(mockError);

    const { result } = renderHook(() => useSaveData(mockUrl));

    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(false);

    act(() => {
      result.current.save(mockBody);
    });
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(mockPost).toHaveBeenCalledWith(mockUrl, mockBody, expect.any(Object));
      expect(result.current.data).toBeUndefined();
      expect(result.current.error).toEqual(mockError);
      expect(result.current.loading).toBe(false);
    });
  });

  it('should respect the skip option', () => {
    const { result } = renderHook(() => useSaveData(mockUrl, { skip: true }));

    act(() => {
      result.current.save(mockBody);
    });

    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(false);
    expect(mockPost).not.toHaveBeenCalled();
  });

  it('should update options correctly', async () => {
    const { result, rerender } = renderHook((props: { url: string }) => useSaveData(props.url), {
      initialProps: { url: mockUrl }
    });

    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(false);

    act(() => {
      result.current.save(mockBody);
    });
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(mockPost).toHaveBeenCalledWith(mockUrl, mockBody, expect.any(Object));
      expect(result.current.data).toEqual(mockData);
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
    });

    const newBody = { id: 2 };
    const newMockData = { ...mockData, id: 2 };
    mockPost.mockResolvedValueOnce(newMockData);

    rerender({ url: mockUrl });

    act(() => {
      result.current.save(newBody);
    });
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(mockPost).toHaveBeenCalledWith(mockUrl, newBody, expect.any(Object));
      expect(result.current.data).toEqual(newMockData);
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
    });
  });

  it('should call onSuccess callback', async () => {
    const mockOnSuccess = jest.fn();
    const mockOnError = jest.fn();
    const { result } = renderHook(() =>
      useSaveData(mockUrl, {
        onSuccess: mockOnSuccess,
        onError: mockOnError
      })
    );

    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(false);

    act(() => {
      result.current.save(mockBody);
    });
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(mockPost).toHaveBeenCalledWith(mockUrl, mockBody, expect.any(Object));
      expect(result.current.data).toEqual(mockData);
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
      expect(mockOnSuccess).toHaveBeenCalledWith(mockData);
      expect(mockOnError).not.toHaveBeenCalled();
    });
  });

  it('should call onError callback', async () => {
    const mockError = new Error('Save error');
    mockPost.mockRejectedValue(mockError);

    const mockOnSuccess = jest.fn();
    const mockOnError = jest.fn();
    const { result } = renderHook(() =>
      useSaveData(mockUrl, {
        onSuccess: mockOnSuccess,
        onError: mockOnError
      })
    );

    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(false);

    act(() => {
      result.current.save(mockBody);
    });
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(mockPost).toHaveBeenCalledWith(mockUrl, mockBody, expect.any(Object));
      expect(result.current.data).toBeUndefined();
      expect(result.current.error).toEqual(mockError);
      expect(result.current.loading).toBe(false);
      expect(mockOnSuccess).not.toHaveBeenCalled();
      expect(mockOnError).toHaveBeenCalledWith(mockError);
    });
  });
});

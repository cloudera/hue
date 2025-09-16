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
import { HttpMethod, sendApiRequest } from '../../../api/utils';

jest.mock('../../../api/utils', () => {
  const original = jest.requireActual('../../../api/utils');
  return {
    ...original,
    post: jest.fn(),
    put: jest.fn(),
    patch: jest.fn(),
    sendApiRequest: jest.fn()
  };
});

const mockSendApiRequest = sendApiRequest as jest.MockedFunction<typeof sendApiRequest>;
const mockUrlPrefix = 'https://api.example.com';
const mockEndpoint = '/save-endpoint';
const mockUrl = `${mockUrlPrefix}${mockEndpoint}`;
const mockData = { id: 1, product: 'Hue' };
const mockBody = { id: 1 };
const mockRequestOptions = {
  ignoreSuccessErrors: true,
  qsEncodeData: false,
  silenceErrors: true
};

describe('useSaveData', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockSendApiRequest.mockResolvedValue(mockData);
  });

  it('should save data successfully and update state', async () => {
    const { result } = renderHook(() => useSaveData(mockUrl));

    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(false);

    act(() => {
      result.current.save(mockBody);
    });

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(mockSendApiRequest).toHaveBeenCalledTimes(1);
      expect(mockSendApiRequest).toHaveBeenCalledWith(
        HttpMethod.POST,
        mockUrl,
        mockBody,
        mockRequestOptions
      );
      expect(result.current.data).toEqual(mockData);
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
    });
  });

  it('should handle errors and update error state', async () => {
    const mockError = new Error('Save error');
    mockSendApiRequest.mockRejectedValue(mockError);

    const { result } = renderHook(() => useSaveData(mockUrl));

    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(false);

    act(() => {
      result.current.save(mockBody);
    });

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(mockSendApiRequest).toHaveBeenCalledWith(
        HttpMethod.POST,
        mockUrl,
        mockBody,
        mockRequestOptions
      );
      expect(result.current.data).toBeUndefined();
      expect(result.current.error).toEqual(mockError);
      expect(result.current.loading).toBe(false);
    });
  });

  it('should not call post when skip option is true', () => {
    const { result } = renderHook(() => useSaveData(mockUrl, { skip: true }));

    act(() => {
      result.current.save(mockBody);
    });

    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(false);
    expect(mockSendApiRequest).not.toHaveBeenCalled();
  });

  it('should update options when props change', async () => {
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
      expect(mockSendApiRequest).toHaveBeenCalledWith(
        HttpMethod.POST,
        mockUrl,
        mockBody,
        mockRequestOptions
      );
      expect(result.current.data).toEqual(mockData);
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
    });

    const newBody = { id: 2 };
    const newMockData = { ...mockData, id: 2 };
    mockSendApiRequest.mockResolvedValueOnce(newMockData);

    rerender({ url: mockUrl });

    act(() => {
      result.current.save(newBody);
    });

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(mockSendApiRequest).toHaveBeenCalledWith(
        HttpMethod.POST,
        mockUrl,
        newBody,
        mockRequestOptions
      );
      expect(result.current.data).toEqual(newMockData);
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
    });
  });

  it('should call onSuccess callback when provided', async () => {
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
      expect(mockSendApiRequest).toHaveBeenCalledWith(
        HttpMethod.POST,
        mockUrl,
        mockBody,
        mockRequestOptions
      );
      expect(result.current.data).toEqual(mockData);
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
      expect(mockOnSuccess).toHaveBeenCalledWith(mockData);
      expect(mockOnError).not.toHaveBeenCalled();
    });
  });

  it('should call onError callback when provided', async () => {
    const mockError = new Error('Save error');
    mockSendApiRequest.mockRejectedValue(mockError);

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
      expect(mockSendApiRequest).toHaveBeenCalledWith(
        HttpMethod.POST,
        mockUrl,
        mockBody,
        mockRequestOptions
      );
      expect(result.current.data).toBeUndefined();
      expect(result.current.error).toEqual(mockError);
      expect(result.current.loading).toBe(false);
      expect(mockOnSuccess).not.toHaveBeenCalled();
      expect(mockOnError).toHaveBeenCalledWith(mockError);
    });
  });

  it('should auto set qsEncodeData to true for non-JSON and non-FormData payloads', async () => {
    const { result } = renderHook(() => useSaveData(mockUrl));

    act(() => {
      result.current.save('hue data');
    });

    await waitFor(() => {
      expect(mockSendApiRequest).toHaveBeenCalledWith(
        HttpMethod.POST,
        mockUrl,
        'hue data',
        expect.objectContaining({
          qsEncodeData: true,
          silenceErrors: true,
          ignoreSuccessErrors: true
        })
      );
      expect(result.current.data).toEqual(mockData);
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
    });
  });

  it('should not auto set qsEncodeData for FormData payloads', async () => {
    const payload = new FormData();

    const { result } = renderHook(() => useSaveData(mockUrl));

    act(() => {
      result.current.save(payload);
    });

    await waitFor(() => {
      expect(mockSendApiRequest).toHaveBeenCalledWith(HttpMethod.POST, mockUrl, payload, {
        ...mockRequestOptions,
        qsEncodeData: false
      });
      expect(result.current.data).toEqual(mockData);
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
    });
  });

  it('should not auto set qsEncodeData for JSON payloads', async () => {
    const payload = { project: 'hue' };

    const { result } = renderHook(() => useSaveData(mockUrl));

    act(() => {
      result.current.save(payload);
    });

    await waitFor(() => {
      expect(mockSendApiRequest).toHaveBeenCalledWith(HttpMethod.POST, mockUrl, payload, {
        ...mockRequestOptions,
        qsEncodeData: false
      });
      expect(result.current.data).toEqual(mockData);
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
    });
  });

  it('should prioritize qsEncodeData from saveOptions.options', async () => {
    const payload = new FormData();

    const { result } = renderHook(() =>
      useSaveData(mockUrl, {
        options: { qsEncodeData: true }
      })
    );

    act(() => {
      result.current.save(payload);
    });

    await waitFor(() => {
      expect(mockSendApiRequest).toHaveBeenCalledWith(HttpMethod.POST, mockUrl, payload, {
        ...mockRequestOptions,
        qsEncodeData: true
      });
      expect(result.current.data).toEqual(mockData);
      expect(result.current.error).toBeUndefined();
      expect(result.current.loading).toBe(false);
    });
  });

  it('should use PUT method when specified in options', async () => {
    mockSendApiRequest.mockResolvedValue(mockData);

    const { result } = renderHook(() => useSaveData(mockUrl, { method: HttpMethod.PUT }));

    act(() => {
      result.current.save(mockBody);
    });

    await waitFor(() => {
      expect(mockSendApiRequest).toHaveBeenCalledTimes(1);
      expect(mockSendApiRequest).toHaveBeenCalledWith(
        HttpMethod.PUT,
        mockUrl,
        mockBody,
        mockRequestOptions
      );
      expect(result.current.data).toEqual(mockData);
      expect(result.current.loading).toBe(false);
    });
  });

  it('should use PATCH method when specified in saveOptions', async () => {
    mockSendApiRequest.mockResolvedValue(mockData);

    const { result } = renderHook(() => useSaveData(mockUrl));

    act(() => {
      result.current.save(mockBody, { method: HttpMethod.PATCH });
    });

    await waitFor(() => {
      expect(mockSendApiRequest).toHaveBeenCalledTimes(1);
      expect(mockSendApiRequest).toHaveBeenCalledWith(
        HttpMethod.PATCH,
        mockUrl,
        mockBody,
        mockRequestOptions
      );
      expect(result.current.data).toEqual(mockData);
      expect(result.current.loading).toBe(false);
    });
  });

  it('should prioritize saveOptions method over options method', async () => {
    mockSendApiRequest.mockResolvedValue(mockData);

    const { result } = renderHook(() => useSaveData(mockUrl, { method: HttpMethod.PUT }));

    act(() => {
      result.current.save(mockBody, { method: HttpMethod.PATCH });
    });

    await waitFor(() => {
      expect(mockSendApiRequest).toHaveBeenCalledTimes(1);
      expect(mockSendApiRequest).toHaveBeenCalledWith(
        HttpMethod.PATCH,
        mockUrl,
        mockBody,
        mockRequestOptions
      );
      expect(result.current.data).toEqual(mockData);
      expect(result.current.loading).toBe(false);
    });
  });

  it('should default to POST when no method is specified', async () => {
    const { result } = renderHook(() => useSaveData(mockUrl));

    act(() => {
      result.current.save(mockBody);
    });

    await waitFor(() => {
      expect(mockSendApiRequest).toHaveBeenCalledTimes(1);
      expect(mockSendApiRequest).toHaveBeenCalledWith(
        HttpMethod.POST,
        mockUrl,
        mockBody,
        mockRequestOptions
      );
      expect(result.current.data).toEqual(mockData);
      expect(result.current.loading).toBe(false);
    });
  });

  it('should transform response keys to camelCase by default', async () => {
    const mockRawData = { product_id: 1, product_name: 'Hue' };
    const mockCamelCaseData = { productId: 1, productName: 'Hue' };
    mockSendApiRequest.mockResolvedValue(mockRawData);

    const { result } = renderHook(() => useSaveData(mockUrl));

    act(() => {
      result.current.save(mockBody);
    });

    await waitFor(() => {
      expect(result.current.data).toEqual(mockCamelCaseData);
    });
  });

  it('should transform response keys to camelCase when transformKeys is "camelCase"', async () => {
    const mockRawData = { product_id: 1, product_name: 'Hue' };
    const mockCamelCaseData = { productId: 1, productName: 'Hue' };
    mockSendApiRequest.mockResolvedValue(mockRawData);

    const { result } = renderHook(() => useSaveData(mockUrl, { transformKeys: 'camelCase' }));

    act(() => {
      result.current.save(mockBody);
    });

    await waitFor(() => {
      expect(result.current.data).toEqual(mockCamelCaseData);
    });
  });

  it('should not transform response keys when transformKeys is "none"', async () => {
    const mockRawData = { product_id: 1, product_name: 'Hue' };
    mockSendApiRequest.mockResolvedValue(mockRawData);

    const { result } = renderHook(() => useSaveData(mockUrl, { transformKeys: 'none' }));

    act(() => {
      result.current.save(mockBody);
    });

    await waitFor(() => {
      expect(result.current.data).toEqual(mockRawData);
    });
  });
});

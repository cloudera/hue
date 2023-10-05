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

import { successResponseIsError, generateCacheKey, fetchWithMemoryCache } from './apiUtils';

describe('apiUtils.js', () => {
  describe('success response that is actually an error', () => {
    it('should not determine that a success response is an error response if status is 0', () => {
      expect(successResponseIsError({ status: 0 })).toBeFalsy();
    });

    it('should determine that a success response is an error response if status is 1', () => {
      expect(successResponseIsError({ status: 1 })).toBeTruthy();
    });

    it('should determine that a success response is an error response if status is -1', () => {
      expect(successResponseIsError({ status: -1 })).toBeTruthy();
    });

    it('should determine that a success response is an error response if status is -3', () => {
      expect(successResponseIsError({ status: -3 })).toBeTruthy();
    });

    it('determine that a success response is an error response if status is 500', () => {
      expect(successResponseIsError({ status: 500 })).toBeTruthy();
    });

    it('should determine that a success response is an error response if code is 500', () => {
      expect(successResponseIsError({ code: 500 })).toBeTruthy();
    });

    it('should determine that a success response is an error response if code is 503', () => {
      expect(successResponseIsError({ code: 503 })).toBeTruthy();
    });

    it('should determine that a success response is an error response if it contains traceback', () => {
      expect(successResponseIsError({ traceback: {} })).toBeTruthy();
    });
  });

  describe('generateCacheKey', () => {
    it('should generate a cache key based on input data', () => {
      const data = { foo: 'bar', baz: 123 };
      const expectedKey = '111aa47a6d112b23cfaff7cdc9a523d1';
      const actualKey = generateCacheKey(data);
      expect(actualKey).toEqual(expectedKey);
    });
  });

  describe('fetchWithMemoryCache', () => {
    const stubFetch = jest.fn(() => Promise.resolve({ json: () => ({ result: 'success' }) }));

    beforeEach(() => {
      jest.clearAllMocks();
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should cache and retrieve data', async () => {
      const response = await fetchWithMemoryCache({ url: '/data' });
      expect(stubFetch).toHaveBeenCalledTimes(1);
      expect(response).toEqual({ result: 'success' });
      const cachedResponse = await fetchWithMemoryCache({ url: '/data' });
      expect(stubFetch).toHaveBeenCalledTimes(1);
      expect(cachedResponse).toEqual({ result: 'success' });
    });

    it('should use custom cache key if provided', async () => {
      const cacheKey = 'custom_key';
      await fetchWithMemoryCache({ url: '/data', cacheKey });
      expect(stubFetch).toHaveBeenCalledTimes(1);
      await fetchWithMemoryCache({ url: '/data', cacheKey });
      expect(stubFetch).toHaveBeenCalledTimes(1);
    });

    it('should delete expired cache entries', async () => {
      const keepFor = 1000; // 1 second
      await fetchWithMemoryCache({ url: '/data', keepFor });
      expect(stubFetch).toHaveBeenCalledTimes(1);
      await fetchWithMemoryCache({ url: '/data', keepFor });
      expect(stubFetch).toHaveBeenCalledTimes(1);
      jest.advanceTimersByTime(keepFor);
      await fetchWithMemoryCache({ url: '/data', keepFor });
      expect(stubFetch).toHaveBeenCalledTimes(2);
    });

    it('should limit the number of cache entries', async () => {
      const cacheSize = 50;
      for (let i = 0; i < cacheSize * 2; i++) {
        await fetchWithMemoryCache({ url: `/data/${i}` });
      }
      expect(stubFetch).toHaveBeenCalledTimes(cacheSize * 2);
    });

    it('should use POST method and JSON content type by default', async () => {
      const data = { foo: 'bar', baz: 123 };
      await fetchWithMemoryCache({ url: '/data', data });
      expect(stubFetch).toHaveBeenCalledTimes(1);
      expect(stubFetch.mock.calls[0][1].method).toEqual('POST');
      expect(stubFetch.mock.calls[0][1].headers['Content-Type']).toEqual('application/json');
      expect(stubFetch.mock.calls[0][1].body).toEqual(JSON.stringify(data));
    });
  });
});

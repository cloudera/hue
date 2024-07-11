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
import { renderHook, act } from '@testing-library/react';
import useDebounce, { SomeFunction } from './useDebounce';
import { DEBOUNCE_DELAY } from './constants/common';

const mockFunction: jest.Mock<SomeFunction> = jest.fn();
jest.useFakeTimers();

afterEach(() => {
  jest.clearAllTimers();
  mockFunction.mockReset();
});

describe('useDebounce', () => {
  it('should return a debounced function', () => {
    const { result } = renderHook(() => useDebounce(mockFunction));
    expect(typeof result.current).toBe('function');
  });

  it('should not call the function immediately when called with arguments', () => {
    const { result } = renderHook(() => useDebounce(mockFunction));
    act(() => {
      result.current('test');
    });
    expect(mockFunction).not.toHaveBeenCalled();
  });

  it('should call the function with the latest arguments after the delay', async () => {
    const { result } = renderHook(() => useDebounce(mockFunction));
    act(() => {
      result.current('test1');
      result.current('test2'); // Simulate multiple calls before delay
    });
    jest.advanceTimersByTime(DEBOUNCE_DELAY);
    expect(mockFunction).toHaveBeenCalledTimes(1);
    expect(mockFunction).toHaveBeenCalledWith('test2'); // Only the latest arguments should be passed
  });

  it('should cancel the previous timeout if called again before delay', () => {
    const { result } = renderHook(() => useDebounce(mockFunction));
    act(() => {
      result.current('test1');
      result.current('test2');
    });
    jest.advanceTimersByTime(DEBOUNCE_DELAY / 2); // Advance half the delay to simulate a race condition
    result.current('test3');

    jest.runAllTimers();

    expect(mockFunction).toHaveBeenCalledTimes(1);
    expect(mockFunction).toHaveBeenCalledWith('test3'); // Only the latest arguments after the race condition should be passed
  });

  it('should cleanup the timer on unmount', () => {
    const { result, unmount } = renderHook(() => useDebounce(mockFunction));
    act(() => {
      result.current('test');
    });
    unmount();
    jest.advanceTimersByTime(DEBOUNCE_DELAY);
    expect(mockFunction).not.toHaveBeenCalled();
  });

  it('should not call the function with empty arguments', () => {
    const { result } = renderHook(() => useDebounce(mockFunction));
    act(() => {
      result.current(); // Call with empty arguments
    });
    expect(mockFunction).not.toHaveBeenCalled();
  });

  it('should handle very short delays (0ms)', () => {
    const { result } = renderHook(() => useDebounce(mockFunction, 0));
    act(() => {
      result.current('test');
    });
    jest.runAllTimers();
    expect(mockFunction).toHaveBeenCalledTimes(1);
    expect(mockFunction).toHaveBeenCalledWith('test');
  });
});

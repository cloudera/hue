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
import { useWindowSize } from './useWindowSize';

describe('useWindowSize', () => {
  const mockGetBoundingClientRect = jest.fn();

  beforeAll(() => {
    global.HTMLElement.prototype.getBoundingClientRect = mockGetBoundingClientRect;
  });

  beforeEach(() => {
    mockGetBoundingClientRect.mockClear();
  });

  it('should handle missing ref gracefully', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      value: 800
    });
    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      value: 600
    });

    const { result } = renderHook(() => useWindowSize());

    expect(result.current.size).toEqual({ width: 800, height: 600 });
    expect(result.current.offset).toEqual({ top: 0, left: 0 });
  });

  it('should initialize size and offset correctly', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      value: 800
    });
    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      value: 600
    });

    mockGetBoundingClientRect.mockReturnValue({
      top: 50,
      left: 100,
      width: 200,
      height: 100,
      right: 300,
      bottom: 150
    });

    const mockRef = {
      current: document.createElement('div')
    };

    const { result } = renderHook(() => useWindowSize(mockRef));

    expect(result.current.size).toEqual({ width: 800, height: 600 });
    expect(result.current.offset).toEqual({ top: 50, left: 100 });
  });

  it('should update size and offset on window resize', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      value: 800
    });
    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      value: 600
    });
    mockGetBoundingClientRect.mockReturnValue({
      top: 50,
      left: 100,
      width: 200,
      height: 100,
      right: 300,
      bottom: 150
    });

    const mockRef = {
      current: document.createElement('div')
    };

    const { result } = renderHook(() => useWindowSize(mockRef));

    expect(result.current.size).toEqual({ width: 800, height: 600 });
    expect(result.current.offset).toEqual({ top: 50, left: 100 });

    mockGetBoundingClientRect.mockReturnValue({
      top: 60,
      left: 120,
      width: 200,
      height: 100,
      right: 320,
      bottom: 160
    });

    act(() => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        value: 1024
      });
      Object.defineProperty(window, 'innerHeight', {
        writable: true,
        value: 768
      });
      window.dispatchEvent(new Event('resize'));
    });

    expect(result.current.size).toEqual({ width: 1024, height: 768 });
    expect(result.current.offset).toEqual({ top: 60, left: 120 });
  });
});

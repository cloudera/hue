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

import { act, renderHook } from '@testing-library/react';
import useResizeObserver from './useResizeObserver';

describe('useResizeObserver', () => {
  const mockCallback = jest.fn();
  const mockObserver = {
    observe: jest.fn(),
    disconnect: jest.fn()
  };

  beforeAll(() => {
    global.ResizeObserver = jest.fn().mockImplementation(callback => {
      mockCallback.mockImplementation(callback);
      return mockObserver;
    });
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should initialize with default dimensions', () => {
    const { result } = renderHook(() => useResizeObserver());

    expect(result.current[1]).toEqual({
      x: 0,
      y: 0,
      width: 0,
      height: 0,
      top: 0,
      right: 0,
      bottom: 0,
      left: 0
    });
  });

  it('should update dimensions when ResizeObserver fires', () => {
    const { result } = renderHook(() => useResizeObserver());
    const div = document.createElement('div');
    result.current[0].current = div;

    const newDimensions = {
      x: 10,
      y: 20,
      width: 100,
      height: 200,
      top: 20,
      right: 110,
      bottom: 220,
      left: 10
    };

    act(() => {
      mockCallback([{ target: div, contentRect: newDimensions }]);
    });

    expect(result.current[1]).toEqual(newDimensions);
  });

  it('should disconnect observer on unmount', () => {
    const { unmount } = renderHook(() => useResizeObserver());

    unmount();
    expect(mockObserver.disconnect).toHaveBeenCalled();
  });
});

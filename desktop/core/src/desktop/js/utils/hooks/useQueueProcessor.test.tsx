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
import useQueueProcessor from './useQueueProcessor';

describe('useQueueProcessor', () => {
  const mockProcessItem = jest.fn(() => new Promise<void>(resolve => setTimeout(resolve, 100)));

  it('should process items concurrently with a maximum of 1 item', async () => {
    const { result } = renderHook(() => useQueueProcessor(mockProcessItem));

    expect(result.current.pendingQueue).toEqual([]);
    expect(result.current.processingQueue).toEqual([]);
    expect(result.current.completedQueue).toEqual([]);

    act(() => {
      result.current.enqueue(['item1', 'item2', 'item3']);
    });

    expect(result.current.processingQueue).toEqual(['item1']);
    expect(result.current.pendingQueue).toEqual(['item2', 'item3']);
    expect(result.current.completedQueue).toEqual([]);

    await waitFor(() => expect(result.current.completedQueue).toEqual(['item1']));

    expect(result.current.processingQueue).toEqual(['item2']);
    expect(result.current.pendingQueue).toEqual(['item3']);
    expect(result.current.completedQueue).toEqual(['item1']);
  });

  it('should handle processing multiple items concurrently', async () => {
    const CONCURRENT_PROCESS = 2;
    const { result } = renderHook(() => useQueueProcessor(mockProcessItem, CONCURRENT_PROCESS));

    act(() => {
      result.current.enqueue(['item1', 'item2', 'item3', 'item4']);
    });

    expect(result.current.pendingQueue).toEqual(['item3', 'item4']);
    expect(result.current.processingQueue.length).toEqual(CONCURRENT_PROCESS);
    expect(result.current.processingQueue).toEqual(['item1', 'item2']);
    expect(result.current.completedQueue).toEqual([]);

    await waitFor(() => expect(result.current.completedQueue).toEqual(['item1', 'item2']));

    expect(result.current.pendingQueue).toEqual([]);
    expect(result.current.processingQueue.length).toEqual(CONCURRENT_PROCESS);
    expect(result.current.processingQueue).toEqual(['item3', 'item4']);
    expect(result.current.completedQueue).toEqual(['item1', 'item2']);
  });

  it('should remove items from pending queue when dequeued', async () => {
    const { result } = renderHook(() => useQueueProcessor(mockProcessItem));

    act(() => {
      result.current.enqueue(['item1', 'item2', 'item3']);
    });

    expect(result.current.processingQueue).toEqual(['item1']);
    expect(result.current.pendingQueue).toEqual(['item2', 'item3']);

    act(() => {
      result.current.dequeue('item3');
    });

    expect(result.current.pendingQueue).toEqual(['item2']);
    expect(result.current.processingQueue).toEqual(['item1']);
  });

  it('should remove items from pending queue when dequeued', async () => {
    const { result } = renderHook(() => useQueueProcessor(mockProcessItem));

    act(() => {
      result.current.enqueue(['item1', 'item2', 'item3']);
    });

    expect(result.current.processingQueue).toEqual(['item1']);
    expect(result.current.pendingQueue).toEqual(['item2', 'item3']);

    act(() => {
      result.current.dequeue('item3');
    });

    expect(result.current.pendingQueue).toEqual(['item2']);
    expect(result.current.processingQueue).toEqual(['item1']);
    expect(result.current.completedQueue).toEqual([]);
  });

  it('should update isProcessing when items are being processed', async () => {
    const { result } = renderHook(() => useQueueProcessor(mockProcessItem, 1));

    expect(result.current.isProcessing).toBe(false);

    act(() => {
      result.current.enqueue(['item1', 'item2']);
    });

    await waitFor(() => {
      expect(result.current.isProcessing).toBe(true);
    });

    await waitFor(() => {
      expect(result.current.completedQueue).toEqual(['item1']);
    });

    expect(result.current.isProcessing).toBe(true);

    await waitFor(() => {
      expect(result.current.completedQueue).toEqual(['item1', 'item2']);
    });

    expect(result.current.isProcessing).toBe(false);
  });
});

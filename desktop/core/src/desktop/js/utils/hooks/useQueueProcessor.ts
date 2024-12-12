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

import { useState, useEffect } from 'react';

interface UseQueueProcessorResult<T> {
  queue: T[];
  enqueue: (newItems: T[]) => void;
  enqueueAsync: (newItems: T[]) => Promise<void>;
  dequeue: (item: T) => void;
  isLoading: boolean;
}

interface UseQueueProcessorOptions {
  concurrentProcess: number;
  onSuccess?: () => void;
}

const useQueueProcessor = <T>(
  onItemProcess: (item: T) => Promise<void>,
  options: UseQueueProcessorOptions
): UseQueueProcessorResult<T> => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [queue, setQueue] = useState<T[]>([]);
  const [processingQueue, setProcessingQueue] = useState<T[]>([]);

  const enqueue = (newItems: T[]) => {
    setQueue(prevQueue => [...prevQueue, ...newItems]);
  };

  const enqueueAsync = (newItems: T[]) => {
    enqueue(newItems);
    return new Promise<void>(resolve => {
      const interval = setInterval(() => {
        if (queue.length === 0 && processingQueue.length === 0) {
          clearInterval(interval);
          resolve();
        }
      }, 100);
    });
  };

  const dequeue = (item: T) => {
    setQueue(prev => prev.filter(i => i !== item));
  };

  const processQueueItem = async (item: T) => {
    if (!isLoading) {
      setIsLoading(true);
    }

    setProcessingQueue(prev => [...prev, item]);
    await onItemProcess(item);
    setProcessingQueue(prev => prev.filter(i => i !== item));
  };

  useEffect(() => {
    if (processingQueue.length < options.concurrentProcess && queue.length) {
      const item = queue[0];
      setQueue(prev => prev.slice(1));
      processQueueItem(item);
    }

    // if all items are processed then call the onSuccess callback
    if (isLoading && processingQueue.length === 0 && queue.length === 0) {
      setIsLoading(false);
      options.onSuccess && options.onSuccess();
    }
  }, [queue, processingQueue, options.concurrentProcess, options.onSuccess, isLoading]);

  return {
    queue,
    isLoading,
    enqueue,
    enqueueAsync,
    dequeue
  };
};

export default useQueueProcessor;

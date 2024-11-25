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

type QueueProcessorState<T> = {
  pendingQueue: T[];
  processingQueue: T[];
  completedQueue: T[];
};

type UseQueueProcessorResult<T> = QueueProcessorState<T> & {
  enqueue: (newItems: T[]) => void;
  dequeue: (item: T) => void;
  isProcessing: boolean;
};

const useQueueProcessor = <T>(
  onItemProcess: (item: T) => Promise<void>,
  concurrentProcess: number = 1
): UseQueueProcessorResult<T> => {
  const [pendingQueue, setPendingQueue] = useState<QueueProcessorState<T>['pendingQueue']>([]);
  const [processingQueue, setProcessingQueue] = useState<QueueProcessorState<T>['processingQueue']>(
    []
  );
  const [completedQueue, setCompletedQueue] = useState<QueueProcessorState<T>['completedQueue']>(
    []
  );

  const processQueueItem = async () => {
    const nextItem = pendingQueue.shift();

    if (nextItem) {
      setProcessingQueue(prev => [...prev, nextItem]);
      await onItemProcess(nextItem);
      setProcessingQueue(prev => prev.filter(i => i !== nextItem));
      setCompletedQueue(prev => [...prev, nextItem]);
      processQueueItem();
    }
  };

  const enqueue = (newItems: T[]) => {
    setPendingQueue(prevQueue => [...prevQueue, ...newItems]);
  };

  const dequeue = (item: T) => {
    setPendingQueue(prev => prev.filter(i => i !== item));
  };

  useEffect(() => {
    let i = processingQueue.length;
    while (i < Math.min(concurrentProcess, pendingQueue.length)) {
      processQueueItem();
      i++;
    }
  }, [pendingQueue, processingQueue]);

  return {
    pendingQueue,
    completedQueue,
    processingQueue,
    isProcessing: !!processingQueue.length,
    enqueue,
    dequeue
  };
};

export default useQueueProcessor;

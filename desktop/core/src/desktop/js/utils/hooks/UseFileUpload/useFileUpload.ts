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

import { useEffect, useState } from 'react';
import useRegularUpload from './useRegularUpload';
import useChunkUpload from './useChunkUpload';
import { getNewFileItems, UploadItem } from './util';
import { FileUploadStatus } from '../../constants/storageBrowser';

interface UseUploadQueueResponse {
  uploadQueue: UploadItem[];
  onCancel: (item: UploadItem) => void;
  isLoading: boolean;
}

interface UploadQueueOptions {
  onComplete: () => UploadItem[] | void;
}

const isChunkUploadEnable = true;

const useFileUpload = (
  filesQueue: UploadItem[],
  { onComplete }: UploadQueueOptions
): UseUploadQueueResponse => {
  const [uploadQueue, setUploadQueue] = useState<UploadItem[]>([]);

  const onStatusUpdate = (item: UploadItem, newStatus: FileUploadStatus) =>
    setUploadQueue(prev =>
      prev.map(queueItem =>
        queueItem.uuid === item.uuid ? { ...queueItem, status: newStatus } : queueItem
      )
    );

  const findQueueItem = (item: UploadItem) =>
    uploadQueue.filter(queueItem => queueItem.uuid === item.uuid)?.[0];

  const {
    addFiles: addToChunkUpload,
    removeFile: removeFromChunkUpload,
    isLoading: isChunkLoading
  } = useChunkUpload({
    onStatusUpdate,
    onComplete
  });

  const {
    addFiles: addToRegularUpload,
    removeFile: removeFromRegularUpload,
    isLoading: isNonChunkLoading
  } = useRegularUpload({
    onStatusUpdate,
    onComplete
  });

  const onCancel = (item: UploadItem) => {
    const queueItem = findQueueItem(item);
    if (queueItem.status === FileUploadStatus.Pending) {
      onStatusUpdate(item, FileUploadStatus.Canceled);

      if (isChunkUploadEnable) {
        removeFromChunkUpload(item);
      } else {
        removeFromRegularUpload(item);
      }
    }
  };

  useEffect(() => {
    const newQueueItems = getNewFileItems(filesQueue, uploadQueue);

    if (newQueueItems.length > 0) {
      setUploadQueue(prev => [...prev, ...newQueueItems]);

      if (isChunkUploadEnable) {
        addToChunkUpload(newQueueItems);
      } else {
        addToRegularUpload(newQueueItems);
      }
    }
  }, [filesQueue, uploadQueue]);

  return { uploadQueue, onCancel, isLoading: isChunkLoading || isNonChunkLoading };
};

export default useFileUpload;

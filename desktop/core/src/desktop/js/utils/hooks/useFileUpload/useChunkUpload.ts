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
import { getLastKnownConfig } from '../../../config/hueConfig';
import useSaveData from '../useSaveData';
import useQueueProcessor from '../useQueueProcessor';
import {
  DEFAULT_CHUNK_SIZE,
  DEFAULT_CONCURRENT_MAX_CONNECTIONS,
  FileUploadStatus
} from '../../constants/storageBrowser';
import useLoadData from '../useLoadData';
import { TaskServerResponse, TaskStatus } from '../../../reactComponents/TaskBrowser/TaskBrowser';
import {
  createChunks,
  getChunksCompletePayload,
  getChunkItemPayload,
  getChunkSinglePayload,
  getStatusHashMap,
  getTotalChunk,
  UploadChunkItem,
  UploadItem
} from './util';

interface UseUploadQueueResponse {
  addFiles: (item: UploadItem[]) => void;
  removeFile: (item: UploadItem) => void;
  isLoading: boolean;
}

interface ChunkUploadOptions {
  concurrentProcess?: number;
  onStatusUpdate: (item: UploadItem, newStatus: FileUploadStatus) => void;
  onComplete: () => void;
}

const useChunkUpload = ({
  concurrentProcess = DEFAULT_CONCURRENT_MAX_CONNECTIONS,
  onStatusUpdate,
  onComplete
}: ChunkUploadOptions): UseUploadQueueResponse => {
  const config = getLastKnownConfig();
  const chunkSize = config?.storage_browser?.file_upload_chunk_size ?? DEFAULT_CHUNK_SIZE;
  const [pendingItems, setPendingItems] = useState<UploadItem[]>([]);

  const { save } = useSaveData(undefined, {
    postOptions: {
      qsEncodeData: false,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }
  });

  const updateItemStatus = (serverResponse: TaskServerResponse[]) => {
    const statusMap = getStatusHashMap(serverResponse);

    const remainingItems = pendingItems.filter(item => {
      const status = statusMap[item.uuid];
      if (status === TaskStatus.Success || status === TaskStatus.Failure) {
        const ItemStatus =
          status === TaskStatus.Success ? FileUploadStatus.Uploaded : FileUploadStatus.Failed;
        onStatusUpdate(item, ItemStatus);
        return false;
      }
      return true;
    });
    if (remainingItems.length === 0) {
      onComplete();
    }
    setPendingItems(remainingItems);
  };

  const { data: tasksStatus } = useLoadData<TaskServerResponse[]>(
    '/desktop/api2/taskserver/get_taskserver_tasks/',
    {
      pollInterval: pendingItems.length ? 5000 : undefined,
      skip: !pendingItems.length
    }
  );

  useEffect(() => {
    if (tasksStatus) {
      updateItemStatus(tasksStatus);
    }
  }, [tasksStatus]);

  const addItemToPending = (item: UploadItem) => {
    setPendingItems(prev => [...prev, item]);
  };

  const onChunksUploadComplete = async (item: UploadItem) => {
    const { url, payload } = getChunksCompletePayload(item, chunkSize);
    return save(payload, {
      url,
      onSuccess: () => addItemToPending(item)
    });
  };

  const uploadChunk = async (chunkItem: UploadChunkItem) => {
    const { url, payload } = getChunkItemPayload(chunkItem, chunkSize);
    return save(payload, { url });
  };

  const { enqueueAsync } = useQueueProcessor<UploadChunkItem>(uploadChunk, {
    concurrentProcess
  });

  const uploadItemInChunks = async (item: UploadItem) => {
    const chunks = createChunks(item, chunkSize);
    await enqueueAsync(chunks);
    return onChunksUploadComplete(item);
  };

  const uploadItemInSingleChunk = (item: UploadItem) => {
    const { url, payload } = getChunkSinglePayload(item, chunkSize);
    return save(payload, {
      url,
      onSuccess: () => addItemToPending(item)
    });
  };

  const uploadItem = async (item: UploadItem) => {
    onStatusUpdate(item, FileUploadStatus.Uploading);
    const chunks = getTotalChunk(item.file.size, chunkSize);
    if (chunks === 1) {
      return uploadItemInSingleChunk(item);
    }
    return uploadItemInChunks(item);
  };

  const {
    enqueue: addFiles,
    dequeue: removeFile,
    isLoading
  } = useQueueProcessor<UploadItem>(uploadItem, {
    concurrentProcess: 1 // This value must be 1 always
  });

  return { addFiles, removeFile, isLoading };
};

export default useChunkUpload;

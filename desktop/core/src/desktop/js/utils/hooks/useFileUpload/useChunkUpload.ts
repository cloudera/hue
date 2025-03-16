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

import { useState } from 'react';
import { getLastKnownConfig } from '../../../config/hueConfig';
import useSaveData from '../useSaveData/useSaveData';
import useQueueProcessor from '../useQueueProcessor/useQueueProcessor';
import {
  DEFAULT_CHUNK_SIZE,
  DEFAULT_CONCURRENT_MAX_CONNECTIONS,
  FileUploadStatus
} from '../../constants/storageBrowser';
import useLoadData from '../useLoadData/useLoadData';
import { TaskServerResponse, TaskStatus } from '../../../reactComponents/TaskBrowser/TaskBrowser';
import {
  type UploadChunkItem,
  type UploadItem,
  type UploadItemVariables,
  type InProgresChunk,
  getChunksCompletePayload,
  getItemProgress,
  getItemsTotalProgress,
  getChunkItemPayload,
  getChunkSinglePayload,
  isSpaceAvailableInServer,
  createChunks,
  getStatusHashMap
} from './util';

interface UseUploadQueueResponse {
  addFiles: (item: UploadItem[]) => void;
  removeFile: (item: UploadItem['uuid']) => void;
  isLoading: boolean;
}

interface ChunkUploadOptions {
  concurrentProcess?: number;
  onItemUpdate: (itemId: UploadItem['uuid'], variables: UploadItemVariables) => void;
  onComplete: () => void;
}

const useChunkUpload = ({
  concurrentProcess = DEFAULT_CONCURRENT_MAX_CONNECTIONS,
  onItemUpdate,
  onComplete
}: ChunkUploadOptions): UseUploadQueueResponse => {
  const config = getLastKnownConfig();
  const chunkSize = config?.storage_browser?.file_upload_chunk_size ?? DEFAULT_CHUNK_SIZE;
  const [taskServerItems, setTaskServerItems] = useState<Record<UploadItem['uuid'], number>>({});
  const [chunksInProgress, setChunksInProgress] = useState<Record<string, InProgresChunk[]>>({});

  const { save } = useSaveData(undefined, {
    postOptions: {
      qsEncodeData: false,
      headers: { 'Content-Type': 'multipart/form-data' }
    }
  });

  const onError = (chunkItem: UploadChunkItem) => (error: Error) => {
    onItemUpdate(chunkItem.uuid, { status: FileUploadStatus.Failed, error });
  };

  const processChunkUploadStatus = (tasksStatus?: TaskServerResponse[]) => {
    if (tasksStatus?.length) {
      const statusMap = getStatusHashMap(tasksStatus);
      setTaskServerItems(prev => {
        Object.keys(prev).forEach(uuid => {
          const status = statusMap[uuid];
          if (status === TaskStatus.Success || status === TaskStatus.Failure) {
            const ItemStatus =
              status === TaskStatus.Success ? FileUploadStatus.Uploaded : FileUploadStatus.Failed;
            onItemUpdate(uuid, { status: ItemStatus });
            delete prev[uuid];
          }
        });
        if (Object.keys(prev).length === 0) {
          onComplete();
        }
        return prev;
      });
    }
  };

  useLoadData<TaskServerResponse[]>('/desktop/api2/taskserver/get_taskserver_tasks/', {
    pollInterval: 5000,
    skip: !Object.keys(taskServerItems).length,
    onSuccess: processChunkUploadStatus,
    transformKeys: 'none'
  });

  const onChunksUploadComplete = async (chunkItem: UploadChunkItem) => {
    const { url, payload } = getChunksCompletePayload(chunkItem);
    return save(payload, {
      url,
      onSuccess: () => {
        setTaskServerItems(prev => ({ ...prev, [chunkItem.uuid]: 1 }));
      },
      onError: onError(chunkItem)
    });
  };

  const onChunkUploadSuccess = (chunkItem: UploadChunkItem) => () => {
    setChunksInProgress(prev => {
      const chunks = prev[chunkItem.uuid] || [];
      const allChunksUploaded = chunks.every(chunk => chunk.progress === 100);
      if (allChunksUploaded && chunks.length === chunkItem.totalChunks) {
        if (chunkItem.totalChunks > 1) {
          onChunksUploadComplete(chunkItem);
        }

        delete prev[chunkItem.uuid];
      }

      return prev;
    });
  };

  const onUploadProgress = (chunkItem: UploadChunkItem) => (progress: ProgressEvent) => {
    setChunksInProgress(prev => {
      const chunks = prev[chunkItem.uuid] || [];
      const chunk = chunks.find(c => c.chunkIndex === chunkItem.chunkIndex);
      if (!chunk) {
        return prev;
      }
      chunk.progress = getItemProgress(progress);

      const totalProgress = getItemsTotalProgress(chunkItem, chunks);
      onItemUpdate(chunkItem.uuid, { progress: totalProgress });
      return { ...prev, [chunkItem.uuid]: chunks };
    });
  };

  const uploadChunkItem = async (chunkItem: UploadChunkItem) => {
    const { url, payload } = getChunkItemPayload(chunkItem);
    return save(payload, {
      url,
      onSuccess: onChunkUploadSuccess(chunkItem),
      onError: onError(chunkItem),
      postOptions: { onUploadProgress: onUploadProgress(chunkItem) }
    });
  };

  const uploadChunkInSingle = async (chunkItem: UploadChunkItem) => {
    const { url, payload } = getChunkSinglePayload(chunkItem);
    return save(payload, {
      url,
      onSuccess: () => setTaskServerItems(prev => ({ ...prev, [chunkItem.uuid]: 1 })),
      onError: onError(chunkItem),
      postOptions: { onUploadProgress: onUploadProgress(chunkItem) }
    });
  };

  const uploadChunk = async (chunkItem: UploadChunkItem): Promise<void> => {
    setChunksInProgress(prev => ({
      ...prev,
      [chunkItem.uuid]: [
        ...(prev[chunkItem.uuid] ?? []),
        {
          chunkIndex: chunkItem.chunkIndex,
          progress: 0,
          chunkSize: chunkItem.file.size
        }
      ]
    }));

    const isFirstChunk = !chunksInProgress[chunkItem.uuid];

    if (isFirstChunk) {
      onItemUpdate(chunkItem.uuid, { status: FileUploadStatus.Uploading });
      const availableSpace = await isSpaceAvailableInServer(chunkItem.file.size);
      if (!availableSpace) {
        const error = new Error('Upload server ran out of space. Try again later.');
        onError(chunkItem)(error);
        return Promise.resolve();
      }
    }

    if (chunkItem.totalChunks === 1) {
      return uploadChunkInSingle(chunkItem);
    }
    return uploadChunkItem(chunkItem);
  };

  const { enqueue, dequeue } = useQueueProcessor<UploadChunkItem>(uploadChunk, {
    concurrentProcess
  });

  const addFiles = (newItems: UploadItem[]) => {
    newItems.forEach(item => {
      const chunks = createChunks(item, chunkSize);
      enqueue(chunks);
    });
  };

  const removeFile = (itemId: UploadItem['uuid']) => {
    dequeue(itemId, 'uuid');
  };

  return { addFiles, removeFile, isLoading: !!taskServerItems.length };
};

export default useChunkUpload;

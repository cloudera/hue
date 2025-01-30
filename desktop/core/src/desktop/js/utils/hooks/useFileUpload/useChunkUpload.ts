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
  createChunks,
  getChunksCompletePayload,
  getChunkItemPayload,
  getChunkSinglePayload,
  getStatusHashMap,
  getTotalChunk,
  UploadChunkItem,
  UploadItem
} from './util';
import { get } from '../../../api/utils';
import { UPLOAD_AVAILABLE_SPACE_URL } from '../../../reactComponents/FileChooser/api';

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
  const [processingItem, setProcessingItem] = useState<UploadItem>();
  const [pendingUploadItems, setPendingUploadItems] = useState<UploadItem[]>([]);
  const [awaitingStatusItems, setAwaitingStatusItems] = useState<UploadItem[]>([]);

  const onError = () => {
    if (processingItem) {
      onStatusUpdate(processingItem, FileUploadStatus.Failed);
      setProcessingItem(undefined);
    }
  };

  const onSuccess = (item: UploadItem) => () => {
    setAwaitingStatusItems(prev => [...prev, item]);
    setProcessingItem(undefined);
  };

  const { save } = useSaveData(undefined, {
    postOptions: {
      qsEncodeData: false,
      headers: { 'Content-Type': 'multipart/form-data' }
    },
    onError
  });

  const updateItemStatus = (serverResponse: TaskServerResponse[]) => {
    const statusMap = getStatusHashMap(serverResponse);

    const remainingItems = awaitingStatusItems.filter(item => {
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
    setAwaitingStatusItems(remainingItems);
  };

  const { data: tasksStatus } = useLoadData<TaskServerResponse[]>(
    '/desktop/api2/taskserver/get_taskserver_tasks/',
    {
      pollInterval: awaitingStatusItems.length ? 5000 : undefined,
      skip: !awaitingStatusItems.length
    }
  );

  useEffect(() => {
    if (tasksStatus) {
      updateItemStatus(tasksStatus);
    }
  }, [tasksStatus]);

  const onChunksUploadComplete = async () => {
    if (processingItem) {
      const { url, payload } = getChunksCompletePayload(processingItem, chunkSize);
      return save(payload, {
        url,
        onSuccess: onSuccess(processingItem)
      });
    }
  };

  const uploadChunk = async (chunkItem: UploadChunkItem) => {
    const { url, payload } = getChunkItemPayload(chunkItem, chunkSize);
    return save(payload, { url });
  };

  const { enqueue } = useQueueProcessor<UploadChunkItem>(uploadChunk, {
    concurrentProcess,
    onSuccess: onChunksUploadComplete
  });

  const uploadItemInChunks = (item: UploadItem) => {
    const chunks = createChunks(item, chunkSize);
    return enqueue(chunks);
  };

  const uploadItemInSingleChunk = async (item: UploadItem) => {
    const { url, payload } = getChunkSinglePayload(item, chunkSize);
    return save(payload, {
      url,
      onSuccess: onSuccess(item)
    });
  };

  const checkAvailableSpace = async (fileSize: number) => {
    const { upload_available_space: availableSpace } = await get<{
      upload_available_space: number;
    }>(UPLOAD_AVAILABLE_SPACE_URL);
    return availableSpace >= fileSize;
  };

  const uploadItem = async (item: UploadItem) => {
    const isSpaceAvailable = await checkAvailableSpace(item.file.size);
    if (!isSpaceAvailable) {
      onStatusUpdate(item, FileUploadStatus.Failed);
      return Promise.resolve();
    }

    onStatusUpdate(item, FileUploadStatus.Uploading);
    const chunks = getTotalChunk(item.file.size, chunkSize);
    if (chunks === 1) {
      return uploadItemInSingleChunk(item);
    }
    return uploadItemInChunks(item);
  };

  const addFiles = (newItems: UploadItem[]) => {
    setPendingUploadItems(prev => [...prev, ...newItems]);
  };

  const removeFile = (item: UploadItem) => {
    setPendingUploadItems(prev => prev.filter(i => i.uuid !== item.uuid));
  };

  useEffect(() => {
    // Ensures one file is broken down in chunks and uploaded to the server
    if (!processingItem && pendingUploadItems.length) {
      const item = pendingUploadItems[0];
      setProcessingItem(item);
      setPendingUploadItems(prev => prev.slice(1));
      uploadItem(item);
    }
  }, [pendingUploadItems, processingItem]);

  return { addFiles, removeFile, isLoading: !!processingItem || !!pendingUploadItems.length };
};

export default useChunkUpload;

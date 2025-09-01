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
  DEFAULT_CONCURRENT_MAX_CONNECTIONS
} from '../../constants/storageBrowser';
import useLoadData from '../useLoadData/useLoadData';
import { TaskServerResponse, TaskStatus } from '../../../reactComponents/TaskServer/types';
import { GET_TASKS_URL } from '../../../reactComponents/TaskServer/constants';
import {
  getChunksCompletePayload,
  getItemProgress,
  getItemsTotalProgress,
  getChunkItemPayload,
  createChunks,
  getStatusHashMap,
  addChunkToInProcess,
  isSpaceAvailableInServer,
  isAllChunksOfFileUploaded
} from './utils';
import {
  RegularFile,
  ChunkedFile,
  FileVariables,
  FileStatus,
  ChunkedFilesInProgress
} from './types';

interface UseChunkUploadResponse {
  addFiles: (items: RegularFile[]) => void;
  cancelFile: (item: RegularFile['uuid']) => void;
  isLoading: boolean;
}

interface ChunkUploadOptions {
  concurrentProcess?: number;
  updateFileVariables: (itemId: ChunkedFile['uuid'], variables: FileVariables) => void;
  onComplete: () => void;
}

const useChunkUpload = ({
  concurrentProcess = DEFAULT_CONCURRENT_MAX_CONNECTIONS,
  updateFileVariables,
  onComplete
}: ChunkUploadOptions): UseChunkUploadResponse => {
  const config = getLastKnownConfig();
  const chunkSize = config?.storage_browser?.file_upload_chunk_size ?? DEFAULT_CHUNK_SIZE;
  const [filesWaitingFinalStatus, setFilesWaitingFinalStatus] = useState<ChunkedFile['uuid'][]>([]);
  const [filesInProgress, setFilesInProgress] = useState<ChunkedFilesInProgress>({});

  const { save } = useSaveData();

  const processTaskServerResponse = (response: TaskServerResponse[]) => {
    const statusMap = getStatusHashMap(response);
    setFilesWaitingFinalStatus(prev => {
      const remainingFiles = prev.filter(uuid => {
        const fileStatus = statusMap[uuid];
        if (fileStatus === TaskStatus.Success || fileStatus === TaskStatus.Failure) {
          const mappedStatus =
            fileStatus === TaskStatus.Success ? FileStatus.Uploaded : FileStatus.Failed;
          updateFileVariables(uuid, { status: mappedStatus });
          return false; // remove the file as final status is received
        }
        return true;
      });
      if (remainingFiles.length === 0) {
        onComplete();
      }
      return remainingFiles;
    });
  };

  useLoadData<TaskServerResponse[]>(GET_TASKS_URL, {
    pollInterval: 5000,
    skip: filesWaitingFinalStatus.length === 0,
    onSuccess: processTaskServerResponse
  });

  const handleAllChunksUploaded = (chunk: ChunkedFile) => {
    const { url, payload } = getChunksCompletePayload(chunk);
    return save(payload, {
      url,
      onSuccess: () => setFilesWaitingFinalStatus(prev => [...prev, chunk.uuid]),
      onError: error => updateFileVariables(chunk.uuid, { status: FileStatus.Failed, error })
    });
  };

  const onChunkUploadSuccess = (chunk: ChunkedFile) => () => {
    setFilesInProgress(prev => {
      const isAllChunksUploaded = isAllChunksOfFileUploaded(prev, chunk);
      if (isAllChunksUploaded) {
        handleAllChunksUploaded(chunk);
        delete prev[chunk.uuid];
      }

      return prev;
    });
  };

  const onUploadProgress = (chunk: ChunkedFile) => (chunkProgress: ProgressEvent) => {
    setFilesInProgress(prev => {
      const allChunks = prev[chunk.uuid] || [];
      const chunk1 = allChunks.find(c => c.chunkNumber === chunk.chunkNumber);
      if (!chunk1) {
        return prev;
      }
      chunk1.progress = getItemProgress(chunkProgress);

      const totalProgress = getItemsTotalProgress(chunk, allChunks);
      updateFileVariables(chunk.uuid, { progress: totalProgress });
      return { ...prev, [chunk.uuid]: allChunks };
    });
  };

  const uploadChunkToServer = async (chunk: ChunkedFile) => {
    const { url, payload } = getChunkItemPayload(chunk);
    return save(payload, {
      url,
      onSuccess: onChunkUploadSuccess(chunk),
      onError: error => updateFileVariables(chunk.uuid, { status: FileStatus.Failed, error }),
      options: { onUploadProgress: onUploadProgress(chunk) }
    });
  };

  const processChunkedFile = async (chunk: ChunkedFile): Promise<void> => {
    const isFirstChunk = !filesInProgress[chunk.uuid];
    if (isFirstChunk) {
      updateFileVariables(chunk.uuid, { status: FileStatus.Uploading });
      const isUploadPossible = await isSpaceAvailableInServer(chunk.totalSize);
      if (!isUploadPossible) {
        const error = new Error('Upload server ran out of space. Try again later.');
        cancelFile(chunk.uuid);
        return updateFileVariables(chunk.uuid, { status: FileStatus.Failed, error });
      }
    }
    setFilesInProgress(prev => addChunkToInProcess(prev, chunk));

    return uploadChunkToServer(chunk);
  };

  const { enqueue, dequeue } = useQueueProcessor<ChunkedFile>(processChunkedFile, {
    concurrentProcess
  });

  const addFiles = (newFiles: RegularFile[]) => {
    newFiles.forEach(file => {
      const chunks = createChunks(file, chunkSize);
      enqueue(chunks);
    });
  };

  const cancelFile = (fileUuid: ChunkedFile['uuid']) => dequeue(fileUuid, 'uuid');

  return {
    addFiles,
    cancelFile,
    isLoading: !!(filesWaitingFinalStatus.length || filesInProgress.length)
  };
};

export default useChunkUpload;

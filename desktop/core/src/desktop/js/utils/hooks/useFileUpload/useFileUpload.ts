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
import useRegularUpload from './useRegularUpload';
import useChunkUpload from './useChunkUpload';
import { DEFAULT_CONCURRENT_MAX_CONNECTIONS } from '../../constants/storageBrowser';
import { getLastKnownConfig } from '../../../config/hueConfig';
import { FileStatus, RegularFile, FileVariables } from './types';
import { i18nReact } from '../../../utils/i18nReact';

interface UseUploadQueueResponse {
  uploadQueue: RegularFile[];
  addFiles: (newFiles: RegularFile[]) => void;
  cancelFile: (item: RegularFile) => void;
  isLoading: boolean;
}

interface UploadQueueOptions {
  isChunkUpload?: boolean;
  onComplete: () => RegularFile[] | void;
}

const useFileUpload = ({
  isChunkUpload = false,
  onComplete
}: UploadQueueOptions): UseUploadQueueResponse => {
  const { t } = i18nReact.useTranslation();

  const config = getLastKnownConfig();
  const concurrentProcess =
    config?.storage_browser.concurrent_max_connection ?? DEFAULT_CONCURRENT_MAX_CONNECTIONS;

  const [uploadQueue, setUploadQueue] = useState<RegularFile[]>([]);

  const updateFileVariables = (
    itemId: RegularFile['uuid'],
    { status, error, progress }: FileVariables
  ) => {
    setUploadQueue(prev => {
      return prev.map(queueItem => {
        if (queueItem.uuid === itemId) {
          return {
            ...queueItem,
            status: status ?? queueItem.status,
            error: error ?? queueItem.error,
            progress: progress ?? queueItem.progress
          };
        }
        return queueItem;
      });
    });
  };

  const {
    addFiles: addToChunkUpload,
    cancelFile: cancelFromChunkUpload,
    isLoading: isChunkLoading
  } = useChunkUpload({
    concurrentProcess,
    updateFileVariables,
    onComplete
  });

  const {
    addFiles: addToRegularUpload,
    cancelFile: cancelFromRegularUpload,
    isLoading: isRegularLoading
  } = useRegularUpload({
    concurrentProcess,
    updateFileVariables,
    onComplete
  });

  const cancelFile = (fileItem: RegularFile) => {
    const queueItem = uploadQueue.find(q => q.uuid === fileItem.uuid);
    if (queueItem?.status === FileStatus.Pending) {
      const error = new Error(t('Upload cancelled'));
      updateFileVariables(fileItem.uuid, { status: FileStatus.Cancelled, error });

      if (isChunkUpload) {
        cancelFromChunkUpload(fileItem.uuid);
      } else {
        cancelFromRegularUpload(fileItem.uuid);
      }
    }
  };

  const addFiles = (fileItems: RegularFile[]) => {
    if (fileItems.length > 0) {
      setUploadQueue(prev => [...prev, ...fileItems]);

      if (isChunkUpload) {
        addToChunkUpload(fileItems);
      } else {
        addToRegularUpload(fileItems);
      }
    }
  };

  return { uploadQueue, cancelFile, addFiles, isLoading: isChunkLoading || isRegularLoading };
};

export default useFileUpload;

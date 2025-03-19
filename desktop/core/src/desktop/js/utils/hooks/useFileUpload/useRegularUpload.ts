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

import useQueueProcessor from '../useQueueProcessor/useQueueProcessor';
import { UPLOAD_FILE_URL } from '../../../apps/storageBrowser/api';
import { DEFAULT_CONCURRENT_MAX_CONNECTIONS } from '../../constants/storageBrowser';
import useSaveData from '../useSaveData/useSaveData';
import { getItemProgress, UploadItem, UploadItemVariables, UploadStatus } from './util';

interface UseUploadQueueResponse {
  addFiles: (item: UploadItem[]) => void;
  removeFile: (uuid: UploadItem['uuid']) => void;
  isLoading: boolean;
}

interface UploadQueueOptions {
  concurrentProcess?: number;
  onItemUpdate: (item: UploadItem['uuid'], variables: UploadItemVariables) => void;
  onComplete: () => void;
}

const useRegularUpload = ({
  concurrentProcess = DEFAULT_CONCURRENT_MAX_CONNECTIONS,
  onItemUpdate,
  onComplete
}: UploadQueueOptions): UseUploadQueueResponse => {
  const { save } = useSaveData(UPLOAD_FILE_URL, {
    postOptions: {
      qsEncodeData: false,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }
  });

  const processUploadItem = async (item: UploadItem) => {
    onItemUpdate(item.uuid, { status: UploadStatus.Uploading });

    const payload = new FormData();
    payload.append('file', item.file);
    payload.append('destination_path', item.filePath);

    return save(payload, {
      onSuccess: () => {
        onItemUpdate(item.uuid, { status: UploadStatus.Uploaded });
      },
      onError: error => {
        onItemUpdate(item.uuid, { status: UploadStatus.Failed, error });
      },
      postOptions: {
        onUploadProgress: progress => {
          const itemProgress = getItemProgress(progress);
          onItemUpdate(item.uuid, { progress: itemProgress });
        }
      }
    });
  };

  const {
    enqueue: addFiles,
    dequeue,
    isLoading
  } = useQueueProcessor<UploadItem>(processUploadItem, {
    concurrentProcess,
    onSuccess: onComplete
  });

  const removeFile = (itemId: UploadItem['uuid']) => dequeue(itemId, 'uuid');

  return { addFiles, removeFile, isLoading };
};

export default useRegularUpload;

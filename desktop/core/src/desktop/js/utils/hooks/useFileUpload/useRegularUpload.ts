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
import {
  DEFAULT_CONCURRENT_MAX_CONNECTIONS,
  FileUploadStatus
} from '../../constants/storageBrowser';
import useSaveData from '../useSaveData/useSaveData';
import { UploadItem } from './util';

interface UseUploadQueueResponse {
  addFiles: (item: UploadItem[]) => void;
  removeFile: (item: UploadItem) => void;
  isLoading: boolean;
}

interface UploadQueueOptions {
  concurrentProcess?: number;
  onStatusUpdate: (item: UploadItem, newStatus: FileUploadStatus) => void;
  onComplete: () => void;
}

const useRegularUpload = ({
  concurrentProcess = DEFAULT_CONCURRENT_MAX_CONNECTIONS,
  onStatusUpdate,
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
    onStatusUpdate(item, FileUploadStatus.Uploading);

    const payload = new FormData();
    payload.append('file', item.file);
    payload.append('destination_path', item.filePath);

    return save(payload, {
      onSuccess: () => {
        onStatusUpdate(item, FileUploadStatus.Uploaded);
      },
      onError: () => {
        onStatusUpdate(item, FileUploadStatus.Failed);
      }
    });
  };

  const {
    enqueue: addFiles,
    dequeue: removeFile,
    isLoading
  } = useQueueProcessor<UploadItem>(processUploadItem, {
    concurrentProcess,
    onSuccess: onComplete
  });

  return { addFiles, removeFile, isLoading };
};

export default useRegularUpload;

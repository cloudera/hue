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
import { getItemProgress } from './utils';
import { RegularFile, FileVariables, FileStatus } from './types';

interface UseUploadQueueResponse {
  addFiles: (item: RegularFile[]) => void;
  cancelFile: (uuid: RegularFile['uuid']) => void;
  isLoading: boolean;
}

interface UploadQueueOptions {
  concurrentProcess?: number;
  updateFileVariables: (item: RegularFile['uuid'], variables: FileVariables) => void;
  onComplete: () => void;
}

const useRegularUpload = ({
  concurrentProcess = DEFAULT_CONCURRENT_MAX_CONNECTIONS,
  updateFileVariables,
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

  const processRegularFile = async (item: RegularFile) => {
    updateFileVariables(item.uuid, { status: FileStatus.Uploading });

    const payload = new FormData();
    payload.append('file', item.file);
    payload.append('destination_path', item.filePath);

    return save(payload, {
      onSuccess: () => {
        updateFileVariables(item.uuid, { status: FileStatus.Uploaded });
      },
      onError: error => {
        updateFileVariables(item.uuid, { status: FileStatus.Failed, error });
      },
      postOptions: {
        onUploadProgress: progress => {
          const itemProgress = getItemProgress(progress);
          updateFileVariables(item.uuid, { progress: itemProgress });
        }
      }
    });
  };

  const {
    enqueue: addFiles,
    dequeue,
    isLoading
  } = useQueueProcessor<RegularFile>(processRegularFile, {
    concurrentProcess,
    onSuccess: onComplete
  });

  const cancelFile = (itemId: RegularFile['uuid']) => dequeue(itemId, 'uuid');

  return { addFiles, cancelFile, isLoading };
};

export default useRegularUpload;

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

interface UseRegularUploadResponse {
  addFiles: (items: RegularFile[], overwrite?: boolean) => void;
  cancelFile: (uuid: RegularFile['uuid']) => void;
  isLoading: boolean;
}

interface UseRegularUploadProps {
  concurrentProcess?: number;
  updateFileVariables: (item: RegularFile['uuid'], variables: FileVariables) => void;
  onComplete: () => void;
}

const useRegularUpload = ({
  concurrentProcess = DEFAULT_CONCURRENT_MAX_CONNECTIONS,
  updateFileVariables,
  onComplete
}: UseRegularUploadProps): UseRegularUploadResponse => {
  const { save } = useSaveData(UPLOAD_FILE_URL);

  const processRegularFile = async (item: RegularFile) => {
    updateFileVariables(item.uuid, { status: FileStatus.Uploading });

    const payload = new FormData();
    payload.append('file', item.file);

    return save(payload, {
      onSuccess: () => {
        updateFileVariables(item.uuid, { status: FileStatus.Uploaded });
      },
      onError: error => {
        updateFileVariables(item.uuid, { status: FileStatus.Failed, error });
      },
      options: {
        params: {
          destination_path: item.filePath,
          overwrite: item.overwrite ? 'true' : 'false'
        },
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

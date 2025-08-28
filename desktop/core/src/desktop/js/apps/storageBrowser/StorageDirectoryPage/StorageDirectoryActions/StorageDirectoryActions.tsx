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

import React from 'react';
import { inTrash } from '../../utils/utils';
import CreateAndUploadAction from './CreateAndUpload/CreateAndUploadAction';
import TrashActions from './Trash/TrashActions';
import FileAndFolderActions from './FileAndFolder/FileAndFolderActions';
import { FileStats, FileSystem, StorageDirectoryTableData } from '../../types';
import huePubSub from '../../../../utils/huePubSub';

interface StorageDirectoryActionsProps {
  fileStats: FileStats;
  fileSystem: FileSystem;
  onFilePathChange: (path: string) => void;
  onActionSuccess: () => void;
  selectedFiles: StorageDirectoryTableData[];
  onFilesDrop: (files: File[]) => void;
}

const StorageDirectoryActions = ({
  fileStats,
  fileSystem,
  onFilePathChange,
  onActionSuccess,
  selectedFiles,
  onFilesDrop
}: StorageDirectoryActionsProps): JSX.Element => {
  const onApiSuccess = () => {
    onActionSuccess();
  };

  const onApiError = (error: Error) => {
    huePubSub.publish('hue.error', error);
  };

  if (inTrash(fileStats.path)) {
    return (
      <TrashActions
        selectedFiles={selectedFiles}
        currentPath={fileStats.path}
        onActionSuccess={onApiSuccess}
        onActionError={onApiError}
        onTrashEmptySuccess={() => onFilePathChange(fileSystem.userHomeDirectory)}
      />
    );
  }

  return (
    <>
      <FileAndFolderActions
        config={fileSystem.config}
        currentPath={fileStats.path}
        selectedFiles={selectedFiles}
        onActionSuccess={onApiSuccess}
        onActionError={onApiError}
      />
      <CreateAndUploadAction
        currentPath={fileStats.path}
        onActionSuccess={onApiSuccess}
        onActionError={onApiError}
        onFilesUpload={onFilesDrop}
      />
    </>
  );
};

export default StorageDirectoryActions;

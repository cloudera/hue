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

import { getLastKnownConfig } from 'config/hueConfig';
import {
  BrowserViewType,
  StorageDirectoryTableData
} from '../../../../reactComponents/FileChooser/types';
import {
  isHDFS,
  isOFS,
  isABFSRoot,
  isGSRoot,
  isOFSServiceID,
  isOFSVol,
  isS3Root,
  isABFS,
  isGS,
  isS3,
  isOFSRoot,
  inTrash
} from '../../../../utils/storageBrowserUtils';
import { SUPPORTED_COMPRESSED_FILE_EXTENTION } from '../../../../utils/constants/storageBrowser';

export enum ActionType {
  Copy = 'copy',
  Move = 'move',
  Summary = 'summary',
  Rename = 'rename',
  Replication = 'replication',
  Delete = 'delete',
  Compress = 'compress',
  Extract = 'extract',
  Download = 'download',
  ChangeOwnerAndGroup = 'changeOwnerAndGroup'
}

const isValidFileOrFolder = (filePath: string): boolean => {
  return (
    isHDFS(filePath) ||
    (isS3(filePath) && !isS3Root(filePath)) ||
    (isGS(filePath) && !isGSRoot(filePath)) ||
    (isABFS(filePath) && !isABFSRoot(filePath)) ||
    (isOFS(filePath) && !isOFSRoot(filePath) && !isOFSServiceID(filePath) && !isOFSVol(filePath))
  );
};

const isFileCompressed = (filePath: string): boolean => {
  return SUPPORTED_COMPRESSED_FILE_EXTENTION.some(ext => filePath.endsWith(ext));
};

const isActionEnabled = (file: StorageDirectoryTableData, action: ActionType): boolean => {
  const config = getLastKnownConfig()?.storage_browser;
  switch (action) {
    case ActionType.Summary:
      return (isHDFS(file.path) || isOFS(file.path)) && file.type === BrowserViewType.file;
    case ActionType.Replication:
      return isHDFS(file.path) && file.type === BrowserViewType.file;
    case ActionType.Rename:
    case ActionType.Copy:
    case ActionType.Delete:
    case ActionType.Move:
      return isValidFileOrFolder(file.path);
    case ActionType.Extract:
      return (
        !!config?.enable_extract_uploaded_archive &&
        isHDFS(file.path) &&
        isFileCompressed(file.path)
      );
    case ActionType.Compress:
      return !!config?.enable_extract_uploaded_archive && isHDFS(file.path);
    case ActionType.Download:
      return !!config?.enable_file_download_button && file.type === BrowserViewType.file;
    case ActionType.ChangeOwnerAndGroup:
      return isValidFileOrFolder(file.path);
    default:
      return false;
  }
};

const isSingleFileActionEnabled = (
  files: StorageDirectoryTableData[],
  action: ActionType
): boolean => {
  return files.length === 1 && isActionEnabled(files[0], action);
};

const isMultipleFileActionEnabled = (
  files: StorageDirectoryTableData[],
  action: ActionType
): boolean => {
  return files.length !== 0 && files.every(file => isActionEnabled(file, action));
};

export const getEnabledActions = (
  files: StorageDirectoryTableData[],
  isFsSuperUser?: boolean
): {
  enabled: boolean;
  type: ActionType;
  label: string;
}[] => {
  const isAnyFileInTrash = files.some(file => inTrash(file.path));
  const isNoFileSelected = files && files.length === 0;
  if (isAnyFileInTrash || isNoFileSelected) {
    return [];
  }

  // order of the elements will be the order of the action menu
  const actions = [
    {
      enabled: isMultipleFileActionEnabled(files, ActionType.Copy),
      type: ActionType.Copy,
      label: 'Copy'
    },
    {
      enabled: isMultipleFileActionEnabled(files, ActionType.Move),
      type: ActionType.Move,
      label: 'Move'
    },
    {
      enabled: isSingleFileActionEnabled(files, ActionType.Summary),
      type: ActionType.Summary,
      label: 'View Summary'
    },
    {
      enabled: isSingleFileActionEnabled(files, ActionType.Rename),
      type: ActionType.Rename,
      label: 'Rename'
    },
    {
      enabled: isMultipleFileActionEnabled(files, ActionType.Delete),
      type: ActionType.Delete,
      label: 'Delete'
    },
    {
      enabled: isSingleFileActionEnabled(files, ActionType.Replication),
      type: ActionType.Replication,
      label: 'Set Replication'
    },
    {
      enabled: isMultipleFileActionEnabled(files, ActionType.Compress),
      type: ActionType.Compress,
      label: 'Compress'
    },
    {
      enabled: isSingleFileActionEnabled(files, ActionType.Extract),
      type: ActionType.Extract,
      label: 'Extract'
    },
    {
      enabled: isSingleFileActionEnabled(files, ActionType.Download),
      type: ActionType.Download,
      label: 'Download'
    },
    {
      enabled:
        !!isFsSuperUser && isMultipleFileActionEnabled(files, ActionType.ChangeOwnerAndGroup),
      type: ActionType.ChangeOwnerAndGroup,
      label: 'Change Owner / Group'
    }
  ].filter(e => e.enabled);

  return actions;
};

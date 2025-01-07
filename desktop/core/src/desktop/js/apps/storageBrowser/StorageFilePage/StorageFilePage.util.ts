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

import { TFunction } from 'i18next';
import { FileStats } from '../../../reactComponents/FileChooser/types';
import { formatTimestamp } from '../../../utils/dateTimeUtils';
import formatBytes from '../../../utils/formatBytes';
import {
  SUPPORTED_FILE_EXTENSIONS,
  SupportedFileTypes
} from '../../../utils/constants/storageBrowser';

export type MetaData = {
  name: string;
  label: string;
  value: string;
};

export const getFileMetaData = (t: TFunction, fileStats: FileStats): MetaData[][] => {
  return [
    [
      {
        name: 'size',
        label: t('Size'),
        value: formatBytes(fileStats.size)
      },
      {
        name: 'user',
        label: t('Created By'),
        value: fileStats.user
      }
    ],
    [
      {
        name: 'group',
        label: t('Group'),
        value: fileStats.group
      },
      {
        name: 'permissions',
        label: t('Permissions'),
        value: fileStats.rwx
      },
      {
        name: 'mtime',
        label: t('Last Modified'),
        value: formatTimestamp(new Date(fileStats.mtime * 1000))
      }
    ]
  ];
};

export const getFileType = (fileName: string): SupportedFileTypes => {
  const fileExtension = fileName?.split('.')?.pop()?.toLowerCase();
  if (!fileExtension) {
    return SupportedFileTypes.OTHER;
  }
  return SUPPORTED_FILE_EXTENSIONS[fileExtension] ?? SupportedFileTypes.OTHER;
};

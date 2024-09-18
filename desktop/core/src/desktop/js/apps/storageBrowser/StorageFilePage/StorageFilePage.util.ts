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
import { PathAndFileData } from '../../../reactComponents/FileChooser/types';
import { formatTimestamp } from '../../../utils/dateTimeUtils';
import formatBytes from '../../../utils/formatBytes';
import { get } from '../../../api/utils';

export type MetaData = {
  name: string;
  label: string;
  value: string;
};

export const getFileMetaData = (t: TFunction, fileData: PathAndFileData): MetaData[][] => {
  return [
    [
      {
        name: 'size',
        label: t('Size'),
        value: formatBytes(fileData.stats?.size)
      },
      {
        name: 'user',
        label: t('Created By'),
        value: fileData.stats?.user
      }
    ],
    [
      {
        name: 'group',
        label: t('Group'),
        value: fileData.stats?.group
      },
      {
        name: 'permissions',
        label: t('Permissions'),
        value: fileData.rwx
      },
      {
        name: 'mtime',
        label: t('Last Modified'),
        value: fileData.stats?.mtime
          ? formatTimestamp(new Date(Number(fileData.stats.mtime) * 1000))
          : '-'
      }
    ]
  ];
};

export const downloadFile = async (url: string): Promise<void> => {
  try {
    const response = await get<File>(url, { responseType: 'blob' });

    if (response) {
      const blob = new Blob([response], { type: response.type });

      const downloadUrl = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = url.split('/').pop() || 'download';
      a.click();
      URL.revokeObjectURL(downloadUrl);
    }
  } catch (error) {
    console.error('Error downloading file:', error);
  }
};

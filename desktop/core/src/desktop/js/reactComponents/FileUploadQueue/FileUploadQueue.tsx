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

import React, { useState } from 'react';
import CloseIcon from '../../components/icons/CloseIcon';
import { i18nReact } from '../../utils/i18nReact';
import { RegularFile, FileStatus } from '../../utils/hooks/useFileUpload/types';
import useFileUpload from '../../utils/hooks/useFileUpload/useFileUpload';
import { DEFAULT_ENABLE_CHUNK_UPLOAD } from '../../utils/constants/storageBrowser';
import { getLastKnownConfig } from '../../config/hueConfig';
import FileUploadRow from './FileUploadRow/FileUploadRow';

import './FileUploadQueue.scss';

interface FileUploadQueueProps {
  filesQueue: RegularFile[];
  onClose: () => void;
  onComplete: () => void;
}

const sortOrder = [
  FileStatus.Uploading,
  FileStatus.Failed,
  FileStatus.Pending,
  FileStatus.Cancelled,
  FileStatus.Uploaded
].reduce((acc: Record<string, number>, status: FileStatus, index: number) => {
  acc[status] = index + 1;
  return acc;
}, {});

const FileUploadQueue: React.FC<FileUploadQueueProps> = ({ filesQueue, onClose, onComplete }) => {
  const config = getLastKnownConfig();
  const isChunkUpload =
    (config?.storage_browser.enable_chunked_file_upload ?? DEFAULT_ENABLE_CHUNK_UPLOAD) &&
    !!config?.hue_config.enable_task_server;

  const { t } = i18nReact.useTranslation();

  const { uploadQueue, onCancel } = useFileUpload(filesQueue, {
    isChunkUpload,
    onComplete
  });

  const uploadedCount = uploadQueue.filter(item => item.status === FileStatus.Uploaded).length;
  const pendingCount = uploadQueue.filter(
    item => item.status === FileStatus.Pending || item.status === FileStatus.Uploading
  ).length;

  return (
    <details className="upload-queue cuix antd" open>
      <summary className="upload-queue__header" data-testid="upload-queue__header">
        {pendingCount > 0
          ? t('{{count}} file(s) remaining', {
              count: pendingCount
            })
          : t('{{count}} file(s) uploaded', {
              count: uploadedCount
            })}
        <CloseIcon onClick={onClose} height={16} width={16} />
      </summary>
      <div className="upload-queue__list">
        {uploadQueue
          .sort((a, b) => sortOrder[a.status] - sortOrder[b.status])
          .map((row: RegularFile) => (
            <FileUploadRow
              key={`${row.filePath}__${row.file.name}`}
              data={row}
              onCancel={() => onCancel(row)}
            />
          ))}
      </div>
    </details>
  );
};

export default FileUploadQueue;

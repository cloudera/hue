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
import './FileUploadQueue.scss';
import { Tooltip } from 'antd';
import CloseIcon from '../../components/icons/CloseIcon';
import { i18nReact } from '../../utils/i18nReact';
import formatBytes from '../../utils/formatBytes';
import StatusPendingIcon from '@cloudera/cuix-core/icons/react/StatusPendingIcon';
import StatusInProgressIcon from '@cloudera/cuix-core/icons/react/StatusInProgressIcon';
import StatusSuccessIcon from '@cloudera/cuix-core/icons/react/StatusSuccessIcon';
import StatusStoppedIcon from '@cloudera/cuix-core/icons/react/StatusStoppedIcon';
import StatusErrorIcon from '@cloudera/cuix-core/icons/react/StatusErrorIcon';
import { UploadItem } from '../../utils/hooks/useFileUpload/util';
import useFileUpload from '../../utils/hooks/useFileUpload/useFileUpload';
import {
  DEFAULT_ENABLE_CHUNK_UPLOAD,
  FileUploadStatus
} from '../../utils/constants/storageBrowser';
import { getLastKnownConfig } from '../../config/hueConfig';

interface FileUploadQueueProps {
  filesQueue: UploadItem[];
  onClose: () => void;
  onComplete: () => void;
}

const sortOrder = [
  FileUploadStatus.Uploading,
  FileUploadStatus.Failed,
  FileUploadStatus.Pending,
  FileUploadStatus.Canceled,
  FileUploadStatus.Uploaded
].reduce((acc: Record<string, number>, status: FileUploadStatus, index: number) => {
  acc[status] = index + 1;
  return acc;
}, {});

const FileUploadQueue: React.FC<FileUploadQueueProps> = ({ filesQueue, onClose, onComplete }) => {
  const config = getLastKnownConfig();
  const isChunkUpload =
    config?.storage_browser.enable_chunked_file_uploader ?? DEFAULT_ENABLE_CHUNK_UPLOAD;
  const { t } = i18nReact.useTranslation();
  const [isExpanded, setIsExpanded] = useState(true);

  const { uploadQueue, onCancel } = useFileUpload(filesQueue, {
    isChunkUpload,
    onComplete
  });

  const uploadedCount = uploadQueue.filter(
    item => item.status === FileUploadStatus.Uploaded
  ).length;
  const pendingCount = uploadQueue.filter(
    item => item.status === FileUploadStatus.Pending || item.status === FileUploadStatus.Uploading
  ).length;

  const statusIcon = {
    [FileUploadStatus.Pending]: <StatusPendingIcon />,
    [FileUploadStatus.Uploading]: <StatusInProgressIcon />,
    [FileUploadStatus.Uploaded]: <StatusSuccessIcon />,
    [FileUploadStatus.Canceled]: <StatusStoppedIcon />,
    [FileUploadStatus.Failed]: <StatusErrorIcon />
  };

  return (
    <div className="upload-queue cuix antd">
      <div
        className="upload-queue__header"
        data-testid="upload-queue__header"
        onClick={() => setIsExpanded(prev => !prev)}
      >
        {pendingCount > 0
          ? t('{{count}} file(s) remaining', {
              count: pendingCount
            })
          : t('{{count}} file(s) uploaded', {
              count: uploadedCount
            })}
        <CloseIcon onClick={onClose} height={16} width={16} />
      </div>
      {isExpanded && (
        <div className="upload-queue__list">
          {uploadQueue
            .sort((a, b) => sortOrder[a.status] - sortOrder[b.status])
            .map((row: UploadItem) => (
              <div key={`${row.filePath}__${row.file.name}`} className="upload-queue__list__row">
                <Tooltip
                  title={row.status}
                  mouseEnterDelay={1.5}
                  className="upload-queue__list__row__status"
                >
                  {statusIcon[row.status]}
                </Tooltip>
                <div className="upload-queue__list__row__name">{row.file.name}</div>
                <div className="upload-queue__list__row__size">{formatBytes(row.file.size)}</div>
                {row.status === FileUploadStatus.Pending && (
                  <Tooltip
                    title={t('Cancel')}
                    mouseEnterDelay={1.5}
                    className="upload-queue__list__row__close"
                  >
                    <CloseIcon
                      data-testid="upload-queue__list__row__close-icon"
                      onClick={() => onCancel(row)}
                      height={16}
                      width={16}
                    />
                  </Tooltip>
                )}
              </div>
            ))}
        </div>
      )}
    </div>
  );
};

export default FileUploadQueue;

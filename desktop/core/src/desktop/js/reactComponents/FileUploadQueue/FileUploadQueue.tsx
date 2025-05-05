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
import CloseIcon from '@cloudera/cuix-core/icons/react/CloseIcon';
import CaratDownIcon from '@cloudera/cuix-core/icons/react/CaratDownIcon';
import CaratUpIcon from '@cloudera/cuix-core/icons/react/CaratUpIcon';
import { i18nReact } from '../../utils/i18nReact';
import { RegularFile, FileStatus } from '../../utils/hooks/useFileUpload/types';
import useFileUpload from '../../utils/hooks/useFileUpload/useFileUpload';
import { DEFAULT_ENABLE_CHUNK_UPLOAD } from '../../utils/constants/storageBrowser';
import { getLastKnownConfig } from '../../config/hueConfig';
import FileUploadRow from './FileUploadRow/FileUploadRow';
import { useHuePubSub } from '../../utils/hooks/useHuePubSub/useHuePubSub';

import './FileUploadQueue.scss';
import huePubSub from '../../utils/huePubSub';
import { BorderlessButton } from 'cuix/dist/components/Button';

interface FileUploadEvent {
  files: RegularFile[];
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

const FileUploadQueue = (): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const [filesQueue, setFilesQueue] = useState<RegularFile[]>([]);
  const [expandQueue, setExpandQueue] = useState<boolean>(true);

  useHuePubSub<FileUploadEvent>({
    topic: 'hue.file.upload.start',
    callback: (newData?: FileUploadEvent) => {
      if (newData?.files) {
        setFilesQueue(newData.files);
      }
    }
  });

  const onComplete = () => {
    huePubSub.publish('hue.file.upload.complete');
  };

  const onClose = () => {
    setFilesQueue([]);
  };

  const config = getLastKnownConfig();
  const isChunkUpload =
    (config?.storage_browser.enable_chunked_file_upload ?? DEFAULT_ENABLE_CHUNK_UPLOAD) &&
    !!config?.hue_config.enable_task_server;

  const { uploadQueue, onCancel } = useFileUpload(filesQueue, {
    isChunkUpload,
    onComplete
  });

  const uploadedCount = uploadQueue.filter(item => item.status === FileStatus.Uploaded).length;
  const pendingCount = uploadQueue.filter(
    item => item.status === FileStatus.Pending || item.status === FileStatus.Uploading
  ).length;
  const failedCount = uploadQueue.filter(item => item.status === FileStatus.Failed).length;

  if (!filesQueue.length) {
    return <></>;
  }

  return (
    <div className="hue-upload-queue-container antd cuix">
      <div className="hue-upload-queue-container__header" data-testid="hue-upload-queue__header">
        {pendingCount > 0
          ? t('{{uploadedCount}} / {{totalCount}} uploaded, {{failedCount}} failed ', {
              uploadedCount,
              totalCount: uploadQueue.length,
              failedCount
            })
          : t('{{count}} file(s) uploaded', {
              count: uploadedCount
            })}
        <div className="hue-upload-queue-container__header__button-group">
          <BorderlessButton
            onClick={() => setExpandQueue(!expandQueue)}
            data-testid="hue-upload-queue-container__expand-button"
            icon={expandQueue ? <CaratDownIcon /> : <CaratUpIcon />}
          />
          <BorderlessButton
            onClick={onClose}
            data-testid="hue-upload-queue-container__close-button"
            icon={<CloseIcon />}
          />
        </div>
      </div>
      {expandQueue ? (
        <div className="hue-upload-queue-container__list">
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
      ) : (
        <></>
      )}
    </div>
  );
};

export default FileUploadQueue;

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
import './FileUploadRow.scss';
import { Tooltip } from 'antd';
import CloseIcon from '../../../components/icons/CloseIcon';
import formatBytes from '../../../utils/formatBytes';
import StatusPendingIcon from '@cloudera/cuix-core/icons/react/StatusPendingIcon';
import StatusInProgressIcon from '@cloudera/cuix-core/icons/react/StatusInProgressIcon';
import StatusSuccessIcon from '@cloudera/cuix-core/icons/react/StatusSuccessIcon';
import StatusStoppedIcon from '@cloudera/cuix-core/icons/react/StatusStoppedIcon';
import StatusErrorIcon from '@cloudera/cuix-core/icons/react/StatusErrorIcon';
import { RegularFile, FileStatus } from '../../../utils/hooks/useFileUpload/types';
import { i18nReact } from '../../../utils/i18nReact';

interface FileUploadRowProps {
  data: RegularFile;
  onCancel: () => void;
}

const statusIcon = {
  [FileStatus.Pending]: <StatusPendingIcon />,
  [FileStatus.Uploading]: <StatusInProgressIcon />,
  [FileStatus.Uploaded]: <StatusSuccessIcon />,
  [FileStatus.Cancelled]: <StatusStoppedIcon />,
  [FileStatus.Failed]: <StatusErrorIcon />
};

const FileUploadRow: React.FC<FileUploadRowProps> = ({ data, onCancel }) => {
  const { t } = i18nReact.useTranslation();

  return (
    <div key={`${data.filePath}__${data.file.name}`} className="hue-upload-queue-row">
      <div className="hue-upload-queue-row__container">
        <Tooltip title={data.status} mouseEnterDelay={1.5} className="hue-upload-queue-row__status">
          {statusIcon[data.status]}
        </Tooltip>
        <div className="hue-upload-queue-row__name">{data.file.name}</div>
        <div className="hue-upload-queue-row__size">{formatBytes(data.file.size)}</div>
        {data.status === FileStatus.Pending && (
          <Tooltip title={t('Cancel')} mouseEnterDelay={1.5}>
            <CloseIcon data-testid="hue-upload-queue-row__close-icon" onClick={onCancel} />
          </Tooltip>
        )}
      </div>
      <div
        className="hue-upload-queue-row__progressbar"
        data-testid="hue-upload-queue-row__progressbar"
        style={{
          width: `${data.status === FileStatus.Uploading ? data.progress : 0}%`
        }}
      />
    </div>
  );
};

export default FileUploadRow;

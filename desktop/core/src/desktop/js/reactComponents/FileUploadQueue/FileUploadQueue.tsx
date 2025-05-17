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
import Modal from 'cuix/dist/components/Modal';
import { Button } from 'antd'; 
import ReactDOM from 'react-dom';
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
import huePubSub from '../../utils/huePubSub';
import { BorderlessButton } from 'cuix/dist/components/Button';
import { FILE_UPLOAD_START_EVENT, FILE_UPLOAD_SUCCESS_EVENT } from './event';

import './FileUploadQueue.scss';

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

  const [expandQueue, setExpandQueue] = useState<boolean>(true);
  const [isVisible, setIsVisible] = useState<boolean>(false);
  const [uploadedFiles, setUploadedFiles] = useState<RegularFile[]>([]); // Track successfully uploaded files.
  const [conflictFiles, setConflictFiles] = useState<RegularFile[]>([]); // Track conflicting files.
  const [isModalVisible, setIsModalVisible] = useState<boolean>(false); // State for controlling modal visibility.

  const onComplete = () => {
    huePubSub.publish(FILE_UPLOAD_SUCCESS_EVENT);
    // Update the list of successfully uploaded files when uploads complete.
    const newlyUploadedFiles = uploadQueue.filter(file => file.status === FileStatus.Uploaded);
    setUploadedFiles(prevUploadedFiles => [...prevUploadedFiles, ...newlyUploadedFiles]);
  };

  const config = getLastKnownConfig();
  const isChunkUpload =
    (config?.storage_browser.enable_chunked_file_upload ?? DEFAULT_ENABLE_CHUNK_UPLOAD) &&
    !!config?.hue_config.enable_task_server;

  const { uploadQueue, cancelFile, addFiles } = useFileUpload({
    isChunkUpload,
    onComplete
  });

  useHuePubSub<FileUploadEvent>({
    topic: FILE_UPLOAD_START_EVENT,
    callback: (data?: FileUploadEvent) => {
      if (data?.files) {
        setIsVisible(true);
        //addFiles(data.files);
        resolveFileConflicts(data.files); // Resolve any conflicts on enqueue.
      }
    }
  });

  const resolveFileConflicts = (newFiles: RegularFile[]) => {
    // Check for conflicts with already uploaded files.
    const conflicting = newFiles.filter(newFile =>
      uploadedFiles.some(uploadedFile => uploadedFile.file.name === newFile.file.name)
    );

    if (conflicting.length > 0) {
      setConflictFiles(conflicting);
      setIsModalVisible(true); // Show conflict resolution modal.
    } else {
      // No conflicts, directly add files.
      addFiles(newFiles);
      setIsVisible(true);
    }
  };

  const handleModalOk = (overwrite: boolean) => {
    if (overwrite) {
      // Overwrite files: Add conflicting files to the upload queue (new versions).
      addFiles(conflictFiles);
    } else {
      // Keep original files: Filter out conflicting files and only add new non-conflicting files.
      const nonConflictingFiles = conflictFiles.filter(
        file => !uploadedFiles.some(uploadedFile => uploadedFile.file.name === file.file.name)
      );
      addFiles(nonConflictingFiles);
    }
    setConflictFiles([]); // Reset conflict list.
    setIsModalVisible(false); // Close modal.
    setIsVisible(true);
  };


  const onClose = () => {
    uploadQueue.forEach(file => cancelFile(file));
    setIsVisible(false);
  };

  const uploadedCount = uploadQueue.filter(item => item.status === FileStatus.Uploaded).length;
  const pendingCount = uploadQueue.filter(
    item => item.status === FileStatus.Pending || item.status === FileStatus.Uploading
  ).length;
  const failedCount = uploadQueue.filter(item => item.status === FileStatus.Failed).length;

  if (!isVisible) {
    return <></>;
  }

  const getHeaderText = () => {
    const fileText = uploadQueue.length > 1 ? 'files' : 'file';
    const uploadedText = `{{uploadedCount}} ${fileText} uploaded`;
    const pendingText = pendingCount > 0 ? `{{pendingCount}} ${fileText} remaining` : '';
    const failedText = failedCount > 0 ? `, {{failedCount}} failed` : '';
    if (pendingCount > 0) {
      return `${pendingText}${failedText}`;
    }
    return `${uploadedText}${failedText}`;
  };

  return (
    <>
      {isModalVisible &&
        ReactDOM.createPortal(
          <Modal
            title={t('Resolve Filename Conflicts')}
            visible={isModalVisible}
            onCancel={() => setIsModalVisible(false)}
            footer={[
              <Button key="keep" onClick={() => handleModalOk(false)} data-testid="keep-original-btn">
                {t('Keep Original Files')}
              </Button>,
              <Button key="overwrite" type="primary" onClick={() => handleModalOk(true)} data-testid="overwrite-btn">
                {t('Overwrite Files')}
              </Button>
            ]}
          >
            {t('Some files you are trying to upload already exist in the uploaded files')}
            <ul>
              {conflictFiles.map(file => (
                <li key={file.file.name}>{file.file.name}</li>
              ))}
            </ul>
          </Modal>,
          document.body
        )}
      <div className="hue-upload-queue-container antd cuix">
        <div className="hue-upload-queue-container__header" data-testid="hue-upload-queue__header">
          {t(getHeaderText(), {
            pendingCount,
            uploadedCount,
            failedCount
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
        {expandQueue && (
          <div className="hue-upload-queue-container__list">
            {uploadQueue
              .sort((a, b) => sortOrder[a.status] - sortOrder[b.status])
              .map((row: RegularFile, index: number) => (
                <FileUploadRow
                  key={`${row.filePath}__${row.file.name}__${index}`}
                  data={row}
                  onCancel={() => cancelFile(row)}
                />
              ))}
          </div>
        )}
      </div>
    </>
  );
};

export default FileUploadQueue;

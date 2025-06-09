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

import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import FileIcon from '@cloudera/cuix-core/icons/react/DocumentationIcon';
import CloseIcon from '@cloudera/cuix-core/icons/react/CloseIcon';
import CaratDownIcon from '@cloudera/cuix-core/icons/react/CaratDownIcon';
import { BorderlessButton } from 'cuix/dist/components/Button';
import CaratUpIcon from '@cloudera/cuix-core/icons/react/CaratUpIcon';
import Modal from 'cuix/dist/components/Modal';

import { i18nReact } from '../../utils/i18nReact';
import { RegularFile, FileStatus } from '../../utils/hooks/useFileUpload/types';
import useFileUpload from '../../utils/hooks/useFileUpload/useFileUpload';
import { DEFAULT_ENABLE_CHUNK_UPLOAD } from '../../utils/constants/storageBrowser';
import { get } from '../../api/utils';
import { getLastKnownConfig } from '../../config/hueConfig';
import FileUploadRow from './FileUploadRow/FileUploadRow';
import { useHuePubSub } from '../../utils/hooks/useHuePubSub/useHuePubSub';
import huePubSub from '../../utils/huePubSub';
import { FILE_UPLOAD_START_EVENT, FILE_UPLOAD_SUCCESS_EVENT } from './event';
import { LIST_DIRECTORY_API_URL } from '../../apps/storageBrowser/api';
import { ListDirectory } from '../../apps/storageBrowser/types';

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
  const [conflictFiles, setConflictFiles] = useState<RegularFile[]>([]);
  const [isModalVisible, setIsModalVisible] = useState<boolean>(false);

  const fetchUploadedFiles = async (uploadPath: string) => {
    try {
      const response = await get<ListDirectory>(LIST_DIRECTORY_API_URL, {
        path: uploadPath,
        pagesize: '1000'
      });
      return response.files ?? []; // Return an empty array if no files are found
    } catch (error) {
      console.error('Failed to fetch files:', error);
    }
  };


  const onComplete = () => {
    huePubSub.publish(FILE_UPLOAD_SUCCESS_EVENT);
    const newlyUploadedFiles = uploadQueue.filter(file => file.status === FileStatus.Uploaded);
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
    callback: async (data?: FileUploadEvent) => {
      if ((data?.files ?? []).length > 0) {
        const uploadPath = data?.files?.[0]?.filePath ?? null;
        if (!uploadPath) {
          console.error('File path missing for uploaded files');
          return;
        }
        const uploadedFile = await fetchUploadedFiles(uploadPath);
        const { conflicts, nonConflictingFiles } = resolveFileConflicts(
          uploadedFile ?? [],
          data?.files ?? []
        );
        if (conflicts.length > 0) {
          setConflictFiles(conflicts);
          setIsModalVisible(true);
        } else {
         
          setConflictFiles([]);
          setIsModalVisible(false);
        }
        if (nonConflictingFiles.length > 0) {
          addFiles(nonConflictingFiles);
          setIsVisible(true);
        }
        setIsVisible(true);
      }
    }
  });

  const resolveFileConflicts = (uploadedFiles: any[], newFiles: RegularFile[]) => {
    const inProgressFileIdentifiers = new Set(
      uploadQueue
        .filter(file => file.status === FileStatus.Uploading || file.status === FileStatus.Pending)
        .map(file => `${file.filePath}/${file.file.name}`)
    );
  
    // Filter out files that are in progress in the upload queue
    const filteredNewFiles = newFiles.filter(
      newFile => !inProgressFileIdentifiers.has(`${newFile.filePath}/${newFile.file.name}`)
    );
  
    // Create a Set for existing uploaded file names for faster lookup
    const existingUploadedFilePaths = new Set(uploadedFiles.map(f => f.path));
  
    // Check for conflicts only with files that are already uploaded
    const conflicts = filteredNewFiles.filter(newFile =>
      existingUploadedFilePaths.has(`${newFile.filePath}/${newFile.file.name}`)
    );

    // Non-conflicting files to be added
    const nonConflictingFiles = filteredNewFiles.filter(
      newFile => !existingUploadedFilePaths.has(`${newFile.filePath}/${newFile.file.name}`)
    );  
    return { conflicts, nonConflictingFiles };
  };

  const onClose = () => {
    uploadQueue.forEach(file => cancelFile(file));
    setIsVisible(false);
  };

  const handleModalOk = (overwrite: boolean) => {
    if (overwrite) {
      addFiles(conflictFiles, true);
    }
    setConflictFiles([]);
    setIsModalVisible(false);
    setIsVisible(true);
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
      {isModalVisible && (
      <Modal
      title={t('Resolve Filename Conflicts')}
      open={isModalVisible}
      okText={t('Overwrite')}
      onOk={() => handleModalOk(true)}
      cancelText={t('Cancel')}
      onCancel={() => setIsModalVisible(false)}
      secondaryButtonText={t('Skip Upload')}
      onSecondary={() => handleModalOk(false)}
      className="hue-modal"
    >
      {t(
        `${conflictFiles.length} files you are trying to upload already exist in the uploaded files.`
      )}
      <div className="conflict-files__container">
        {conflictFiles.map(file => (
          <div key={file.file.name} className="conflict-files__item">
            <div className="file-icon">
              <FileIcon />
            </div>
            <span className="file-name">{file.file.name}</span>
          </div>
        ))}
      </div>
          </Modal>
        )}
      <div className="hue-upload-queue-container antd cuix">
        <div className="hue-upload-queue-container__header">
          {t(getHeaderText(), { pendingCount, uploadedCount, failedCount })}
          <div className="hue-upload-queue-container__header__button-group">
            <BorderlessButton
              onClick={() => setExpandQueue(!expandQueue)}
              icon={expandQueue ? <CaratDownIcon /> : <CaratUpIcon />}
            />
            <BorderlessButton onClick={onClose} icon={<CloseIcon />} />
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

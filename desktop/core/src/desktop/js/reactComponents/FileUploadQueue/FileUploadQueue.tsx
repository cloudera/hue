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
import { get } from '../../api/utils';
import Modal from 'cuix/dist/components/Modal';
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
import { LIST_DIRECTORY_API_URL } from '../../apps/storageBrowser/api';
import './FileUploadQueue.scss';
import { ListDirectory } from '../../apps/storageBrowser/types';
import FileIcon from '@cloudera/cuix-core/icons/react/DocumentationIcon';

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
  const [uploadedFiles, setUploadedFiles] = useState<RegularFile[]>([]);
  const [conflictFiles, setConflictFiles] = useState<RegularFile[]>([]);
  const [isModalVisible, setIsModalVisible] = useState<boolean>(false);
  const [path, setPath] = useState<string | null>(null);

  const fetchUploadedFiles = async (uploadPath: string) => {
    try {
      const response = await get<ListDirectory>(LIST_DIRECTORY_API_URL, {
        path: uploadPath,
        pagesize: '1000'
      });
      if (response?.files) {
        setUploadedFiles(
          response.files.map(file => ({
            uuid: crypto.randomUUID(),
            file: new File([''], file.path.split('/').pop() || ''),
            status: FileStatus.Uploaded,
            filePath: file.path
          }))
        );
      }
    } catch (error) {
      console.error('Failed to fetch files:', error);
    }
  };

  useEffect(() => {
    if (path) {
      fetchUploadedFiles(path);
    }
  }, [path]);

  useEffect(() => {
    // Automatically resolve file conflicts after uploadedFiles updates
    if (conflictFiles.length > 0) {
      resolveFileConflicts(conflictFiles);
    }
  }, [uploadedFiles]);

  const onComplete = () => {
    huePubSub.publish(FILE_UPLOAD_SUCCESS_EVENT);
    const newlyUploadedFiles = uploadQueue.filter(file => file.status === FileStatus.Uploaded);

    setUploadedFiles(existing => {
      const updatedFiles = [...existing, ...newlyUploadedFiles].filter(
        (file, index, self) => index === self.findIndex(f => f.file.name === file.file.name)
      );
      return updatedFiles;
    });
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

        setPath(uploadPath);

        await fetchUploadedFiles(uploadPath);

        setIsVisible(true);

        if (data?.files) {
          setConflictFiles(data.files); // Store new files temporarily
        }
      }
    }
  });

  const resolveFileConflicts = (newFiles: RegularFile[]) => {
    // Identify files currently in progress (Uploading or Pending) in the queue
    const inProgressFileIdentifiers = uploadQueue
      .filter(file => file.status === FileStatus.Uploading || file.status === FileStatus.Pending)
      .map(file => `${file.filePath}/${file.file.name}`);

    // Filter out files that are in progress in the upload queue
    const filteredNewFiles = newFiles.filter(
      newFile => !inProgressFileIdentifiers.includes(`${newFile.filePath}/${newFile.file.name}`)
    );

    // Check for conflicts only with files that are already uploaded
    const existingUploadedFileNames = uploadedFiles.map(f => f.file.name);
    const conflicts = filteredNewFiles.filter(newFile =>
      existingUploadedFileNames.includes(newFile.file.name)
    );

    // Non-conflicting files to be added
    const nonConflictingFiles = filteredNewFiles.filter(
      newFile => !existingUploadedFileNames.includes(newFile.file.name)
    );

    if (conflicts.length > 0) {
      setConflictFiles(conflicts);
      setIsModalVisible(true);
    } else {
      // Clear stale conflict state if no conflicts exist
      setConflictFiles([]);
      setIsModalVisible(false);
    }

    if (nonConflictingFiles.length > 0) {
      addFiles(nonConflictingFiles);
      setIsVisible(true);
    }
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
      {isModalVisible &&
        ReactDOM.createPortal(
          <Modal
            title={t('Resolve Filename Conflicts')}
            open={isModalVisible}
            okText={t('Overwrite')}
            onOk={() => handleModalOk(true)}
            cancelText={t('Cancel')}
            onCancel={() => setIsModalVisible(false)}
            secondaryButtonText={t('Keep Original')}
            onSecondary={() => handleModalOk(false)}
            style={{
              height: '50vh'
            }}
            bodyStyle={{
              display: 'flex',
              flexDirection: 'column',
              gap: '8px'
            }}
          >
            {t(
              `${conflictFiles.length} files you are trying to upload already exist in the uploaded files.`
            )}
            <div
              style={{
                marginTop: '8px',
                overflowY: 'auto',
                maxHeight: 'calc(50vh - 100px)',
                borderTop: '1px solid #e9e9e9',
                paddingTop: '8px'
              }}
            >
              {conflictFiles.map(file => (
                <div
                  key={file.file.name}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  <div
                    style={{
                      flexShrink: 0, // Prevent icon from shrinking
                      width: '20px', // Set icon's width
                      height: '20px' // Set icon's height
                    }}
                  >
                    <FileIcon style={{ width: '100%', height: '100%' }} />
                  </div>
                  <span
                    style={{
                      wordBreak: 'break-word', // Allow long names to wrap
                      maxWidth: 'calc(100% - 28px)' // Ensure the name takes the remaining space
                    }}
                  >
                    {file.file.name}
                  </span>
                </div>
              ))}
            </div>
          </Modal>,
          document.body
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

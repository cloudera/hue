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

import React, { useRef } from 'react';
import DocumentationIcon from '@cloudera/cuix-core/icons/react/DocumentationIcon';
import Button from 'cuix/dist/components/Button';

import { FileMetaData, ImporterFileSource, LocalFileUploadResponse } from '../types';
import { UPLOAD_LOCAL_FILE_API_URL } from '../api';
import useSaveData from '../../../utils/hooks/useSaveData/useSaveData';
import { i18nReact } from '../../../utils/i18nReact';
import { SUPPORTED_UPLOAD_TYPES, DEFAULT_UPLOAD_LIMIT } from '../constants';
import { getLastKnownConfig } from '../../../config/hueConfig';

interface LocalFileUploadOptionProps {
  setFileMetaData: (fileMetaData: FileMetaData) => void;
  setUploadError: (error: string) => void;
}

const LocalFileUploadOption = ({
  setFileMetaData,
  setUploadError
}: LocalFileUploadOptionProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const uploadRef = useRef<HTMLInputElement>(null);
  const config = getLastKnownConfig()?.importer;

  const { save: upload } = useSaveData<LocalFileUploadResponse>(UPLOAD_LOCAL_FILE_API_URL);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) {
      return;
    }

    const file = files[0];

    const payload = new FormData();
    payload.append('file', file);

    const fileSize = file.size;
    if (fileSize === 0) {
      setUploadError(t('This file is empty, please select another file.'));
    } else if (fileSize > (config?.max_local_file_size_upload_limit ?? DEFAULT_UPLOAD_LIMIT)) {
      setUploadError(
        t('File size exceeds the supported size. Please use any file browser to upload files.')
      );
    } else {
      upload(payload, {
        onSuccess: data => {
          setFileMetaData({
            path: data.filePath,
            fileName: file.name,
            source: ImporterFileSource.LOCAL
          });
        },
        onError: error => {
          setUploadError(error.message);
        }
      });
    }
  };

  //TODO: Add loader or extend fileUploadQueue to accept local file upload
  return (
    <div className="hue-importer__source-selector-option">
      <Button
        className="hue-importer__source-selector-option-button"
        size="large"
        icon={<DocumentationIcon />}
        onClick={() => uploadRef?.current?.click()}
      />
      <span className="hue-importer__source-selector-option-btn-title">
        {t('Upload from File')}
      </span>
      <input
        ref={uploadRef}
        type="file"
        data-testid="hue-file-input"
        className="hue-importer__source-selector-option-upload"
        onChange={handleFileUpload}
        accept={SUPPORTED_UPLOAD_TYPES}
      />
    </div>
  );
};

export default LocalFileUploadOption;

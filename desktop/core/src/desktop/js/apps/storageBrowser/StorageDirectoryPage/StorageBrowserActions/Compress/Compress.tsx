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
import { i18nReact } from '../../../../../utils/i18nReact';
import useSaveData from '../../../../../utils/hooks/useSaveData';
import { StorageDirectoryTableData } from '../../../../../reactComponents/FileChooser/types';
import { COMPRESS_API_URL } from '../../../../../reactComponents/FileChooser/api';
import { Input } from 'antd';

import './Compress.scss';

interface CompressActionProps {
  currentPath: string;
  isOpen?: boolean;
  files: StorageDirectoryTableData[];
  setLoading: (value: boolean) => void;
  onSuccess: () => void;
  onError: (error: Error) => void;
  onClose: () => void;
}

const CompressAction = ({
  currentPath,
  isOpen = true,
  files,
  setLoading,
  onSuccess,
  onError,
  onClose
}: CompressActionProps): JSX.Element => {
  const initialName = currentPath.split('/').pop() + '.zip';
  const [value, setValue] = useState<string>(initialName);
  const { t } = i18nReact.useTranslation();

  const { save: saveForm, loading } = useSaveData(undefined, {
    postOptions: {
      qsEncodeData: false,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    },
    skip: !files.length,
    onSuccess,
    onError
  });

  const handleCompress = () => {
    setLoading(true);

    const formData = new FormData();
    files.forEach(selectedFile => {
      formData.append('file_name', selectedFile.name);
    });
    formData.append('upload_path', currentPath);
    formData.append('archive_name', value);

    saveForm(formData, { url: COMPRESS_API_URL });
  };

  return (
    <Modal
      cancelText={t('Cancel')}
      className="cuix antd"
      okText={t('Compress')}
      onCancel={onClose}
      onOk={() => handleCompress()}
      open={isOpen}
      title={t('Compress files and folders')}
      okButtonProps={{ disabled: loading }}
      cancelButtonProps={{ disabled: loading }}
    >
      {t('Compressed file name')}
      <Input
        value={value}
        type="text"
        onPressEnter={() => handleCompress()}
        onChange={e => {
          setValue(e.target.value);
        }}
      />

      <div className="compress-action">
        {t('Following files and folders will be compressed:')}
        <ul className="compress-action__list">
          {files.map(file => (
            <li key={file.path}>{file.name}</li>
          ))}
        </ul>
      </div>
    </Modal>
  );
};

export default CompressAction;

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
import Modal from 'cuix/dist/components/Modal';
import { i18nReact } from '../../../../../../utils/i18nReact';
import useSaveData from '../../../../../../utils/hooks/useSaveData/useSaveData';
import { StorageDirectoryTableData } from '../../../../types';
import { EXTRACT_API_URL } from '../../../../api';
import LoadingErrorWrapper from '../../../../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';

interface ExtractActionProps {
  currentPath: string;
  isOpen?: boolean;
  file: StorageDirectoryTableData;
  onSuccess: () => void;
  onError: (error: Error) => void;
  onClose: () => void;
}

const ExtractionModal = ({
  currentPath,
  isOpen = true,
  file,
  onSuccess,
  onError,
  onClose
}: ExtractActionProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const { save, loading, error } = useSaveData(EXTRACT_API_URL, {
    // TODO: Remove qsEncodeData once API supports RAW JSON payload
    options: { qsEncodeData: true },
    skip: !file,
    onSuccess,
    onError
  });

  const handleExtract = () => {
    save({
      upload_path: currentPath,
      archive_name: file.name
    });
  };

  const errors = [
    {
      enabled: !!error,
      message: error
    }
  ];

  return (
    <Modal
      cancelText={t('Cancel')}
      className="cuix antd"
      okText={t('Extract')}
      onCancel={onClose}
      onOk={handleExtract}
      open={isOpen}
      title={t('Extract Archive')}
      okButtonProps={{ disabled: !!error, loading }}
      cancelButtonProps={{ disabled: loading }}
      closable={!loading}
    >
      <LoadingErrorWrapper errors={errors}>
        {t('Are you sure you want to extract "{{fileName}}" file?', { fileName: file.name })}
      </LoadingErrorWrapper>
    </Modal>
  );
};

export default ExtractionModal;

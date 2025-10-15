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
import Input from 'cuix/dist/components/Input';
import PrimaryButton from 'cuix/dist/components/Button/PrimaryButton';
import { i18nReact } from '../../../utils/i18nReact';
import FileChooserModal from '../../../apps/storageBrowser/FileChooserModal/FileChooserModal';
import './FileChooserInput.scss';

export interface FileChooserInputProps {
  value?: string;
  onChange: (value: string) => void;
  placeholder?: string;
  error?: boolean;
  name?: string;
}

const FileChooserInput: React.FC<FileChooserInputProps> = ({
  value,
  onChange,
  placeholder,
  error,
  name
}) => {
  const { t } = i18nReact.useTranslation();
  const [showModal, setShowModal] = useState(false);
  const [selectedPath, setSelectedPath] = useState(value);

  const handleFileChoose = async (selectedPath: string) => {
    onChange(selectedPath);
    setSelectedPath(selectedPath);
    setShowModal(false);
  };

  return (
    <>
      <div className="hue-form-input__file-chooser">
        <Input
          value={selectedPath}
          onChange={e => onChange(e.target.value)}
          placeholder={placeholder ? t(placeholder) : undefined}
          status={error ? 'error' : undefined}
          name={name}
        />
        <PrimaryButton
          onClick={() => setShowModal(true)}
          className="hue-form-input__file-chooser__button"
        >
          {t('Choose')}
        </PrimaryButton>
      </div>
      {showModal && (
        <FileChooserModal
          showModal={showModal}
          onClose={() => setShowModal(false)}
          onSubmit={handleFileChoose}
          title={t('Choose a file')}
          sourcePath={selectedPath || '/'}
          isFileSelectionAllowed={true}
          submitText={t('Select')}
          cancelText={t('Cancel')}
        />
      )}
    </>
  );
};

export default FileChooserInput;

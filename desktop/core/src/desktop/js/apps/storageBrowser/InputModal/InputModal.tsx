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
import { Input } from 'antd';

import { i18nReact } from '../../../utils/i18nReact';

import './InputModal.scss';

//TODO: Add unit tests
interface InputModalProps {
  cancelText?: string;
  inputLabel: string;
  submitText?: string;
  onClose: () => void;
  onSubmit: (value: string) => void;
  showModal: boolean;
  title: string;
}

const InputModal: React.FC<InputModalProps> = ({
  inputLabel,
  onClose,
  onSubmit,
  showModal,
  title,
  ...i18n
}): JSX.Element => {
  const [value, setValue] = useState<string>('');
  const { t } = i18nReact.useTranslation();
  const { cancelText = t('Close'), submitText = t('Submit') } = i18n;

  return (
    <Modal
      cancelText={cancelText}
      className="hue-input-modal"
      okText={submitText}
      onCancel={() => {
        setValue('');
        onClose();
      }}
      onOk={() => {
        onSubmit(value);
        setValue('');
        onClose();
      }}
      open={showModal}
      title={title}
    >
      <div className="hue-input-modal__input-label">{inputLabel}</div>
      <Input
        className="hue-input-modal__input"
        value={value}
        onInput={e => {
          setValue((e.target as HTMLInputElement).value);
        }}
      />
    </Modal>
  );
};

export default InputModal;

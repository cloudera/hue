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

type InputValueType = string | number;
//TODO: Add unit tests
interface InputModalProps<T> {
  cancelText?: string;
  inputLabel: string;
  submitText?: string;
  onClose: () => void;
  onSubmit: <T>(value: T) => void;
  showModal: boolean;
  title: string;
  inputType: 'number' | 'text';
  initialInputValue: T;
}

const InputModal = <T,>({
  inputLabel,
  onClose,
  onSubmit,
  showModal,
  title,
  inputType,
  initialInputValue,
  ...i18n
}: InputModalProps<T>): JSX.Element => {
  const [value, setValue] = useState<T>(initialInputValue);
  const { t } = i18nReact.useTranslation();
  const { cancelText = t('Cancel'), submitText = t('Submit') } = i18n;

  return (
    <Modal
      cancelText={cancelText}
      className="hue-input-modal cuix antd"
      okText={submitText}
      onCancel={() => {
        setValue(initialInputValue);
        onClose();
      }}
      onOk={() => {
        onSubmit(value);
        setValue(initialInputValue);
        onClose();
      }}
      open={showModal}
      title={title}
    >
      <div className="hue-input-modal__input-label">{inputLabel}</div>
      <Input
        className="hue-input-modal__input"
        value={value}
        type={inputType}
        onInput={e => {
          setValue((e.target as HTMLInputElement).value);
        }}
      />
    </Modal>
  );
};

export default InputModal;

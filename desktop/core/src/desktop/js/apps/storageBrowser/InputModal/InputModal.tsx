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
import Modal from 'cuix/dist/components/Modal';
import { Input, InputRef } from 'antd';
import { i18nReact } from '../../../utils/i18nReact';

import './InputModal.scss';

interface InputModalProps {
  cancelText?: string;
  description: string;
  inputLabel: string;
  inputPlaceholder?: string;
  okText?: string;
  onCancel: () => void;
  onOk: (name: string) => void;
  showModal: boolean;
  title: string;
}

const defaultProps = {
  cancelText: 'Cancel',
  inputPlaceholder: 'Enter text here',
  okText: 'Submit'
};

const InputModal: React.FC<InputModalProps> = ({
  cancelText,
  description,
  inputLabel,
  inputPlaceholder,
  okText,
  onCancel,
  onOk,
  showModal,
  title
}): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const textInput = useRef<InputRef>(null);

  const extractText = (): string => {
    let nameText: string;
    if (textInput.current !== null) {
      nameText = textInput.current.input.value;
    }
    return nameText;
  };

  return (
    <Modal
      cancelText={t(cancelText)}
      className="hue-input-modal"
      okText={t(okText)}
      onCancel={onCancel}
      onOk={() => onOk(extractText())}
      open={showModal}
      title={t(title)}
    >
      <div className="hue-input-modal__description">{t(description)}</div>
      <div className="hue-input-modal__input-label">{t(inputLabel)}</div>
      <Input className="hue-input-modal__input" ref={textInput} placeholder={t(inputPlaceholder)} />
    </Modal>
  );
};

InputModal.defaultProps = defaultProps;
export default InputModal;

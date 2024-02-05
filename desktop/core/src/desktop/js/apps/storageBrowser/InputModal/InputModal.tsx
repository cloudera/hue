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

interface InputModalProps {
  cancelText?: string;
  inputLabel: string;
  okText?: string;
  onClose: () => void;
  onCreate: (name: string) => void;
  showModal: boolean;
  title: string;
}

const defaultProps = {
  cancelText: 'Cancel',
  okText: 'Submit'
};

const InputModal: React.FC<InputModalProps> = ({
  cancelText,
  inputLabel,
  okText,
  onClose,
  onCreate,
  showModal,
  title
}): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [textInput, setTextInput] = useState<string>('');

  return (
    <Modal
      cancelText={t(cancelText)}
      className="hue-input-modal"
      okText={t(okText)}
      onCancel={() => {
        setTextInput('');
        onClose();
      }}
      onOk={() => {
        onCreate(textInput);
        setTextInput('');
        onClose();
      }}
      open={showModal}
      title={t(title)}
    >
      <div className="hue-input-modal__input-label">{t(inputLabel)}</div>
      <Input
        className="hue-input-modal__input"
        value={textInput}
        onInput={e => {
          setTextInput((e.target as HTMLInputElement).value);
        }}
      />
    </Modal>
  );
};

InputModal.defaultProps = defaultProps;
export default InputModal;

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

import { i18nReact } from '../../../utils/i18nReact';

import './ConfirmationModal.scss';

interface ConfirmationModalProps {
  onClose: () => void;
  onSubmit: () => void;
  showModal: boolean;
  title: string;
  modalBody: JSX.Element;
  okText: string;
  cancelText: string;
}

const ConfirmationModal = ({
  modalBody,
  onClose,
  onSubmit,
  showModal,
  title,
  okText,
  cancelText
}: ConfirmationModalProps): JSX.Element => {
  // const { t } = i18nReact.useTranslation();

  return (
    <Modal
      cancelText={cancelText}
      className="hue-confirmation-modal cuix antd"
      okText={okText}
      open={showModal}
      title={title}
      onCancel={() => onClose()}
      onOk={() => {
        onSubmit();
        onClose();
      }}
      okButtonProps={{ style: { backgroundColor: 'red' } }}
    >
      <div className="hue-confirmation-modal__body">{modalBody}</div>
    </Modal>
  );
};

export default ConfirmationModal;

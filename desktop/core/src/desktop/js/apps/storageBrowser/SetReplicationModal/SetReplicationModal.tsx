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
// limitations under the License.
import React, { useState } from 'react';
import Modal from 'cuix/dist/components/Modal';
import { Input } from 'antd';

import { i18nReact } from '../../../utils/i18nReact';

import './SetReplicationModal.scss';

interface SetReplicationModalProps {
  onClose: () => void;
  onSubmit: (value: number) => void;
  showModal: boolean;
  title: string;
  currentReplicationFactor: number;
}

const SetReplicationModal = ({
  showModal,
  onClose,
  onSubmit,
  title,
  currentReplicationFactor
}: SetReplicationModalProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [value, setValue] = useState<number>(currentReplicationFactor);

  return (
    <Modal
      cancelText={t('Cancel')}
      className="hue-set-replication-modal cuix antd"
      okText={t('Submit')}
      title={title}
      open={showModal}
      onCancel={() => {
        onClose();
      }}
      onOk={() => {
        onSubmit(value);
        onClose();
      }}
      destroyOnClose
    >
      <div className="hue-replication-modal__input-label">Replication factor: </div>
      <Input
        className="hue-replication-modal__input"
        value={value}
        type="number"
        onChange={e => {
          setValue(Number(e.target.value));
        }}
      />
    </Modal>
  );
};

export default SetReplicationModal;

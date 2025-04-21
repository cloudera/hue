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
import { i18nReact } from '../../../../utils/i18nReact';
import Button from 'cuix/dist/components/Button';
import Modal from 'cuix/dist/components/Modal';
import './ColumnModal.scss';

interface ColumnModalTableProps {
  isOpen: boolean;
  closeModal: () => void;
}

const ColumnModalTable = ({ isOpen, closeModal }: ColumnModalTableProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  return (
    <Modal
      title={t('Edit Column')}
      open={isOpen}
      onCancel={closeModal}
      footer={[
        <Button key="back" onClick={closeModal}>
          {t('Cancel')}
        </Button>,
        <Button key="submit" onClick={closeModal}>
          {t('Done')}
        </Button>
      ]}
    ></Modal>
  );
};

export default ColumnModalTable;

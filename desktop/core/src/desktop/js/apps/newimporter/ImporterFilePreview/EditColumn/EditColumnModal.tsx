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
import Modal from 'cuix/dist/components/Modal';
import './EditColumn.scss';

interface EditColumnModalProps {
  isOpen: boolean;
  closeModal: () => void;
}

const EditColumnModal = ({ isOpen, closeModal }: EditColumnModalProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  return (
    <Modal
      cancelText={t('Cancel')}
      okText={t('Done')}
      title={t('Edit Column')}
      open={isOpen}
      onCancel={closeModal}
    />
  );
};

export default EditColumnModal;

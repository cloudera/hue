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

import React, { useState, useEffect } from 'react';
import Modal from 'cuix/dist/components/Modal';
import { Form } from 'antd';
import { i18nReact } from '../../../../utils/i18nReact';
import { FileMetaData, ImporterFileSource } from '../../types';
import {
  ADVANCED_SETTINGS_CONFIG,
  StoreLocation,
  TableFormat,
  VisibilityContext
} from './advancedSettingsConfig';
import FormFieldRenderer from './FormFieldRenderer';

import './AdvancedSettingsModal.scss';

interface AdvancedSettingsModalProps {
  isOpen: boolean;
  closeModal: () => void;
  fileMetaData: FileMetaData;
  // fileFormat?: FileFormat;
  advancedSettings: AdvancedSettings;
  onSettingsChange: (settings: AdvancedSettings) => void;
}

export interface AdvancedSettings {
  storeLocation: StoreLocation;
  isTransactional: boolean;
  isInsertOnly: boolean;
  externalLocation: string;
  importData: boolean;
  isIcebergTable: boolean;
  isCopyFile: boolean;
  description: string;
  tableFormat: string;
  primaryKeys: string[];
}

const AdvancedSettingsModal: React.FC<AdvancedSettingsModalProps> = ({
  isOpen,
  closeModal,
  fileMetaData,
  // fileFormat,
  advancedSettings,
  onSettingsChange
}) => {
  const { t } = i18nReact.useTranslation();
  const [localSettings, setLocalSettings] = useState<AdvancedSettings>(advancedSettings);

  useEffect(() => {
    setLocalSettings(advancedSettings);
  }, [advancedSettings]);

  const handleChange = (fieldId: string, value: string | boolean | string[]) => {
    setLocalSettings(prev => ({
      ...prev,
      [fieldId]: value
    }));
  };

  const handleOk = () => {
    onSettingsChange(localSettings);
    closeModal();
  };

  const handleCancel = () => {
    setLocalSettings(advancedSettings);
    closeModal();
  };

  // Create visibility context
  const tableFormat = localSettings.tableFormat || TableFormat.TEXT;
  const context: VisibilityContext = {
    isManagedTable: localSettings.storeLocation === StoreLocation.MANAGED,
    isRemoteTable: fileMetaData.source === ImporterFileSource.REMOTE,
    isKuduTable: tableFormat === TableFormat.KUDU,
    isIcebergEnabled: true, // TODO: Get from config
    isCopyFile: localSettings.isCopyFile,
    isIcebergTable: localSettings.isIcebergTable,
    fileMetaData,
    settings: localSettings,
    // tableFormat,
    isTransactionalVisible:
      tableFormat !== TableFormat.KUDU && fileMetaData.source !== ImporterFileSource.LOCAL,
    isTransactionalUpdateEnabled: localSettings.isTransactional && !localSettings.isInsertOnly
  };

  return (
    <Modal
      title={t('Advanced Settings')}
      open={isOpen}
      onOk={handleOk}
      onCancel={handleCancel}
      width={600}
      okText={t('Apply')}
      cancelText={t('Cancel')}
      className="importer-advanced-settings-modal"
    >
      <Form layout="vertical">
        {ADVANCED_SETTINGS_CONFIG.map(field => (
          <FormFieldRenderer
            key={field.id}
            field={field}
            context={context}
            value={localSettings[field.id as keyof AdvancedSettings]}
            onChange={handleChange}
          />
        ))}
      </Form>
    </Modal>
  );
};

export default AdvancedSettingsModal;

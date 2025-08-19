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
import { Form } from 'antd';

import { FileMetaData, ImporterFileSource, ImporterSettings, SettingsContext } from '../types';
import { ADVANCED_SETTINGS_CONFIG, SettingsFieldConfig } from './SettingsTabConfig';
import FormInput from '../../../reactComponents/FormInput/FormInput';
import { i18nReact } from '../../../utils/i18nReact';

import './SettingsTab.scss';

interface SettingsTabProps {
  fileMetaData: FileMetaData;
  settings: ImporterSettings;
  onSettingsChange: (settings: ImporterSettings) => void;
}

const SettingsTab = ({
  fileMetaData,
  settings,
  onSettingsChange
}: SettingsTabProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const handleChange = (fieldId: string, value: string | boolean | string[]) => {
    onSettingsChange({
      ...settings,
      [fieldId]: value
    });
  };

  // Create visibility context
  const context: SettingsContext = {
    ...settings,
    isRemoteTable: fileMetaData.source === ImporterFileSource.REMOTE,
    isIcebergEnabled: true // TODO: Get from config
  };

  const renderSection = (fields: SettingsFieldConfig[], title?: string, isSingleRow?: boolean) => (
    <div className="hue-importer-settings-tab__section">
      {title && <div className="hue-importer-settings-tab__section__title">{title}</div>}
      <div
        className={`${isSingleRow ? 'hue-importer-settings-tab__section__single-row' : 'hue-importer-settings-tab__section__fields'}`}
      >
        {fields
          .filter(field => !field.isHidden?.(context))
          .map(field => (
            <FormInput<string> key={field.name} field={field} onChange={handleChange} />
          ))}
      </div>
    </div>
  );

  return (
    <div className="hue-importer-settings-tab">
      <Form layout="vertical" className="hue-importer-settings-tab__form">
        {renderSection(ADVANCED_SETTINGS_CONFIG.description)}
        {renderSection(ADVANCED_SETTINGS_CONFIG.properties, t('Properties'))}
        <div>
          {renderSection(ADVANCED_SETTINGS_CONFIG.characterDelimiters, t('Character Delimiters'))}
          {renderSection(ADVANCED_SETTINGS_CONFIG.delimiters, undefined, true)}
        </div>
      </Form>
    </div>
  );
};

export default SettingsTab;

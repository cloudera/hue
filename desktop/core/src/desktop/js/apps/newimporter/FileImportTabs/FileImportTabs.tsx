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
import { Tabs } from 'antd';
import { i18nReact } from '../../../utils/i18nReact';
import { DestinationConfig, FileMetaData, Partition } from '../types';

import './FileImportTabs.scss';
import FilePreviewTab from '../FilePreviewTab/FilePreviewTab';
import BorderlessButton from 'cuix/dist/components/Button/BorderlessButton';
import { PrimaryButton } from 'cuix/dist/components/Button';
import useSaveData from '../../../utils/hooks/useSaveData/useSaveData';
import { FINISH_IMPORT_URL } from '../api';
import { getDefaultTableName } from '../utils/utils';
import SettingsTab from '../SettingsTab/SettingsTab';
import PartitionsTab from '../PartitionsTab/PartitionsTab';
import { ImporterSettings, StoreLocation, TableFormat } from '../types';

interface FileImportTabsProps {
  fileMetaData: FileMetaData;
}

const FileImportTabs = ({ fileMetaData }: FileImportTabsProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const [destinationConfig, setDestinationConfig] = useState<DestinationConfig>({
    tableName: getDefaultTableName(fileMetaData)
  });
  const [settings, setSettings] = useState<ImporterSettings>({
    storeLocation: StoreLocation.MANAGED,
    isTransactional: false,
    isInsertOnly: false,
    externalLocation: '',
    importData: true,
    isIcebergTable: false,
    isCopyFile: false,
    description: '',
    tableFormat: TableFormat.TEXT,
    primaryKeys: [],
    createEmptyTable: false,
    useExternalLocation: false,
    customCharDelimiters: false,
    fieldDelimiter: '',
    arrayMapDelimiter: '',
    structDelimiter: ''
  });
  const [partitions, setPartitions] = useState<Partition[]>([]);

  const handleDestinationConfigChange = (name: string, value: string) => {
    setDestinationConfig(prevConfig => ({
      ...prevConfig,
      [name]: value
    }));
  };

  const { save: finishImport, loading: finalizingImport } = useSaveData(FINISH_IMPORT_URL);

  const handleFinishImport = () => {
    const source = {
      inputFormat: fileMetaData.source,
      path: fileMetaData.path,
      // format: fileFormat,
      sourceType: destinationConfig.connectorId
    };
    const destination = {
      outputFormat: 'table',
      nonDefaultLocation: fileMetaData.path,
      name: `${destinationConfig.database}.${destinationConfig.tableName}`,
      sourceType: destinationConfig.connectorId
      // columns: previewData?.columns
    };

    const formData = new FormData();
    formData.append('source', JSON.stringify(source));
    formData.append('destination', JSON.stringify(destination));

    finishImport(formData);
  };

  const tabItems = [
    {
      label: t('Preview'),
      key: 'preview',
      children: (
        <FilePreviewTab
          fileMetaData={fileMetaData}
          destinationConfig={destinationConfig}
          onDestinationConfigChange={handleDestinationConfigChange}
        />
      )
    },
    {
      label: t('Settings'),
      key: 'settings',
      children: (
        <SettingsTab
          fileMetaData={fileMetaData}
          settings={settings}
          onSettingsChange={setSettings}
        />
      )
    },
    {
      label: t('Partitions'),
      key: 'partition',
      children: <PartitionsTab partitions={partitions} onPartitionsChange={setPartitions} />
    }
  ];

  return (
    <div className="hue-file-import-tabs">
      <div className="hue-file-import-tabs__header">
        <div className="hue-file-import-tabs__header__title">{fileMetaData?.fileName}</div>
        <div className="hue-file-import-tabs__header__actions">
          <BorderlessButton data-testid="hue-importer-preview-page__header__actions__cancel">
            {t('Cancel')}
          </BorderlessButton>
          <PrimaryButton loading={finalizingImport} onClick={handleFinishImport}>
            {t('Finish Import')}
          </PrimaryButton>
        </div>
      </div>
      <Tabs items={tabItems} className="hue-file-import-tabs__tabs" />
    </div>
  );
};

export default FileImportTabs;

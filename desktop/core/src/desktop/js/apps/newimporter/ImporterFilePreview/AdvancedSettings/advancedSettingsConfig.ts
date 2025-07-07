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

import { FileMetaData } from '../../types';
import { AdvancedSettings } from './AdvancedSettingsModal';

export type FieldType = 'checkbox' | 'input' | 'select' | 'radio';

export interface FieldOption {
  value: string;
  label: string;
}

export interface FieldConfig {
  id: string;
  type: FieldType;
  label?: string;
  placeholder?: string;
  tooltip?: string;
  options?: FieldOption[];
  isHidden?: (context: VisibilityContext) => boolean;
  style?: React.CSSProperties;
  nested?: boolean;
  parentField?: string;
}

export interface VisibilityContext {
  isManagedTable: boolean;
  isRemoteTable: boolean;
  isKuduTable: boolean;
  fileMetaData: FileMetaData;
  settings: AdvancedSettings;
  isIcebergEnabled: boolean;
  isIcebergTable: boolean;
  isTransactionalVisible: boolean;
  isTransactionalUpdateEnabled: boolean;
  isCopyFile: boolean;
}

export enum TableFormat {
  TEXT = 'text',
  PARQUET = 'parquet',
  AVRO = 'avro',
  ORC = 'orc',
  JSON = 'json',
  KUDU = 'kudu',
  CSV = 'csv'
}

export enum StoreLocation {
  MANAGED = 'managed',
  EXTERNAL = 'external'
}

export const TABLE_FORMAT_OPTIONS: FieldOption[] = [
  { value: TableFormat.TEXT, label: 'Text' },
  { value: TableFormat.PARQUET, label: 'Parquet' },
  { value: TableFormat.AVRO, label: 'Avro' },
  { value: TableFormat.ORC, label: 'ORC' },
  { value: TableFormat.JSON, label: 'JSON' },
  { value: TableFormat.KUDU, label: 'Kudu' },
  { value: TableFormat.CSV, label: 'CSV' }
];

export const ADVANCED_SETTINGS_CONFIG: FieldConfig[] = [
  {
    id: 'description',
    type: 'input',
    label: 'Description',
    placeholder: 'Enter table description'
  },
  {
    id: 'tableFormat',
    type: 'select',
    label: 'Format',
    options: TABLE_FORMAT_OPTIONS
  },
  {
    id: 'importData',
    type: 'checkbox',
    label: 'Create empty table',
    tooltip: 'This will only create the table and not import any data'
  },
  {
    id: 'storeLocation',
    type: 'radio',
    label: 'Store in',
    options: [
      { value: StoreLocation.MANAGED, label: 'Default location' },
      { value: StoreLocation.EXTERNAL, label: 'External location' }
    ],
    isHidden: ({ isKuduTable, isIcebergTable, isCopyFile }) =>
      isKuduTable || isIcebergTable || isCopyFile
  },
  {
    id: 'externalLocation',
    type: 'input',
    label: 'External location',
    placeholder: 'External location',
    isHidden: ({ settings }) => settings.storeLocation !== 'external'
  },
  {
    id: 'isTransactional',
    type: 'checkbox',
    label: 'Transactional table',
    isHidden: ({ isKuduTable, isRemoteTable, isIcebergTable, isCopyFile }) =>
      isKuduTable || isRemoteTable || isIcebergTable || isCopyFile
  },
  {
    id: 'isInsertOnly',
    type: 'checkbox',
    label: 'Insert only',
    tooltip: 'Full transactional support available in Hive with ORC',
    parentField: 'isTransactional',
    isHidden: ({ settings }) => !settings.isTransactional
  },

  {
    id: 'isIcebergTable',
    type: 'checkbox',
    label: 'Iceberg table',
    isHidden: ({ isIcebergEnabled, isRemoteTable }) => !isIcebergEnabled || !isRemoteTable
  },
  {
    id: 'isCopyFile',
    type: 'checkbox',
    label: 'Copy file',
    tooltip:
      'Choosing this option will copy the file instead of moving it to the new location, and ensuring the original file remains unchanged.',
    isHidden: ({ settings, isRemoteTable, isManagedTable }) =>
      isManagedTable || settings.isTransactional || !isRemoteTable || settings.importData === false
  }
];

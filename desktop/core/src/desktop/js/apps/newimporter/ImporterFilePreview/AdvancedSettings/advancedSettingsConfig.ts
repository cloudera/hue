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

export type FieldType = 'checkbox' | 'input' | 'select';

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
  fileMetaData: any;
  fileFormat: any;
  settings: any;
  tableFormat: string;
  isKudu: boolean;
  isIcebergEnabled: boolean;
  isTransactionalVisible: boolean;
  isTransactionalUpdateEnabled: boolean;
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
    id: 'useDefaultLocation',
    type: 'checkbox',
    label: 'Store in Default location'
    // isHidden: ({ isKudu, settings }) => isKudu || settings.isIceberg || settings.useCopy
  },
  {
    id: 'nonDefaultLocation',
    type: 'input',
    label: 'External location',
    placeholder: 'Enter external location path',
    isHidden: ({ settings }) => settings.useDefaultLocation
  },
  {
    id: 'isTransactional',
    type: 'checkbox',
    label: 'Transactional table'
    // isHidden: ({ isTransactionalVisible, settings }) =>
    // !isTransactionalVisible || settings.isIceberg || settings.useCopy
  },
  {
    id: 'isInsertOnly',
    type: 'checkbox',
    label: 'Insert only',
    tooltip: 'Full transactional support available in Hive with ORC',
    parentField: 'isTransactional',
    isHidden: ({ settings }) => !settings.isTransactional
    // isHidden: ({ isTransactionalVisible, isTransactionalUpdateEnabled }) =>
    // !isTransactionalVisible || !isTransactionalUpdateEnabled
  },

  {
    id: 'isIceberg',
    type: 'checkbox',
    label: 'Iceberg table'
    // isHidden: ({ isIcebergEnabled, fileMetaData }) =>
    // !isIcebergEnabled || fileMetaData.source !== ImporterFileSource.REMOTE
  },
  {
    id: 'useCopy',
    type: 'checkbox',
    label: 'Copy file',
    tooltip:
      'Choosing this option will copy the file instead of moving it to the new location, and ensuring the original file remains unchanged.'
    // isHidden: ({ settings, fileMetaData }) =>
    // settings.useDefaultLocation ||
    // settings.isTransactional ||
    // fileMetaData.source !== ImporterFileSource.REMOTE
  }
];

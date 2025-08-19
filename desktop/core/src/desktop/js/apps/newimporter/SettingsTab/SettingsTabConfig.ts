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

import { FieldConfig, FieldOption, FieldType } from '../../../reactComponents/FormInput/FormInput';
import { SettingsContext, StoreLocation, TableFormat } from '../types';

export const TABLE_FORMAT_OPTIONS: FieldOption[] = [
  { value: TableFormat.TEXT, label: 'Text' },
  { value: TableFormat.PARQUET, label: 'Parquet' },
  { value: TableFormat.AVRO, label: 'Avro' },
  { value: TableFormat.ORC, label: 'ORC' },
  { value: TableFormat.JSON, label: 'JSON' },
  { value: TableFormat.KUDU, label: 'Kudu' },
  { value: TableFormat.CSV, label: 'CSV' }
];

export const DELIMITER_OPTIONS: FieldOption[] = [
  { value: 'new_line', label: 'New line' },
  { value: 'comma', label: 'Comma' },
  { value: 'tab', label: 'Tab' },
  { value: 'semicolon', label: 'Semicolon' },
  { value: 'pipe', label: 'Pipe' },
  { value: 'custom', label: 'Custom' }
];

export const EXTERNAL_LOCATION_OPTIONS: FieldOption[] = [
  { value: 'hdfs', label: 'HDFS' },
  { value: 's3', label: 'S3' },
  { value: 'abfs', label: 'ABFS' },
  { value: 'custom', label: 'Custom' }
];

export interface SettingsFieldConfig extends FieldConfig {
  isHidden?: (context: SettingsContext) => boolean;
}

export const ADVANCED_SETTINGS_CONFIG: Record<string, SettingsFieldConfig[]> = {
  description: [
    {
      name: 'description',
      type: FieldType.INPUT,
      label: 'Description',
      placeholder: "A table to store customer data imported from the marketing team's CRM.",
      tooltip:
        "This description will be used as the comment for the new database table. It helps other developers understand the table's purpose."
    }
  ],
  properties: [
    {
      name: 'tableFormat',
      type: FieldType.SELECT,
      label: 'Format',
      placeholder: 'Choose an option',
      options: TABLE_FORMAT_OPTIONS,
      tooltip: 'Format of the table'
    },
    {
      name: 'createEmptyTable',
      type: FieldType.CHECKBOX,
      label: 'Create empty table',
      tooltip: 'This will only create the table and not import any data'
    },
    {
      name: 'isTransactional',
      type: FieldType.CHECKBOX,
      label: 'Transactional table',
      tooltip: 'Transactional table',
      isHidden: (context: SettingsContext) =>
        context.tableFormat === TableFormat.KUDU ||
        context.isRemoteTable ||
        context.isIcebergTable ||
        context.isCopyFile
    },
    {
      name: 'isInsertOnly',
      type: FieldType.CHECKBOX,
      label: 'Insert only',
      tooltip:
        'Table will be created with insert only mode, when disabled, the table will be created with insert, delete and update mode',
      isHidden: (context: SettingsContext) => !context.isTransactional
    },
    {
      name: 'isIcebergTable',
      type: FieldType.CHECKBOX,
      label: 'Iceberg table',
      isHidden: (context: SettingsContext) => !context.isIcebergEnabled || !context.isRemoteTable
    },
    {
      name: 'isCopyFile',
      type: FieldType.CHECKBOX,
      label: 'Copy file',
      tooltip:
        'Choosing this option will copy the file instead of moving it to the new location, and ensuring the original file remains unchanged.',
      isHidden: (context: SettingsContext) =>
        context.storeLocation === StoreLocation.MANAGED ||
        context.isTransactional ||
        !context.isRemoteTable ||
        context.importData === false
    },
    {
      name: 'useExternalLocation',
      type: FieldType.CHECKBOX,
      label: 'Use external location instead of default',
      tooltip: 'Use external location instead of default'
    },
    {
      name: 'externalLocation',
      type: FieldType.INPUT,
      placeholder: 'External location',
      isHidden: (context: SettingsContext) => !context.useExternalLocation
    }
  ],

  characterDelimiters: [
    {
      name: 'customCharDelimiters',
      type: FieldType.CHECKBOX,
      label: 'Custom char delimiters',
      tooltip: 'Custom char delimiters'
    }
  ],
  delimiters: [
    {
      name: 'fieldDelimiter',
      type: FieldType.SELECT,
      label: 'Field',
      placeholder: 'Choose an option',
      options: DELIMITER_OPTIONS,
      tooltip: 'Field delimiter',
      isHidden: (context: SettingsContext) => !context.customCharDelimiters
    },
    {
      name: 'arrayMapDelimiter',
      type: FieldType.SELECT,
      label: 'Array Map',
      placeholder: 'Choose an option',
      options: DELIMITER_OPTIONS,
      tooltip: 'Array map delimiter',
      isHidden: (context: SettingsContext) => !context.customCharDelimiters
    },
    {
      name: 'structDelimiter',
      type: FieldType.SELECT,
      label: 'Struct',
      placeholder: 'Choose an option',
      options: DELIMITER_OPTIONS,
      tooltip: 'Struct delimiter',
      isHidden: (context: SettingsContext) => !context.customCharDelimiters
    }
  ]
};

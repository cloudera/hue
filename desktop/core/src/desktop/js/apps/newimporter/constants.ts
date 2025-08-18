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

import { CombinedFileFormat, ImporterFileTypes } from './types';

export const separator = [
  { value: ',', label: 'Comma (,)' },
  { value: '\\t', label: '^Tab (\\t)' },
  { value: '\\n', label: '^New Line (\\n)' },
  { value: '|', label: 'Pipe (|)' },
  { value: '"', label: 'Double Quote (")' },
  { value: "'", label: "Single Quote (')" },
  { value: '\x00', label: '^0 (\\x00)' },
  { value: '\x01', label: '^A (\\x01)' },
  { value: '\x02', label: '^B (\\x02)' },
  { value: '\x03', label: '^C (\\x03)' }
];

export const sourceConfigs: {
  name: keyof CombinedFileFormat;
  label: string;
  hidden?: (type?: ImporterFileTypes) => boolean;
  options: {
    label: string;
    value: string | boolean;
  }[];
}[] = [
  {
    name: 'type',
    label: 'File Type',
    options: [
      { value: ImporterFileTypes.CSV, label: 'CSV' },
      { value: ImporterFileTypes.JSON, label: 'JSON' },
      { value: ImporterFileTypes.EXCEL, label: 'Excel' }
    ]
  },
  {
    name: 'hasHeader',
    label: 'Has Header',
    options: [
      { value: true, label: 'Yes' },
      { value: false, label: 'No' }
    ]
  },
  {
    name: 'fieldSeparator',
    label: 'Field Separator',
    hidden: (type?: ImporterFileTypes) => type !== ImporterFileTypes.CSV,
    options: separator
  },
  {
    name: 'recordSeparator',
    label: 'Record Separator',
    hidden: (type?: ImporterFileTypes) => type !== ImporterFileTypes.CSV,
    options: separator
  },
  {
    name: 'quoteChar',
    label: 'Quote Character',
    hidden: (type?: ImporterFileTypes) => type !== ImporterFileTypes.CSV,
    options: separator
  },
  {
    name: 'selectedSheetName',
    label: 'Sheet Name',
    hidden: (type?: ImporterFileTypes) => type !== ImporterFileTypes.EXCEL,
    options: []
  }
];

export const SUPPORTED_UPLOAD_TYPES = '.csv, .xlsx, .xls';
export const DEFAULT_UPLOAD_LIMIT = 150 * 1000 * 1000;

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

import { type ColumnProps } from 'cuix/dist/components/Table';
import { GuessFieldTypesColumn, ImporterTableData } from '../types';

export const convertToAntdColumns = (
  input?: GuessFieldTypesColumn[]
): ColumnProps<ImporterTableData>[] => {
  if (!input) {
    return [];
  }
  return input?.map(item => ({
    title: item.name,
    dataIndex: item.name,
    key: item.name,
    width: '100px'
  }));
};

export const convertToDataSource = (
  columns: ColumnProps<ImporterTableData>[],
  apiResponse?: string[][]
): ImporterTableData[] => {
  if (!apiResponse) {
    return [];
  }
  return apiResponse?.map((rowData, index) => {
    const row = {
      importerDataKey: `${rowData[0]}__${index}` // this ensure the key is unique
    };
    columns.forEach((column, index) => {
      if (column.key) {
        row[column.key] = rowData[index];
      }
    });
    return row;
  });
};

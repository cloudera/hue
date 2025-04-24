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
import { ImporterFileSource, GuessFieldTypesColumn, ImporterTableData } from '../types';
import { getLastDirOrFileNameFromPath } from '../../../reactComponents/PathBrowser/PathBrowser.util';

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

export const getFileNameFromPath = (filePath: string, fileSource: ImporterFileSource): string => {
  // For local files, the file name is extracted from the path
  // Example: /**/**/**:fileName;**.fileExtension
  if (fileSource === ImporterFileSource.LOCAL) {
    const match = filePath.match(/:(.*?);/);
    return match?.[1] ?? '';
  }

  // For Remote
  // Remove extension and replace '.' with '_'
  // Example: file.name.fileExtension -> file_name
  const fileName = getLastDirOrFileNameFromPath(filePath);
  if (fileName.split('.').length === 1) {
    // If there is no extension, return the file name as is
    return fileName;
  }
  return fileName.split('.').slice(0, -1).join('_');
};

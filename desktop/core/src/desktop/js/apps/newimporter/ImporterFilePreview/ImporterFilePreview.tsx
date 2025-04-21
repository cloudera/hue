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

import React, { useEffect, useState } from 'react';
import useSaveData from '../../../utils/hooks/useSaveData/useSaveData';
import {
  FileFormatResponse,
  FileMetaData,
  GuessFieldTypesResponse,
  ImporterTableData
} from '../types';
import { convertToAntdColumns, convertToDataSource, getDefaultTableName } from '../utils/utils';
import { i18nReact } from '../../../utils/i18nReact';
import { BorderlessButton, PrimaryButton } from 'cuix/dist/components/Button';
import PaginatedTable from '../../../reactComponents/PaginatedTable/PaginatedTable';
import { GUESS_FORMAT_URL, GUESS_FIELD_TYPES_URL, FINISH_IMPORT_URL } from '../api';
import SourceConfiguration from './SourceConfiguration/SourceConfiguration';
import EditColumn from './EditColumn/EditColumn';

import './ImporterFilePreview.scss';

interface ImporterFilePreviewProps {
  fileMetaData: FileMetaData;
}

const ImporterFilePreview = ({ fileMetaData }: ImporterFilePreviewProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [fileFormat, setFileFormat] = useState<FileFormatResponse | undefined>();

  const defaultTableName = getDefaultTableName(fileMetaData.path, fileMetaData.source);

  const { save: guessFormat, loading: guessingFormat } = useSaveData<FileFormatResponse>(
    GUESS_FORMAT_URL,
    {
      onSuccess: data => {
        setFileFormat(data);
      }
    }
  );

  const {
    save: guessFields,
    data: previewData,
    loading: guessingFields
  } = useSaveData<GuessFieldTypesResponse>(GUESS_FIELD_TYPES_URL);

  const { save, loading: finalizingImport } =
    useSaveData<GuessFieldTypesResponse>(FINISH_IMPORT_URL);

  useEffect(() => {
    const guessFormatPayload = {
      inputFormat: fileMetaData.source,
      file_type: fileMetaData.type,
      path: fileMetaData.path
    };
    const guessFormatormData = new FormData();
    guessFormatormData.append('fileFormat', JSON.stringify(guessFormatPayload));
    guessFormat(guessFormatormData);
  }, [fileMetaData]);

  useEffect(() => {
    if (!fileFormat) {
      return;
    }

    const payload = {
      path: fileMetaData.path,
      format: fileFormat,
      inputFormat: fileMetaData.source
    };
    const formData = new FormData();
    formData.append('fileFormat', JSON.stringify(payload));
    guessFields(formData);
  }, [fileMetaData.path, fileFormat]);

  const handleFinishImport = () => {
    // TODO: take the hardcoded values from the form once implemented
    const dialect = 'impala';
    const database = 'default';

    const source = {
      inputFormat: fileMetaData.source,
      path: fileMetaData.path,
      format: fileFormat,
      sourceType: dialect
    };
    const destination = {
      outputFormat: 'table',
      nonDefaultLocation: fileMetaData.path,
      name: `${database}.${defaultTableName}`,
      sourceType: dialect,
      columns: previewData?.columns
    };

    const formData = new FormData();
    formData.append('source', JSON.stringify(source));
    formData.append('destination', JSON.stringify(destination));

    save(formData);
  };

  const columns = convertToAntdColumns(previewData?.columns ?? []);
  const tableData = convertToDataSource(columns, previewData?.sample);

  return (
    <div className="hue-importer-preview-page">
      <div className="hue-importer-preview-page__header">
        <div className="hue-importer-preview-page__header__title">{t('Preview')}</div>
        <div className="hue-importer-preview-page__header__actions">
          <BorderlessButton data-testid="hue-importer-preview-page__header__actions__cancel">
            {t('Cancel')}
          </BorderlessButton>
          <PrimaryButton loading={finalizingImport} onClick={handleFinishImport}>
            {t('Finish Import')}
          </PrimaryButton>
        </div>
      </div>
      <div className="hue-importer-preview-page__metadata">{t('DESTINATION')}</div>
      <div className="hue-importer-preview-page__main-section">
        <div className="hue-importer-preview-page__header-section">
          <SourceConfiguration fileFormat={fileFormat} setFileFormat={setFileFormat} />
          <EditColumn />
        </div>
        <PaginatedTable<ImporterTableData>
          loading={guessingFormat || guessingFields}
          data={tableData}
          columns={columns}
          rowKey="importerDataKey"
          isDynamicHeight
          locale={{ emptyText: t('No data found in the file!') }}
        />
      </div>
    </div>
  );
};

export default ImporterFilePreview;

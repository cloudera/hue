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
  DestinationConfig,
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
import EditColumnsModal from './EditColumns/EditColumnsModal';
import type { Column } from './EditColumns/EditColumnsModal';

import './ImporterFilePreview.scss';

interface ImporterFilePreviewProps {
  fileMetaData: FileMetaData;
}

const ImporterFilePreview = ({ fileMetaData }: ImporterFilePreviewProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [fileFormat, setFileFormat] = useState<FileFormatResponse | undefined>();
  const [isEditColumnsOpen, setIsEditColumnsOpen] = useState(false);
  const [columns, setColumns] = useState<Column[]>([]);
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

  // Update columns when previewData changes
  useEffect(() => {
    if (previewData?.columns) {
      setColumns(convertToAntdColumns(previewData.columns));
    }
  }, [previewData]);

  // Update previewData columns before finishing import
  const handleFinishImport = () => {
    const source = {
      inputFormat: fileMetaData.source,
      path: fileMetaData.path,
      format: fileFormat,
      sourceType: destinationConfig.connectorId
    };
    // Map columns back to original format for backend if needed
    const destination = {
      outputFormat: 'table',
      nonDefaultLocation: fileMetaData.path,
      name: `${database}.${defaultTableName}`,
      sourceType: dialect,
      columns: columns.map(col => ({
        name: col.title,
        type: col.type || 'string',
        comment: col.comment || ''
      }))
    };

    const formData = new FormData();
    formData.append('source', JSON.stringify(source));
    formData.append('destination', JSON.stringify(destination));

    save(formData);
  };

  const tableData = convertToDataSource(columns, previewData?.sample);

  const sampleRows = Array.isArray(previewData?.sample?.[0])
    ? previewData.sample.map(rowArr =>
        columns.reduce((acc, col, idx) => {
          acc[col.dataIndex] = rowArr[idx];
          return acc;
        }, {})
      )
    : previewData?.sample;

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
      <div className="hue-importer-preview-page__metadata">
        <DestinationSettings
          defaultValues={destinationConfig}
          onChange={handleDestinationSettingsChange}
        />
      </div>
      <div className="hue-importer-preview-page__main-section">
        <div className="hue-importer-preview-page__header-section">
          <SourceConfiguration fileFormat={fileFormat} setFileFormat={setFileFormat} />
          <BorderlessButton
            onClick={() => setIsEditColumnsOpen(true)}
            className="hue-importer-preview-page__edit-columns-button"
          >
            {t('Edit Columns')}
          </BorderlessButton>
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

      <EditColumnsModal
        isOpen={isEditColumnsOpen}
        closeModal={() => setIsEditColumnsOpen(false)}
        columns={columns}
        setColumns={setColumns}
        sample={sampleRows}
      />
    </div>
  );
};

export default ImporterFilePreview;

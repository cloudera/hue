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

import React, { useState, useEffect } from 'react';
import useSaveData from '../../../utils/hooks/useSaveData/useSaveData';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';
import {
  CombinedFileFormat,
  FileFormatResponse,
  FileMetaData,
  FilePreviewResponse,
  GuessHeaderResponse,
  ImporterTableData
} from '../types';
import { convertToAntdColumns, convertToDataSource, getDefaultTableName } from '../utils/utils';
import { i18nReact } from '../../../utils/i18nReact';
import { BorderlessButton, PrimaryButton } from 'cuix/dist/components/Button';
import PaginatedTable from '../../../reactComponents/PaginatedTable/PaginatedTable';
import {
  FILE_GUESS_METADATA,
  FILE_GUESS_HEADER,
  FILE_PREVIEW_URL,
  FINISH_IMPORT_URL
} from '../api';
import SourceConfiguration from './SourceConfiguration/SourceConfiguration';
import EditColumnsModal from './EditColumns/EditColumnsModal';
import type { Column } from './EditColumns/EditColumnsModal';
import DestinationSettings from './DestinationSettings/DestinationSettings';

import './ImporterFilePreview.scss';

interface ImporterFilePreviewProps {
  fileMetaData: FileMetaData;
}

const ImporterFilePreview = ({ fileMetaData }: ImporterFilePreviewProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [fileFormat, setFileFormat] = useState<CombinedFileFormat | undefined>();

  const [isEditColumnsOpen, setIsEditColumnsOpen] = useState(false);
  const [columns, setColumns] = useState<Column[]>([]);
  interface DestinationConfig {
    connectorId?: string;
    [key: string]: unknown;
  }
  const defaultTableName = getDefaultTableName(fileMetaData);
  const [destinationConfig, setDestinationConfig] = useState<DestinationConfig>({
    tableName: getDefaultTableName(fileMetaData)
  });

  const handleDestinationSettingsChange = (name: string, value: string) => {
    setDestinationConfig(prevConfig => ({
      ...prevConfig,
      [name]: value
    }));
  };

  const { loading: guessingFormat } = useLoadData<FileFormatResponse>(FILE_GUESS_METADATA, {
    params: {
      file_path: fileMetaData.path,
      import_type: fileMetaData.source
    },
    skip: !fileMetaData.path,
    onSuccess: data => {
      setFileFormat({
        ...data,
        recordSeparator: data?.recordSeparator?.includes('\n') ? '\\n' : data?.recordSeparator,
        selectedSheetName: data?.sheetNames?.[0]
      });
    }
  });

  const { loading: guessingHeader } = useLoadData<GuessHeaderResponse>(FILE_GUESS_HEADER, {
    params: {
      file_path: fileMetaData.path,
      file_type: fileFormat?.type,
      import_type: fileMetaData.source,
      sheet_name: fileFormat?.selectedSheetName
    },
    skip: !fileFormat?.type,
    onSuccess: data => {
      setFileFormat(prev => ({
        ...(prev ?? {}),
        hasHeader: data.hasHeader
      }));
    },
    onError: () => {
      setFileFormat(prev => ({
        ...(prev ?? {}),
        hasHeader: false
      }));
    }
  });

  const { data: previewData, loading: loadingPreview } = useLoadData<FilePreviewResponse>(
    FILE_PREVIEW_URL,
    {
      params: {
        file_path: fileMetaData.path,
        file_type: fileFormat?.type,
        import_type: fileMetaData.source,
        sql_dialect: destinationConfig.connectorId,
        has_header: fileFormat?.hasHeader,
        sheet_name: fileFormat?.selectedSheetName,
        field_separator: fileFormat?.fieldSeparator,
        quote_char: fileFormat?.quoteChar,
        record_separator: fileFormat?.recordSeparator
      },
      skip:
        !fileFormat?.type ||
        fileFormat?.hasHeader === undefined ||
        destinationConfig.connectorId === undefined
    }
  );

  const { save, loading: finalizingImport } = useSaveData(FINISH_IMPORT_URL);

  useEffect(() => {
    if (previewData?.columns && Array.isArray(previewData.columns)) {
      setColumns(
        convertToAntdColumns(previewData.columns).map(col => ({
          title: col?.title != null ? String(col.title) : '',
          dataIndex: String(col.dataIndex || '')
        }))
      );
    } else {
      setColumns([]);
    }
  }, [previewData]);

  const handleFinishImport = () => {
    const source = {
      inputFormat: fileMetaData.source,
      path: fileMetaData.path,
      format: fileFormat,
      sourceType: destinationConfig.connectorId
    };

    const destination = {
      outputFormat: 'table',
      nonDefaultLocation: fileMetaData.path,
      name: `${destinationConfig.database}.${defaultTableName}`,
      sourceType: destinationConfig.connectorId,
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

  const tableData = convertToDataSource(previewData?.previewData ?? {});

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
          loading={guessingFormat || loadingPreview || guessingHeader}
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
        sample={tableData[0]}
      />
    </div>
  );
};

export default ImporterFilePreview;

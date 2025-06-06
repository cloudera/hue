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
import useSaveData from '../../../utils/hooks/useSaveData/useSaveData';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';
import { FileFormatResponse, FileMetaData, FilePreviewResponse, ImporterTableData } from '../types';
import { convertToAntdColumns, convertToDataSource, getDefaultTableName } from '../utils/utils';
import { i18nReact } from '../../../utils/i18nReact';
import { BorderlessButton, PrimaryButton } from 'cuix/dist/components/Button';
import PaginatedTable from '../../../reactComponents/PaginatedTable/PaginatedTable';
import { FIle_FORMAT_URL, FILE_PREVIEW_URL, FINISH_IMPORT_URL } from '../api';
import SourceConfiguration from './SourceConfiguration/SourceConfiguration';
import EditColumnsModal from './EditColumns/EditColumnsModal';

import './ImporterFilePreview.scss';

interface ImporterFilePreviewProps {
  fileMetaData: FileMetaData;
}

const ImporterFilePreview = ({ fileMetaData }: ImporterFilePreviewProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [fileFormat, setFileFormat] = useState<FileFormatResponse | undefined>();
  const defaultDialect = 'impala';

  const [isEditColumnsOpen, setIsEditColumnsOpen] = useState(false);
  const defaultTableName = getDefaultTableName(fileMetaData.path, fileMetaData.source);

  const { loading: guessingFormat } = useLoadData<FileFormatResponse>(FIle_FORMAT_URL, {
    params: {
      file_path: fileMetaData.path,
      import_type: fileMetaData.source
    },
    skip: !fileMetaData.path,
    onSuccess: data => {
      setFileFormat(data);
    }
  });

  const { data: previewData, loading: loadingPreview } = useLoadData<FilePreviewResponse>(
    FILE_PREVIEW_URL,
    {
      params: {
        file_path: fileMetaData.path,
        file_type: fileFormat?.type,
        import_type: fileMetaData.source,
        sql_dialect: defaultDialect,
        has_header: fileFormat?.hasHeader
      },
      skip: !fileFormat?.type,
      onSuccess: data => {
        setFileFormat(prev => {
          if (!prev) {
            return prev;
          }
          return {
            ...prev,
            hasHeader: data.hasHeader
          };
        });
      }
    }
  );

  const { save, loading: finalizingImport } = useSaveData(FINISH_IMPORT_URL);

  const handleFinishImport = () => {
    // TODO: take the hardcoded values from the form once implemented
    const database = 'default';

    const source = {
      inputFormat: fileMetaData.source,
      path: fileMetaData.path,
      format: fileFormat,
      sourceType: defaultDialect
    };
    const destination = {
      outputFormat: 'table',
      nonDefaultLocation: fileMetaData.path,
      name: `${database}.${defaultTableName}`,
      sourceType: defaultDialect,
      columns: previewData?.columns
    };

    const formData = new FormData();
    formData.append('source', JSON.stringify(source));
    formData.append('destination', JSON.stringify(destination));

    save(formData);
  };

  const columns = convertToAntdColumns(previewData?.columns ?? []);
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
      <div className="hue-importer-preview-page__metadata">{t('DESTINATION')}</div>
      <div className="hue-importer-preview-page__main-section">
        <div className="hue-importer-preview-page__header-section">
          <SourceConfiguration fileFormat={fileFormat} setFileFormat={setFileFormat} />
          <BorderlessButton onClick={() => setIsEditColumnsOpen(true)}>
            {t('Edit Columns')}
          </BorderlessButton>
        </div>
        <PaginatedTable<ImporterTableData>
          loading={guessingFormat || loadingPreview}
          data={tableData}
          columns={columns}
          rowKey="importerDataKey"
          isDynamicHeight
          locale={{ emptyText: t('No data found in the file!') }}
        />
      </div>
      <EditColumnsModal isOpen={isEditColumnsOpen} closeModal={() => setIsEditColumnsOpen(false)} />
    </div>
  );
};

export default ImporterFilePreview;

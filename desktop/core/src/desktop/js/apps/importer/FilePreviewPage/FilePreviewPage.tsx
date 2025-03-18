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

import React, { useEffect } from 'react';
import './FilePreviewPage.scss';
import useSaveData from '../../../utils/hooks/useSaveData/useSaveData';
import { useWindowSize } from '../../../utils/hooks/useWindowSize/useWindowSize';
import { GuessFieldTypesResponse } from '../types';
import { convertToAntdColumns, convertToDataSource } from '../util/util';
import { i18nReact } from '../../../utils/i18nReact';
import { BorderlessButton, PrimaryButton } from 'cuix/dist/components/Button';
import Table from '../../../reactComponents/Table/Table';
import LoadingErrorWrapper from '../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';

const GUESS_FORMAT_URL = '/indexer/api/indexer/guess_format';
const GUESS_FIELD_TYPES_URL = '/indexer/api/indexer/guess_field_types';

interface ImporterFilePreviewPageProps {
  path: string;
  fileType?: string;
  fileSource?: string;
}

const ImporterFilePreviewPage: React.FC<ImporterFilePreviewPageProps> = ({
  path,
  fileType = 'csv',
  fileSource = 'file'
}): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const {
    data: fileFormatData,
    save: guessFormat,
    loading: guessingFormat
  } = useSaveData(GUESS_FORMAT_URL, {
    postOptions: { qsEncodeData: false }
  });

  const {
    save: guessFields,
    data: previewData,
    loading: guessingFields
  } = useSaveData<GuessFieldTypesResponse>(GUESS_FIELD_TYPES_URL, {
    postOptions: { qsEncodeData: false }
  });

  useEffect(() => {
    const guessFormatPayload = {
      inputFormat: fileSource,
      file_type: fileType,
      path
    };
    const guessFormatormData = new FormData();
    guessFormatormData.append('fileFormat', JSON.stringify(guessFormatPayload));
    guessFormat(guessFormatormData);
  }, [path, fileType, fileSource]);

  useEffect(() => {
    if (!fileFormatData) return;

    const payload = {
      path,
      format: { ...fileFormatData, hasHeader: false },
      inputFormat: fileSource
    };
    const formData = new FormData();
    formData.append('fileFormat', JSON.stringify(payload));
    guessFields(formData);
  }, [path, fileFormatData]);

  const columns = convertToAntdColumns(previewData?.columns ?? []);
  const tableData = convertToDataSource(columns, previewData?.sample);

  const [ref, rect] = useWindowSize();

  return (
    <div className="preview-page">
      <div className="preview-page__header">
        <div className="preview-page__header__title">{t('Preview')}</div>
        <div className="preview-page__header__actions">
          <BorderlessButton data-testid="preview-page__header__actions__cancel" data-event="">
            {t('Cancel')}
          </BorderlessButton>
          <PrimaryButton data-testid="preview-page__header__actions__finish" data-event="">
            {t('Finish Import')}
          </PrimaryButton>
        </div>
      </div>
      <div className="preview-page__metadata">DESTINATION</div>
      <div className="preview-page__main-section" ref={ref}>
        <LoadingErrorWrapper loading={guessingFormat || guessingFields} errors={[]} hideChildren>
          <Table
            data={tableData}
            columns={columns}
            rowKey="importerDataKey"
            scroll={{
              y: Math.max(rect.height - 60, 100),
              x: true
            }}
            locale={{ emptyText: t('No data available') }}
          />
        </LoadingErrorWrapper>
      </div>
    </div>
  );
};

export default ImporterFilePreviewPage;

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
import DataInIcon from '@cloudera/cuix-core/icons/react/DataInIcon';

import { i18nReact } from '../../utils/i18nReact';
import { FileMetaData } from './types';
import CommonHeader from '../../reactComponents/CommonHeader/CommonHeader';
import FileImportTabs from './FileImportTabs/FileImportTabs';
import ImporterSourceSelector from './ImporterSourceSelector/ImporterSourceSelector';

import './ImporterPage.scss';

const ImporterPage = (): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [fileMetaData, setFileMetaData] = useState<FileMetaData>();

  return (
    <div className="hue-importer cuix antd">
      <CommonHeader title={t('Importer')} icon={<DataInIcon />} />
      <div className="hue-importer__container">
        {!fileMetaData?.path ? (
          <ImporterSourceSelector setFileMetaData={setFileMetaData} />
        ) : (
          <FileImportTabs fileMetaData={fileMetaData} />
        )}
      </div>
    </div>
  );
};

export default ImporterPage;

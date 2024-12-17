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
import { Spin } from 'antd';

import { i18nReact } from '../../../../utils/i18nReact';
import BucketIcon from '@cloudera/cuix-core/icons/react/BucketIcon';

import PathBrowser from '../../../../reactComponents/FileChooser/PathBrowser/PathBrowser';
import StorageBrowserTable from '../StorageBrowserTable/StorageBrowserTable';
import { FILE_STATS_API_URL } from '../../../../reactComponents/FileChooser/api';
import { BrowserViewType, FileStats } from '../../../../reactComponents/FileChooser/types';
import useLoadData from '../../../../utils/hooks/useLoadData';

import './StorageBrowserTabContent.scss';
import StorageFilePage from '../../StorageFilePage/StorageFilePage';

interface StorageBrowserTabContentProps {
  homeDir: string;
  testId?: string;
}

const defaultProps = {
  testId: 'hue-storage-browser-tab-content'
};

const StorageBrowserTabContent = ({
  homeDir,
  testId
}: StorageBrowserTabContentProps): JSX.Element => {
  const [filePath, setFilePath] = useState<string>(homeDir);
  const fileName = filePath?.split('/')?.pop() ?? '';

  const { t } = i18nReact.useTranslation();

  const { data: fileStats, loading } = useLoadData<FileStats>(FILE_STATS_API_URL, {
    params: {
      path: filePath
    },
    skip: !filePath
  });

  return (
    <Spin spinning={loading}>
      <div className="hue-storage-browser-tab-content" data-testid={testId}>
        <div className="hue-storage-browser__title-bar" data-testid={`${testId}-title-bar`}>
          <BucketIcon className="hue-storage-browser__icon" data-testid={`${testId}-icon`} />
          <h3 className="hue-storage-browser__folder-name" data-testid={`${testId}-folder-namer`}>
            {fileName}
          </h3>
        </div>
        <div
          className="hue-storage-browser__path-browser-panel"
          data-testid={`${testId}-path-browser-panel`}
        >
          <span className="hue-storage-browser__filePath">{t('File Path:')}</span>
          <PathBrowser
            filePath={filePath}
            onFilepathChange={setFilePath}
            seperator={'/'}
            showIcon={false}
          />
        </div>
        {fileStats?.type === BrowserViewType.dir && (
          <StorageBrowserTable fileStats={fileStats} onFilePathChange={setFilePath} />
        )}
        {fileStats?.type === BrowserViewType.file && (
          <StorageFilePage fileName={fileName} fileStats={fileStats} />
        )}
      </div>
    </Spin>
  );
};

StorageBrowserTabContent.defaultProps = defaultProps;

export default StorageBrowserTabContent;

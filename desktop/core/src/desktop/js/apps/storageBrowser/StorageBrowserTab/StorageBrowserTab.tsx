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

import { i18nReact } from '../../../utils/i18nReact';
import BucketIcon from '@cloudera/cuix-core/icons/react/BucketIcon';

import PathBrowser from '../../../reactComponents/PathBrowser/PathBrowser';
import StorageDirectoryPage from '../StorageDirectoryPage/StorageDirectoryPage';
import { FILE_STATS_API_URL } from '../../../reactComponents/FileChooser/api';
import { BrowserViewType, FileStats } from '../../../reactComponents/FileChooser/types';
import useLoadData from '../../../utils/hooks/useLoadData';

import './StorageBrowserTab.scss';
import StorageFilePage from '../StorageFilePage/StorageFilePage';
import changeURL from '../../../utils/url/changeURL';
import LoadingErrorWrapper from '../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';
import { getFileSystemAndPath } from '../../../reactComponents/PathBrowser/PathBrowser.util';

interface StorageBrowserTabProps {
  homeDir: string;
  fileSystem: string;
  testId?: string;
}

const defaultProps = {
  testId: 'hue-storage-browser-tab-content'
};

const StorageBrowserTab = ({
  homeDir,
  fileSystem,
  testId
}: StorageBrowserTabProps): JSX.Element => {
  const [urlPathname, urlFilePath] = decodeURIComponent(window.location.pathname).split('view=');
  const { fileSystem: urlFileSystem } = getFileSystemAndPath(urlFilePath);
  const initialFilePath = urlFileSystem === fileSystem ? urlFilePath : homeDir;

  const [filePath, setFilePath] = useState<string>(initialFilePath);
  const fileName = filePath.split('/').pop() ?? '';

  const { t } = i18nReact.useTranslation();

  const {
    data: fileStats,
    loading,
    error,
    reloadData
  } = useLoadData<FileStats>(FILE_STATS_API_URL, {
    params: { path: filePath },
    skip: !filePath
  });

  useEffect(() => {
    const encodedPath = `${urlPathname}view=${encodeURIComponent(filePath)}`;
    if (filePath && urlFilePath && filePath !== urlFilePath) {
      changeURL(encodedPath);
    }
    // if url path is correct but not encoded properly
    else if (encodedPath !== window.location.pathname) {
      changeURL(encodedPath, {}, true);
    }
  }, [filePath, urlPathname, urlFilePath, window.location.pathname]);

  const errorConfig = [
    {
      enabled: error?.response?.status === 404,
      message: t('Error: Path "{{path}}" not found.', { path: filePath }),
      action: t('Go to home directory'),
      onClick: () => setFilePath(homeDir)
    },
    {
      enabled: !!error && error?.response?.status !== 404,
      message: t('An error occurred while fetching filesystem "{{fileSystem}}".', {
        fileSystem: fileSystem.toUpperCase()
      }),
      action: t('Retry'),
      onClick: reloadData
    }
  ];

  return (
    <LoadingErrorWrapper loading={loading} errors={errorConfig}>
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
        {fileStats?.type === BrowserViewType.dir && !loading && (
          <StorageDirectoryPage fileStats={fileStats} onFilePathChange={setFilePath} />
        )}
        {fileStats?.type === BrowserViewType.file && !loading && (
          <StorageFilePage fileName={fileName} fileStats={fileStats} onReload={reloadData} />
        )}
      </div>
    </LoadingErrorWrapper>
  );
};

StorageBrowserTab.defaultProps = defaultProps;

export default StorageBrowserTab;

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
import { FILE_STATS_API_URL, TRASH_PATH } from '../api';
import { BrowserViewType, FileStats, FileSystem, TrashData } from '../types';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';
import { BorderlessButton } from 'cuix/dist/components/Button';

import './StorageBrowserTab.scss';
import StorageFilePage from '../StorageFilePage/StorageFilePage';
import changeURL from '../../../utils/url/changeURL';
import LoadingErrorWrapper from '../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';
import { getFileSystemAndPath } from '../../../reactComponents/PathBrowser/PathBrowser.util';
import RefreshIcon from '@cloudera/cuix-core/icons/react/RefreshIcon';
import HomeIcon from '@cloudera/cuix-core/icons/react/HomeIcon';
import DeleteIcon from '@cloudera/cuix-core/icons/react/DeleteIcon';
import { inTrash } from '../../../utils/storageBrowserUtils';
import { Alert } from 'antd';

interface StorageBrowserTabProps {
  fileSystem: FileSystem;
  testId?: string;
}

const defaultProps = {
  testId: 'hue-storage-browser-tab-content'
};

const StorageBrowserTab = ({ fileSystem, testId }: StorageBrowserTabProps): JSX.Element => {
  const urlPathname = window.location.pathname;
  const urlSearchParams = new URLSearchParams(window.location.search);
  const urlFilePath = decodeURIComponent(urlSearchParams.get('path') ?? '');
  const { fileSystem: urlFileSystem } = getFileSystemAndPath(urlFilePath);
  const initialFilePath =
    urlFileSystem === fileSystem.name ? urlFilePath : fileSystem.userHomeDirectory;

  const [filePath, setFilePath] = useState<string>(initialFilePath);
  const fileName =
    filePath.split('/').pop() !== '' ? (filePath.split('/').pop() ?? '') : filePath.split('://')[0];

  const { t } = i18nReact.useTranslation();

  const {
    data: trashData,
    loading: trashLoading,
    reloadData: onTrashPathReload
  } = useLoadData<TrashData>(TRASH_PATH, {
    params: { path: fileSystem.userHomeDirectory },
    skip: !fileSystem.config?.isTrashEnabled || !fileSystem.userHomeDirectory
  });

  const onTrashClick = async () => {
    const latestTrashData = await onTrashPathReload();
    setFilePath(latestTrashData?.trashPath ?? '');
  };

  const reloadTrashPath = () => {
    if (trashData?.trashPath) {
      return;
    }
    onTrashPathReload();
  };

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
    const urlQueryParams = { path: filePath };
    const encodedSearchParams = new URLSearchParams(urlQueryParams).toString();
    if (filePath && urlFilePath && filePath !== urlFilePath) {
      changeURL(urlPathname, urlQueryParams);
    }
    // if url path is correct but not encoded properly
    else if (encodedSearchParams !== window.location.search) {
      changeURL(urlPathname, urlQueryParams, true);
    }
  }, [filePath, urlPathname, urlFilePath, window.location]);

  const errorConfig = [
    {
      enabled: error?.response?.status === 404,
      message: t('Error: Path "{{path}}" not found.', { path: filePath }),
      action: t('Go to home directory'),
      onClick: () => setFilePath(fileSystem.userHomeDirectory)
    },
    {
      enabled: !!error && error?.response?.status !== 404,
      message: t('An error occurred while fetching filesystem "{{fileSystem}}".', {
        fileSystem: fileSystem.name.toUpperCase()
      }),
      action: t('Retry'),
      onClick: reloadData
    }
  ];

  const isLoading = loading || trashLoading;

  return (
    <LoadingErrorWrapper loading={isLoading} errors={errorConfig}>
      <div className="hue-storage-browser-tab-content" data-testid={testId}>
        <div className="hue-storage-browser__title-bar" data-testid={`${testId}-title-bar`}>
          <div className="hue-storage-browser__title">
            <BucketIcon className="hue-storage-browser__icon" data-testid={`${testId}-icon`} />
            <h3 className="hue-storage-browser__folder-name" data-testid={`${testId}-folder-namer`}>
              {fileName}
            </h3>
          </div>
          <div className="hue-storage-browser__home-bar-right">
            <BorderlessButton
              onClick={() => {
                setFilePath(fileSystem.userHomeDirectory);
              }}
              className="hue-storage-browser__home-bar-btns"
              data-event=""
              title={t('Home')}
              icon={<HomeIcon />}
            >
              {t('Home')}
            </BorderlessButton>
            {fileSystem.config?.isTrashEnabled && (
              <BorderlessButton
                onClick={onTrashClick}
                className="hue-path-browser__home-btn"
                data-event=""
                title={t('Trash')}
                icon={<DeleteIcon />}
                disabled={!trashData?.trashPath}
              >
                {t('Trash')}
              </BorderlessButton>
            )}
            <BorderlessButton
              onClick={() => reloadData()}
              className="hue-storage-browser__home-bar-btns"
              data-event=""
              title={t('Refresh')}
              icon={<RefreshIcon />}
            >
              {t('Refresh')}
            </BorderlessButton>
          </div>
        </div>
        {!!inTrash(filePath) && fileSystem.name === 'hdfs' && (
          <Alert
            type="warning"
            message={t(
              'This is Hadoop trash. Files will be under a checkpoint, or timestamp named, directory.'
            )}
          />
        )}
        <div
          className="hue-storage-browser__path-browser-panel"
          data-testid={`${testId}-path-browser-panel`}
        >
          <PathBrowser
            filePath={filePath}
            onFilepathChange={setFilePath}
            seperator={'/'}
            showIcon={false}
          />
        </div>
        {fileStats?.type === BrowserViewType.dir && !isLoading && (
          <StorageDirectoryPage
            fileStats={fileStats}
            onFilePathChange={setFilePath}
            fileSystem={fileSystem}
            reloadTrashPath={reloadTrashPath}
          />
        )}
        {fileStats?.type === BrowserViewType.file && !isLoading && (
          <StorageFilePage fileName={fileName} fileStats={fileStats} onReload={reloadData} />
        )}
      </div>
    </LoadingErrorWrapper>
  );
};

StorageBrowserTab.defaultProps = defaultProps;

export default StorageBrowserTab;

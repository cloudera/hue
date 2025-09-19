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
import { Alert } from 'antd';
import { AxiosError } from 'axios';
import BucketIcon from '@cloudera/cuix-core/icons/react/BucketIcon';
import RefreshIcon from '@cloudera/cuix-core/icons/react/RefreshIcon';
import HomeIcon from '@cloudera/cuix-core/icons/react/HomeIcon';
import DeleteIcon from '@cloudera/cuix-core/icons/react/DeleteIcon';

import { i18nReact } from '../../../utils/i18nReact';
import PathBrowser from '../../../reactComponents/PathBrowser/PathBrowser';
import StorageDirectoryPage from '../StorageDirectoryPage/StorageDirectoryPage';
import { FILE_STATS_API_URL, TRASH_PATH } from '../api';
import { BrowserViewType, FileStats, FileSystem, TrashData } from '../types';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';
import { BorderlessButton } from 'cuix/dist/components/Button';
import StorageFilePage from '../StorageFilePage/StorageFilePage';
import changeURL from '../../../utils/url/changeURL';
import LoadingErrorWrapper from '../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';
import {
  getLastDirOrFileNameFromPath,
  getFileSystemAndPath
} from '../../../reactComponents/PathBrowser/PathBrowser.util';
import { inTrash } from '../utils/utils';

import './StorageBrowserTab.scss';

interface StorageBrowserTabProps {
  fileSystem: FileSystem;
  testId?: string;
}

const defaultProps = {
  testId: 'hue-storage-browser-tab-content'
};

const StorageBrowserTab = ({ fileSystem, testId }: StorageBrowserTabProps): JSX.Element => {
  const urlFilePath = new URLSearchParams(window.location.search).get('path') ?? '';
  const { fileSystem: urlFileSystem } = getFileSystemAndPath(urlFilePath);
  const initialFilePath =
    urlFileSystem === fileSystem.name ? urlFilePath : fileSystem.userHomeDirectory;

  const [filePath, setFilePath] = useState<string>(initialFilePath);
  const fileName = getLastDirOrFileNameFromPath(filePath);

  const { t } = i18nReact.useTranslation();

  const { data: trashData, reloadData: onTrashPathReload } = useLoadData<TrashData>(TRASH_PATH, {
    params: { path: fileSystem.userHomeDirectory },
    skip: !fileSystem.config?.isTrashEnabled || !fileSystem.userHomeDirectory
  });

  const onTrashClick = async () => {
    const latestTrashData = await onTrashPathReload();
    setFilePath(latestTrashData?.trashPath ?? '');
  };

  const reloadTrashPath = () => {
    if (trashData?.trashPath || !fileSystem.config?.isTrashEnabled) {
      return;
    }
    onTrashPathReload();
  };

  const {
    data: fileStats,
    loading,
    error,
    reloadData
  } = useLoadData<FileStats, { path: string }, AxiosError>(FILE_STATS_API_URL, {
    options: { isRawError: true },
    params: { path: filePath },
    skip: !filePath
  });

  useEffect(() => {
    const urlPathname = window.location.pathname;
    const urlQueryParams = { path: filePath };
    const encodedSearchParams = new URLSearchParams(urlQueryParams).toString();
    if (filePath && urlFilePath && filePath !== urlFilePath) {
      changeURL(urlPathname, urlQueryParams);
    }
    // if url path is correct but not encoded properly
    else if (encodedSearchParams !== window.location.search) {
      changeURL(urlPathname, urlQueryParams, true);
    }
  }, [filePath, urlFilePath, window.location]);

  const errors = [
    {
      enabled: error?.response?.status === 404 && filePath !== fileSystem.userHomeDirectory,
      message: t('Path "{{path}}" does not exist.', { path: filePath })
    },
    {
      enabled: error?.response?.status === 404 && filePath === fileSystem.userHomeDirectory,
      message: t('User home directory "{{path}}" does not exist.', {
        path: filePath
      })
    },
    {
      enabled: error?.response?.status === 403,
      message: t('Unauthorized access to the path "{{path}}".', {
        path: filePath
      })
    },
    {
      enabled: !!error && error?.response?.status !== 404 && error?.response?.status !== 403,
      message: t('An unkown error occurred while fetching path "{{path}}".', {
        path: filePath
      }),
      actionText: t('Retry'),
      onClick: reloadData
    }
  ];

  return (
    <div className="hue-storage-browser-tab" data-testid={testId}>
      <div
        className="hue-storage-browser-tab__title-bar-container"
        data-testid={`${testId}-title-bar`}
      >
        <div className="hue-storage-browser-tab__title-bar">
          <BucketIcon
            className="hue-storage-browser-tab__title-bar-icon"
            data-testid={`${testId}-icon`}
          />
          <h3
            className="hue-storage-browser-tab__title-bar-name"
            data-testid={`${testId}-folder-namer`}
          >
            {fileName}
          </h3>
        </div>
        <div className="hue-storage-browser-tab__title-bar-button-group">
          <BorderlessButton
            onClick={() => {
              setFilePath(fileSystem.userHomeDirectory);
            }}
            className="hue-storage-browser-tab__title-bar-button"
            title={t('Home')}
            icon={<HomeIcon />}
          >
            {t('Home')}
          </BorderlessButton>
          {fileSystem.config?.isTrashEnabled && (
            <BorderlessButton
              onClick={onTrashClick}
              className="hue-storage-browser-tab__title-bar-button"
              title={t('Trash')}
              icon={<DeleteIcon />}
              disabled={!trashData?.trashPath}
            >
              {t('Trash')}
            </BorderlessButton>
          )}
          <BorderlessButton
            onClick={reloadData}
            className="hue-storage-browser-tab__title-bar-button"
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
        className="hue-storage-browser-tab__path-browser-container"
        data-testid={`${testId}-path-browser-panel`}
      >
        <PathBrowser filePath={filePath} onFilepathChange={setFilePath} />
      </div>
      <LoadingErrorWrapper loading={loading} errors={errors}>
        {fileStats?.type === BrowserViewType.dir && !loading && (
          <StorageDirectoryPage
            fileStats={fileStats}
            onFilePathChange={setFilePath}
            fileSystem={fileSystem}
            reloadTrashPath={reloadTrashPath}
          />
        )}
        {fileStats?.type === BrowserViewType.file && !loading && (
          <StorageFilePage fileStats={fileStats} onReload={reloadData} />
        )}
      </LoadingErrorWrapper>
    </div>
  );
};

StorageBrowserTab.defaultProps = defaultProps;

export default StorageBrowserTab;

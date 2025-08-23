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

import React from 'react';
import { Tabs } from 'antd';

import DataBrowserIcon from '@cloudera/cuix-core/icons/react/DataBrowserIcon';

import { i18nReact } from '../../utils/i18nReact';
import CommonHeader from '../../reactComponents/CommonHeader/CommonHeader';
import StorageBrowserTab from './StorageBrowserTab/StorageBrowserTab';
import { FILESYSTEMS_API_URL } from './api';

import './StorageBrowserPage.scss';
import useLoadData from '../../utils/hooks/useLoadData/useLoadData';
import LoadingErrorWrapper from '../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';
import { getFileSystemAndPath } from '../../reactComponents/PathBrowser/PathBrowser.util';
import { FileSystem } from './types';

const StorageBrowserPage = (): JSX.Element => {
  const urlFilePath = new URLSearchParams(window.location.search).get('path') ?? '';
  const { fileSystem: urlFileSystem } = getFileSystemAndPath(urlFilePath);

  const { t } = i18nReact.useTranslation();

  const { data, loading, error, reloadData } = useLoadData<FileSystem[]>(FILESYSTEMS_API_URL);

  const errorConfig = [
    {
      enabled: !!error,
      message: t('An error occurred while fetching the filesystem'),
      actionText: t('Retry'),
      onClick: reloadData
    }
  ];

  return (
    <div className="hue-storage-browser cuix antd">
      <CommonHeader title={t('Storage Browser')} icon={<DataBrowserIcon />} />
      <div className="hue-storage-browser__container">
        <LoadingErrorWrapper loading={loading} errors={errorConfig}>
          <Tabs
            className="hue-storage-browser__tab"
            data-testid="hue-storage-browser__tabs"
            destroyInactiveTabPane
            defaultActiveKey={urlFileSystem ?? data?.[0]?.name}
            items={data?.map(fileSystem => ({
              label: fileSystem.name.toUpperCase(),
              key: fileSystem.name,
              children: <StorageBrowserTab fileSystem={fileSystem} />
            }))}
          />
        </LoadingErrorWrapper>
      </div>
    </div>
  );
};

export default StorageBrowserPage;

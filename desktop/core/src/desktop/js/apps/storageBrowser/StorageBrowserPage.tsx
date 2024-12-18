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
import { Tabs, Spin } from 'antd';

import DataBrowserIcon from '@cloudera/cuix-core/icons/react/DataBrowserIcon';

import { i18nReact } from '../../utils/i18nReact';
import CommonHeader from '../../reactComponents/CommonHeader/CommonHeader';
import StorageBrowserTab from './StorageBrowserTab/StorageBrowserTab';
import { ApiFileSystem, FILESYSTEMS_API_URL } from '../../reactComponents/FileChooser/api';

import './StorageBrowserPage.scss';
import useLoadData from '../../utils/hooks/useLoadData';

const StorageBrowserPage = (): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const { data: fileSystems, loading } = useLoadData<ApiFileSystem[]>(FILESYSTEMS_API_URL);

  return (
    <div className="hue-storage-browser cuix antd">
      <CommonHeader title={t('Storage Browser')} icon={<DataBrowserIcon />} />
      <Spin spinning={loading}>
        <Tabs
          className="hue-storage-browser__tab"
          defaultActiveKey="0"
          items={fileSystems?.map(system => ({
            label: system.file_system.toUpperCase(),
            key: system.file_system + '_tab',
            children: <StorageBrowserTab homeDir={system.user_home_directory} />
          }))}
        />
      </Spin>
    </div>
  );
};

export default StorageBrowserPage;

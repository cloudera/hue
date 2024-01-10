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
import { Tabs, Spin } from 'antd';
import type { TabsProps } from 'antd';

import DataBrowserIcon from '@cloudera/cuix-core/icons/react/DataBrowserIcon';

import { i18nReact } from '../../../utils/i18nReact';
import CommonHeader from '../../../reactComponents/CommonHeader/CommonHeader';
import StorageBrowserTabContent from './StorageBrowserTabContents/StorageBrowserTabContent';
import { fetchFileSystems } from '../../../reactComponents/FileChooser/api';

import './StorageBrowserPage.scss';

const StorageBrowserPage: React.FC = (): JSX.Element => {
  const [fileSystemTabs, setFileSystemTabs] = useState<TabsProps['items'] | undefined>();
  const [loading, setLoading] = useState(true);

  const { t } = i18nReact.useTranslation();

  useEffect(() => {
    if (!fileSystemTabs) {
      setLoading(true);
      fetchFileSystems()
        .then(fileSystems => {
          const fileSystemsObj = fileSystems.map(system => {
            return {
              label: system.file_system.toUpperCase(),
              key: system.file_system + '_tab',
              children: <StorageBrowserTabContent user_home_dir={system.user_home_directory} />
            };
          });
          setFileSystemTabs(fileSystemsObj);
        })
        .catch(error => {
          //TODO: Properly handle errors.
          console.error(error);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, []);

  return (
    <div className="hue-storage-browser">
      <CommonHeader title={t('Storage Browser')} icon={<DataBrowserIcon />} />
      <Spin spinning={loading}>
        <Tabs className="hue-storage-browser__tab" defaultActiveKey="0" items={fileSystemTabs} />
      </Spin>
    </div>
  );
};

export default StorageBrowserPage;

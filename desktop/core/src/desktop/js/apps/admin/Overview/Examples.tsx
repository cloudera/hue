// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import React, { useState } from 'react';
import { Button } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
// import { fetchWithCsrf } from '../../../reactComponents/utils';
import { get } from '../../../api/utils';
import huePubSub from '../../../utils/huePubSub';
import { i18nReact } from '../../../utils/i18nReact';
import './Overview.scss';

const exampleApps = [
  { id: 'hive', name: 'Hive', old_name: 'beeswax' },
  { id: 'impala', name: 'Impala' },
  { id: 'search', name: 'Solr Search', data: ['log_analytics_demo', 'twitter_demo', 'yelp_demo'] },
  { id: 'spark', name: 'Spark', old_name: 'notebook' },
  { id: 'oozie', name: 'Oozie Editor/Dashboard' },
  { id: 'hbase', name: 'Hbase Browser' },
  { id: 'pig', name: 'Pig Editor' }
];

type InstallExamplesResponse = {
  status: number;
  message?: string;
};

const Examples = (): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [installingAppId, setInstallingAppId] = useState(null);

  const handleInstall = async appData => {
    setInstallingAppId(appData.id);
    const appIdOrOldName = appData.old_name || appData.id;
    const url = `/${appIdOrOldName}/install_examples`;
    const data = appData.data ? { data: appData.data } : null;

    get<InstallExamplesResponse>(url, data, {
      method: 'POST',
      silenceErrors: true
    })
      .then(response => {
        if (response.status === 0) {
          const message = response.message ? t(response.message) : t('Examples refreshed');
          huePubSub.publish('hue.global.info', { message });
        } else {
          const errorMessage = response.message
            ? t(response.message)
            : t('An error occurred while installing examples.');
          huePubSub.publish('hue.global.error', { message: errorMessage });
        }
      })
      .catch(error => {
        const errorMessage =
          error && typeof error === 'object' && error.message
            ? t(error.message)
            : t('An unexpected error occurred');
        huePubSub.publish('hue.global.error', { message: errorMessage });
      })
      .finally(() => {
        setInstallingAppId(null);
      });
  };

  // const handleInstall = async (appData) => {
  //   try {
  //     setInstallingAppId(appData.id);
  //     const appIdOrOldName = appData.old_name || appData.id;
  //     const url = `/${appIdOrOldName}/install_examples`;

  //     const data = appData.data ? { data: appData.data } : {};

  // const options = {
  //   method: 'POST',
  //   headers: {
  //     'Content-Type': 'application/json'
  //   }
  // };
  // if (appData.data) {
  //   options.body = JSON.stringify({ data: appData.data });
  // }
  // const response = await fetchWithCsrf(url, options);

  //     const responseBody = await response.json();
  //     if (responseBody.status == 0) {
  //       if (responseBody.message) {
  //         huePubSub.publish('hue.global.info', { message: t(responseBody.message) });
  //       } else {
  //         huePubSub.publish('hue.global.info', { message: t('Examples refreshed') });
  //       }
  //     } else {
  //       huePubSub.publish('hue.global.error', { message: t(responseBody.message) });
  //     }
  //   } finally {
  //     setInstallingAppId(null);
  //   }
  // };

  return (
    <div className="overview-examples">
      <h3>{t('Install some data examples')}</h3>
      {exampleApps.map(appData => (
        <div key={appData.id}>
          <Button
            type="link"
            onClick={() => handleInstall(appData)}
            disabled={installingAppId === appData.id}
            icon={<DownloadOutlined />}
          >
            {installingAppId === appData.id ? 'Installing...' : appData.name}
          </Button>
        </div>
      ))}
    </div>
  );
};

export default Examples;

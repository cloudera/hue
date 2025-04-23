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

import React, { useState, useEffect } from 'react';
import LinkButton from 'cuix/dist/components/Button/LinkButton';
import { DownloadOutlined } from '@ant-design/icons';
import Loading from 'cuix/dist/components/Loading';
import {
  INSTALL_APP_EXAMPLES_API_URL,
  INSTALL_AVAILABLE_EXAMPLES_API_URL
} from '../Components/utils';
import { get, post } from '../../../api/utils';
import huePubSub from '../../../utils/huePubSub';
import { i18nReact } from '../../../utils/i18nReact';
import './Overview.scss';

const exampleAppsWithData = [
  { id: 'search', name: 'Solr Search', data: ['log_analytics_demo', 'twitter_demo', 'yelp_demo'] }
];

const excludedApps = ['notebook'];

type InstallExamplesResponse = {
  status: number;
  message?: string;
};

const Examples = (): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [installingAppId, setInstallingAppId] = useState<string>('');
  const [availableApps, setAvailableApps] = useState<{ [key: string]: string }>({});
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchAvailableApps = async () => {
      try {
        const response = await get(INSTALL_AVAILABLE_EXAMPLES_API_URL, {});
        if (response.apps) {
          const filteredApps = Object.entries(response.apps)
            .filter(([appId]) => !excludedApps.includes(appId))
            .reduce((apps, [appId, appName]) => ({ ...apps, [appId]: appName }), {});

          setAvailableApps(filteredApps);
        }
      } catch (error) {
        console.error('Error fetching available app examples:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAvailableApps();
  }, []);

  const installExamplesCall = async (url: string, data: Record<string, unknown>) => {
    const response = await post<InstallExamplesResponse>(url, data);
    return response;
  };

  const handleInstall = async (exampleApp: { id: string; name: string }) => {
    setInstallingAppId(exampleApp.id);
    const url = INSTALL_APP_EXAMPLES_API_URL;

    let actualAppName;
    switch (exampleApp.id) {
      case 'spark':
        actualAppName = 'notebook';
        break;
      case 'jobsub':
        actualAppName = 'oozie';
        break;
      default:
        actualAppName = exampleApp.id;
    }

    try {
      const appWithExtraData = exampleAppsWithData.find(app => app.id === exampleApp.id);
      if (appWithExtraData && appWithExtraData.data) {
        const installPromises = appWithExtraData.data.map(eachData =>
          installExamplesCall(url, {
            app_name: actualAppName,
            data: eachData
          })
        );
        await Promise.all(installPromises);
      } else {
        await installExamplesCall(url, { app_name: actualAppName });
      }
      const message = `${actualAppName} ${t('examples installed successfully')}`;
      huePubSub.publish('hue.global.info', { message });
    } catch (error) {
      const errorMessage = error.message
        ? `${t('An error occurred while installing')} ${actualAppName}: ${error.message}`
        : `${t('An error occurred while installing')} ${actualAppName}.`;
      huePubSub.publish('hue.global.error', { message: errorMessage });
    } finally {
      setInstallingAppId('');
    }
  };

  return (
    <div className="overview-examples">
      <h3>{t('Install some data examples')}</h3>
      {loading ? (
        <Loading spinning={loading} />
      ) : (
        Object.entries(availableApps).map(([appId, appName]) => (
          <div key={appId}>
            <LinkButton
              onClick={() => handleInstall({ id: appId, name: appName })}
              disabled={installingAppId === appId}
              icon={<DownloadOutlined />}
              className="examples__install-btn"
            >
              {installingAppId === appId
                ? t('Installing...')
                : appName[0].toUpperCase() + appName.slice(1)}
            </LinkButton>
          </div>
        ))
      )}
    </div>
  );
};

export default Examples;

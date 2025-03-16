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
import huePubSub from '../../../utils/huePubSub';
import { i18nReact } from '../../../utils/i18nReact';
import { post } from '../../../api/utils';
import './Overview.scss';

interface PostResponse {
  status: number;
  message?: string;
}

const Analytics = (): JSX.Element => {
  const [collectUsage, setCollectUsage] = useState(false);
  const { t } = i18nReact.useTranslation();

  // const saveCollectUsagePreference = async collectUsage => {
  //   $.post('/about/update_preferences', { collect_usage: collectUsage ? 'on' : null }, data => {
  //     if (data.status == 0) {
  //       huePubSub.publish('hue.global.info', { message: t('Configuration updated') });
  //     } else {
  //       huePubSub.publish('hue.global.error', { message: t(data.data) });
  //     }
  //   });
  // };

  const saveCollectUsagePreference = async (collectUsage: boolean) => {
    try {
      const response = await post<PostResponse>('/about/update_preferences', {
        collect_usage: collectUsage ? 'on' : null
      });

      if (response.status === 0) {
        huePubSub.publish('hue.global.info', { message: t('Configuration updated') });
      } else {
        huePubSub.publish('hue.global.error', {
          message: t(response.message || 'Error updating configuration')
        });
      }
    } catch (err) {
      huePubSub.publish('hue.global.error', { message: t(String(err)) });
    }
  };

  const handleCheckboxChange = async event => {
    const newPreference = event.target.checked;
    setCollectUsage(newPreference);
    await saveCollectUsagePreference(newPreference);
  };

  return (
    <div className="overview-analytics">
      <h3>{t('Anonymous usage analytics')}</h3>
      <input
        type="checkbox"
        id="usage_analytics"
        title={t('Check to enable usage analytics')}
        checked={collectUsage}
        onChange={handleCheckboxChange}
      />
      <label htmlFor="usage_analytics" className="usage_analytics">
        {t('Help improve Hue with anonymous usage analytics.')}
      </label>
    </div>
  );
};

export default Analytics;

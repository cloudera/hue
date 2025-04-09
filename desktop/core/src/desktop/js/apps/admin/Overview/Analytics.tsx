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
import Input from 'cuix/dist/components/Input';
import { post } from '../../../api/utils';
import { ANALYTICS_PREFERENCES_API_URL } from '../Components/utils';
import './Overview.scss';

interface UpdatePreferences {
  status: number;
  message?: string;
}

const Analytics = (): JSX.Element => {
  const [collectUsage, setCollectUsage] = useState<boolean>(false);
  const { t } = i18nReact.useTranslation();

  const saveCollectUsagePreference = async (collectUsage: boolean) => {
    const response = await post<UpdatePreferences>(ANALYTICS_PREFERENCES_API_URL, {
      collect_usage: collectUsage ? 'on' : null
    });

    if (response.status === 0) {
      huePubSub.publish('hue.global.info', { message: t('Configuration updated') });
    } else {
      huePubSub.publish('hue.global.error', {
        message: t('Error updating configuration')
      });
    }
  };

  const handleCheckboxChange = event => {
    const newPreference = event.target.checked;
    setCollectUsage(newPreference);
    saveCollectUsagePreference(newPreference);
  };

  return (
    <div className="overview-analytics">
      <h3>{t('Anonymous usage analytics')}</h3>
      <div className="analytics-checkbox-container">
        <Input
          type="checkbox"
          className="analytics__checkbox-icon"
          id="usage_analytics"
          checked={collectUsage}
          onChange={handleCheckboxChange}
        />
        <label htmlFor="usage_analytics" className="usage__analytics">
          {t('Help improve Hue with anonymous usage analytics.')}
        </label>
      </div>
    </div>
  );
};

export default Analytics;

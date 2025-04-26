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
import huePubSub from '../../../utils/huePubSub';
import { i18nReact } from '../../../utils/i18nReact';
import Alert from 'cuix/dist/components/Alert';
import Input from 'cuix/dist/components/Input';
import { post } from '../../../api/utils';
import { GET_USAGE_ANALYTICS_API_URL, UPDATE_USAGE_ANALYTICS_API_URL } from '../Components/utils';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';
import LoadingErrorWrapper from '../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';
import './Overview.scss';

interface UsageAnalyticsResponse {
  analytics_enabled: boolean;
  message?: string;
}

const Analytics = (): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const { data, loading, error, reloadData } = useLoadData<UsageAnalyticsResponse>(
    GET_USAGE_ANALYTICS_API_URL
  );

  const [analyticsEnabled, setAnalyticsEnabled] = useState<boolean>(false);

  useEffect(() => {
    if (data?.analytics_enabled !== undefined) {
      setAnalyticsEnabled(data.analytics_enabled);
    }
  }, [data]);

  const saveCollectUsagePreference = async (newPreference: boolean) => {
    try {
      const response = await post<UsageAnalyticsResponse>(UPDATE_USAGE_ANALYTICS_API_URL, {
        analytics_enabled: newPreference
      });

      if (response && response.analytics_enabled !== undefined) {
        reloadData();
        setAnalyticsEnabled(newPreference);

        const successMessage = newPreference
          ? t('Analytics have been activated.')
          : t('Analytics have been deactivated.');
        huePubSub.publish('hue.global.info', { message: successMessage });
      }
    } catch (error) {
      console.error('Error updating usage analytics settings:', error);
      const errorMessage = newPreference
        ? t('Failed to activate analytics.')
        : t('Failed to deactivate analytics.');
      huePubSub.publish('hue.global.error', { message: errorMessage });
    }
  };

  const handleCheckboxChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const newPreference = event.target.checked;
    await saveCollectUsagePreference(newPreference);
  };

  return (
    <LoadingErrorWrapper loading={loading}>
      <div className="overview-analytics">
        <h3>{t('Anonymous usage analytics')}</h3>
        <div className="analytics-checkbox-container">
          <Input
            type="checkbox"
            className="analytics__checkbox-icon"
            id="usage_analytics"
            checked={analyticsEnabled}
            onChange={handleCheckboxChange}
            disabled={loading}
          />
          <label htmlFor="usage_analytics" className="usage__analytics">
            {t('Help improve Hue with anonymous usage analytics.')}
          </label>
        </div>
        {error && (
          <Alert
            message={`${t('Error:')} ${error}`}
            description={t('An error occurred while fetching usage analytics settings.')}
            type="error"
          />
        )}
      </div>
    </LoadingErrorWrapper>
  );
};

export default Analytics;

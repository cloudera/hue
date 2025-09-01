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

import React from 'react';
import huePubSub from '../../../utils/huePubSub';
import { i18nReact } from '../../../utils/i18nReact';
import Input from 'cuix/dist/components/Input';
import { USAGE_ANALYTICS_API_URL } from '../Components/utils';
import { HueAlert } from '../../../reactComponents/GlobalAlert/types';
import { GLOBAL_INFO_TOPIC } from '../../../reactComponents/GlobalAlert/events';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';
import useSaveData from '../../../utils/hooks/useSaveData/useSaveData';
import LoadingErrorWrapper from '../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';
import { HttpMethod } from '../../../api/utils';
import './Overview.scss';

interface UsageAnalyticsResponse {
  collectUsage?: boolean;
}

const Analytics = (): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const {
    data: usageAnalyticsData,
    loading: loadingAnalytics,
    error: usageAnalyticsError,
    reloadData
  } = useLoadData<UsageAnalyticsResponse>(USAGE_ANALYTICS_API_URL);

  const {
    save: updateAnalyticsPreference,
    loading: updatingAnalyticsPreference,
    error: updateAnalyticsPreferenceError
  } = useSaveData<UsageAnalyticsResponse>(USAGE_ANALYTICS_API_URL, {
    method: HttpMethod.PUT,
    onSuccess: response => {
      reloadData();
      const successMessage = response.collectUsage
        ? t('Analytics have been activated.')
        : t('Analytics have been deactivated.');
      huePubSub.publish<HueAlert>(GLOBAL_INFO_TOPIC, { message: successMessage });
    }
  });

  const errors = [
    {
      enabled: !!usageAnalyticsError,
      message: usageAnalyticsError ?? t('An unknown error occurred while fetching data.')
    },
    {
      enabled: !!updateAnalyticsPreferenceError,
      message: updateAnalyticsPreferenceError ?? t('Failed to update analytics.')
    }
  ];

  const handleAnalyticsCheckboxChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    updateAnalyticsPreference({ collect_usage: event.target.checked });
  };

  return (
    <LoadingErrorWrapper loading={loadingAnalytics || updatingAnalyticsPreference} errors={errors}>
      <div className="overview-analytics">
        <h3>{t('Anonymous usage analytics')}</h3>
        <div className="analytics-checkbox-container">
          <Input
            type="checkbox"
            className="analytics__checkbox-icon"
            id="usage_analytics"
            checked={!!usageAnalyticsData?.collectUsage}
            onChange={handleAnalyticsCheckboxChange}
            disabled={loadingAnalytics || updatingAnalyticsPreference}
          />
          <label htmlFor="usage_analytics" className="usage__analytics">
            {t('Help improve Hue with anonymous usage analytics.')}
          </label>
        </div>
      </div>
    </LoadingErrorWrapper>
  );
};

export default Analytics;

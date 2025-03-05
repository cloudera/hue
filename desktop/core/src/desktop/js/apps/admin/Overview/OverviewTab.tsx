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
import { Spin, Alert, Tabs } from 'antd';
import Examples from './Examples';
import ConfigStatus from './ConfigStatus';
import Analytics from './Analytics';
import { i18nReact } from '../../../utils/i18nReact';
// import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';
// import { OVERVIEW_API_URL } from '../../Components/utils';
import './Overview.scss';

const { TabPane } = Tabs;

// interface OverviewData {
//   logs: string[];
//   hue_hostname: string;
// }

const Overview: React.FC = (): JSX.Element => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const { t } = i18nReact.useTranslation();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // const response = await get<OverviewResponse>('/desktop/overview/', { format: 'json' });
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="hue-overview-component">
      <Spin spinning={loading}>
        {error && (
          <Alert
            message={`Error: ${error}`}
            description="An error occurred while fetching overview."
            type="error"
          />
        )}

        {!error && !loading && (
          <>
            <Tabs tabPosition="left">
              <TabPane tab={t('ConfigStatus')} key="1">
                <ConfigStatus />
              </TabPane>
              <TabPane tab={t('Examples')} key="2">
                <Examples />
              </TabPane>
              <TabPane tab={t('Analytics')} key="3">
                <Analytics />
              </TabPane>
            </Tabs>
          </>
        )}
      </Spin>
    </div>
  );
};

export default Overview;

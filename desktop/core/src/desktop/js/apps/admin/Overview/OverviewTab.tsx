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
import { Tabs } from 'antd';
import Examples from './Examples';
import ConfigStatus from './ConfigStatus';
import Analytics from './Analytics';
import { i18nReact } from '../../../utils/i18nReact';
import './Overview.scss';

const Overview = (): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const items = [
    {
      label: t('Config Status'),
      key: '1',
      children: <ConfigStatus />
    },
    {
      label: t('Examples'),
      key: '2',
      children: <Examples />
    },
    {
      label: t('Analytics'),
      key: '3',
      children: <Analytics />
    }
  ];

  return (
    <div className="hue-overview-component">
      <Tabs tabPosition="left" items={items} />
      <div className="overview__trademark-text">
        {t('Hue and the Hue logo are trademarks of Cloudera, Inc.')}
      </div>
    </div>
  );
};

export default Overview;

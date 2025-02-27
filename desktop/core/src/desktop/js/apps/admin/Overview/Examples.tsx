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
import { fetchWithCsrf } from '../../../reactComponents/utils';
import huePubSub from '../../../utils/huePubSub';

const exampleApps = [
  { id: 'hive', name: 'Hive', old_name: 'beeswax' },
  { id: 'impala', name: 'Impala' },
  { id: 'search', name: 'Solr Search', data: ['log_analytics_demo', 'twitter_demo', 'yelp_demo'] },
  { id: 'spark', name: 'Spark', old_name: 'notebook' },
  { id: 'oozie', name: 'Oozie Editor/Dashboard' },
  { id: 'hbase', name: 'Hbase Browser' },
  { id: 'pig', name: 'Pig Editor' }
];

const Examples = (): JSX.Element => {
  const [installingAppId, setInstallingAppId] = useState(null);

  const handleInstall = async appData => {
    try {
      setInstallingAppId(appData.id);
      const appIdOrOldName = appData.old_name || appData.id;
      const url = `/${appIdOrOldName}/install_examples`;

      const options = {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      };

      if (appData.data) {
        options.body = JSON.stringify({ data: appData.data });
      }

      const response = await fetchWithCsrf(url, options);

      const responseBody = await response.json();
      if (responseBody.status == 0) {
        if (responseBody.message) {
          huePubSub.publish('hue.global.info', { message: responseBody.message });
        } else {
          huePubSub.publish('hue.global.info', { message: 'Examples refreshed' });
        }
      } else {
        huePubSub.publish('hue.global.error', { message: responseBody.message });
      }
    } finally {
      setInstallingAppId(null);
    }
  };

  return (
    <div>
      <h3>Install some data examples</h3>
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

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

const saveCollectUsagePreference = async collectUsage => {
  $.post('/about/update_preferences', { collect_usage: collectUsage ? 'on' : null }, data => {
    if (data.status == 0) {
      huePubSub.publish('hue.global.info', { message: 'Configuration updated' });
    } else {
      huePubSub.publish('hue.global.error', { message: data.data });
    }
  });
};

const Analytics = (): JSX.Element => {
  const [collectUsage, setCollectUsage] = useState(false);

  const handleCheckboxChange = async event => {
    const newPreference = event.target.checked;
    setCollectUsage(newPreference);
    await saveCollectUsagePreference(newPreference);
  };

  return (
    <div>
      <h3>Anonymous usage analytics</h3>
      <label className="checkbox">
        <input
          type="checkbox"
          name="collect_usage"
          title="Check to enable usage analytics"
          checked={collectUsage}
          onChange={handleCheckboxChange}
        />
        Help improve Hue with anonymous usage analytics.
      </label>
    </div>
  );
};

export default Analytics;
